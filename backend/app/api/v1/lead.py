#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""客户线索 API"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id, get_current_user_role
from app.models.business import CustomerLead, LeadFollowRecord
from app.models.user import User
from app.schemas.response import ApiResponse
from app.utils.helpers import generate_uuid

router = APIRouter()


def ensure_staff_or_admin(user_role: str):
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问"
        )


def _parse_date(value: Optional[str], field_name: str) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} 格式错误，应为 YYYY-MM-DD"
        ) from exc


def _parse_datetime(value: Optional[str], field_name: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} 格式错误，应为 ISO 日期时间"
        ) from exc


def _assert_lead_access(lead: CustomerLead, user_id: str, user_role: str):
    """管理员可访问全部；员工仅可访问自己的线索。"""
    if user_role == "admin":
        return
    if lead.owner_staff_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该线索"
        )


@router.get("/list", summary="获取客户线索列表")
async def get_leads(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status_filter: Optional[str] = Query(None, alias="status", description="线索状态"),
    service_type: Optional[str] = Query(None, description="订单类型"),
    lead_category: Optional[str] = Query(None, description="线索类别 A/B"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键词"),
    owner_staff_id: Optional[str] = Query(None, description="跟进员工ID"),
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    query = db.query(CustomerLead)

    if status_filter:
        query = query.filter(CustomerLead.status == status_filter)
    if service_type:
        query = query.filter(CustomerLead.service_type == service_type)
    if lead_category:
        query = query.filter(CustomerLead.lead_category == lead_category)

    start_date_obj = _parse_date(start_date, "start_date")
    end_date_obj = _parse_date(end_date, "end_date")
    if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始日期不能晚于结束日期"
        )
    if start_date_obj:
        query = query.filter(CustomerLead.lead_date >= start_date_obj)
    if end_date_obj:
        query = query.filter(CustomerLead.lead_date <= end_date_obj)

    # 员工只能看自己的线索
    if user_role == "staff":
        query = query.filter(CustomerLead.owner_staff_id == user_id)
    elif owner_staff_id:
        query = query.filter(CustomerLead.owner_staff_id == owner_staff_id)

    if keyword:
        query = query.filter(
            (CustomerLead.customer_name.like(f"%{keyword}%")) |
            (CustomerLead.phone.like(f"%{keyword}%")) |
            (CustomerLead.lead_name.like(f"%{keyword}%")) |
            (CustomerLead.demand_address.like(f"%{keyword}%"))
        )

    total = query.count()
    rows = query.order_by(CustomerLead.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    owner_ids = [row.owner_staff_id for row in rows if row.owner_staff_id]
    owners = {}
    if owner_ids:
        owner_rows = db.query(User).filter(User.id.in_(owner_ids)).all()
        owners = {item.id: item for item in owner_rows}

    data_list = []
    for row in rows:
        item = row.to_dict()
        owner = owners.get(row.owner_staff_id)
        item["owner_staff_name"] = owner.nickname or owner.real_name or owner.email if owner else ""
        data_list.append(item)

    return ApiResponse.success(
        data={
            "list": data_list,
            "total": total,
            "page": page,
            "page_size": page_size
        },
        message="获取成功"
    )


@router.post("/create", summary="新建客户线索")
async def create_lead(
    request: dict,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    customer_name = request.get("customer_name")
    phone = request.get("phone")
    service_type = request.get("service_type")

    if not customer_name or not phone or not service_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="客户姓名、电话、订单类型不能为空"
        )

    lead_date = _parse_date(request.get("lead_date"), "lead_date") or datetime.now().date()
    lead_category = (request.get("lead_category") or "B").strip().upper()
    if lead_category not in ["A", "B"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="线索类别仅支持 A/B"
        )

    owner_staff_id = request.get("owner_staff_id") or user_id
    if user_role == "staff":
        owner_staff_id = user_id

    lead = CustomerLead(
        id=generate_uuid(),
        lead_no=f"LEAD{datetime.now().strftime('%Y%m%d%H%M%S')}",
        owner_staff_id=owner_staff_id,
        source=request.get("source"),
        source_detail=request.get("source_detail"),
        lead_name=request.get("lead_name"),
        lead_type=request.get("lead_type"),
        lead_date=lead_date,
        customer_name=customer_name,
        phone=phone,
        wechat=request.get("wechat"),
        service_type=service_type,
        demand_address=request.get("demand_address"),
        demand_detail=request.get("demand_detail"),
        budget=request.get("budget"),
        lead_category=lead_category,
        status=request.get("status") or "new",
        invalid_reason=request.get("invalid_reason"),
        remark=request.get("remark")
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)
    return ApiResponse.success(data=lead.to_dict(), message="客户线索创建成功")


@router.get("/{lead_id}", summary="获取客户线索详情")
async def get_lead_detail(
    lead_id: str,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    lead = db.query(CustomerLead).filter(CustomerLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户线索不存在")
    _assert_lead_access(lead, user_id, user_role)

    lead_dict = lead.to_dict()
    owner = db.query(User).filter(User.id == lead.owner_staff_id).first() if lead.owner_staff_id else None
    lead_dict["owner_staff_name"] = owner.nickname or owner.real_name or owner.email if owner else ""
    return ApiResponse.success(data=lead_dict, message="获取成功")


@router.put("/{lead_id}", summary="更新客户线索")
async def update_lead(
    lead_id: str,
    request: dict,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    lead = db.query(CustomerLead).filter(CustomerLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户线索不存在")
    _assert_lead_access(lead, user_id, user_role)

    if "lead_category" in request and request.get("lead_category"):
        lead_category = str(request.get("lead_category")).strip().upper()
        if lead_category not in ["A", "B"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="线索类别仅支持 A/B"
            )
        lead.lead_category = lead_category

    if "lead_date" in request:
        lead.lead_date = _parse_date(request.get("lead_date"), "lead_date")

    for field in [
        "owner_staff_id",
        "source",
        "source_detail",
        "lead_name",
        "lead_type",
        "customer_name",
        "phone",
        "wechat",
        "service_type",
        "demand_address",
        "demand_detail",
        "budget",
        "status",
        "invalid_reason",
        "remark"
    ]:
        if field in request:
            if field == "owner_staff_id" and user_role == "staff":
                continue
            setattr(lead, field, request.get(field))

    db.commit()
    db.refresh(lead)

    lead_dict = lead.to_dict()
    owner = db.query(User).filter(User.id == lead.owner_staff_id).first() if lead.owner_staff_id else None
    lead_dict["owner_staff_name"] = owner.nickname or owner.real_name or owner.email if owner else ""
    return ApiResponse.success(data=lead_dict, message="客户线索更新成功")


@router.get("/{lead_id}/follow-records", summary="获取客户线索跟进记录")
async def get_lead_follow_records(
    lead_id: str,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    lead = db.query(CustomerLead).filter(CustomerLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户线索不存在")
    _assert_lead_access(lead, user_id, user_role)

    records = db.query(LeadFollowRecord).filter(LeadFollowRecord.lead_id == lead_id).order_by(
        LeadFollowRecord.created_at.desc()
    ).all()

    staff_ids = [record.staff_id for record in records if record.staff_id]
    staffs = {}
    if staff_ids:
        staff_rows = db.query(User).filter(User.id.in_(staff_ids)).all()
        staffs = {item.id: item for item in staff_rows}

    data_list = []
    for record in records:
        item = record.to_dict()
        staff = staffs.get(record.staff_id)
        item["staff_name"] = staff.nickname or staff.real_name or staff.email if staff else ""
        data_list.append(item)

    return ApiResponse.success(data=data_list, message="获取成功")


@router.post("/{lead_id}/follow-records", summary="新增客户线索跟进记录")
async def create_lead_follow_record(
    lead_id: str,
    request: dict,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    lead = db.query(CustomerLead).filter(CustomerLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户线索不存在")
    _assert_lead_access(lead, user_id, user_role)

    if not request.get("content"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="跟进内容不能为空")

    next_follow_up_at = _parse_datetime(request.get("next_follow_up_at"), "next_follow_up_at")

    record = LeadFollowRecord(
        id=generate_uuid(),
        lead_id=lead_id,
        staff_id=user_id,
        follow_type=request.get("follow_type") or "phone",
        follow_result=request.get("follow_result"),
        content=request.get("content"),
        next_action=request.get("next_action"),
        next_follow_up_at=next_follow_up_at
    )

    db.add(record)
    lead.latest_follow_up_at = datetime.now()
    if next_follow_up_at:
        lead.next_follow_up_at = next_follow_up_at
    if request.get("status"):
        lead.status = request["status"]
    db.commit()
    db.refresh(record)

    record_dict = record.to_dict()
    staff = db.query(User).filter(User.id == user_id).first()
    record_dict["staff_name"] = staff.nickname or staff.real_name or staff.email if staff else ""
    return ApiResponse.success(data=record_dict, message="跟进记录创建成功")
