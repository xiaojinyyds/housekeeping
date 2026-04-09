#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""合同管理 API"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id, get_current_user_role
from app.models.business import ContractFollowup, CustomerLead, ServiceContract
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


def parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def parse_date(value) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


def user_display_name(user: Optional[User]) -> str:
    if not user:
        return ""
    return user.nickname or getattr(user, "real_name", None) or user.email or user.phone or ""


def ensure_contract_access(contract: ServiceContract, user_role: str, current_user_id: str):
    if user_role == "staff" and contract.broker_staff_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该合同")


def build_contract_detail(db: Session, contract: ServiceContract):
    contract_dict = contract.to_dict()

    user_ids = [item for item in [contract.worker_user_id, contract.broker_staff_id, contract.customer_user_id] if item]
    users = {}
    if user_ids:
        users = {item.id: item for item in db.query(User).filter(User.id.in_(user_ids)).all()}

    lead = db.query(CustomerLead).filter(CustomerLead.id == contract.lead_id).first() if contract.lead_id else None

    contract_dict["worker_name"] = user_display_name(users.get(contract.worker_user_id))
    contract_dict["broker_staff_name"] = user_display_name(users.get(contract.broker_staff_id))
    contract_dict["customer_user_name"] = user_display_name(users.get(contract.customer_user_id))
    contract_dict["lead_no"] = lead.lead_no if lead else ""
    contract_dict["lead_customer_name"] = lead.customer_name if lead else ""
    return contract_dict


@router.get("/list", summary="获取合同列表")
async def get_contract_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status_filter: Optional[str] = Query(None, alias="status", description="合同状态"),
    service_type: Optional[str] = Query(None, description="订单类型"),
    keyword: Optional[str] = Query(None, description="关键词"),
    broker_staff_id: Optional[str] = Query(None, description="签单员工ID"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    query = db.query(ServiceContract)

    if user_role == "staff":
        query = query.filter(ServiceContract.broker_staff_id == user_id)
    elif broker_staff_id:
        query = query.filter(ServiceContract.broker_staff_id == broker_staff_id)

    if status_filter:
        query = query.filter(ServiceContract.status == status_filter)
    if service_type:
        query = query.filter(ServiceContract.service_type == service_type)

    start = parse_date(start_date)
    end = parse_date(end_date)
    if start:
        query = query.filter(ServiceContract.contract_date >= start)
    if end:
        query = query.filter(ServiceContract.contract_date <= end)

    if keyword:
        query = query.filter(
            (ServiceContract.contract_no.like(f"%{keyword}%")) |
            (ServiceContract.customer_name.like(f"%{keyword}%")) |
            (ServiceContract.customer_phone.like(f"%{keyword}%")) |
            (ServiceContract.service_address.like(f"%{keyword}%"))
        )

    total = query.count()
    total_contract_amount = query.with_entities(func.coalesce(func.sum(ServiceContract.contract_amount), 0)).scalar() or 0
    rows = query.order_by(ServiceContract.contract_date.desc(), ServiceContract.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    user_ids = []
    for row in rows:
        if row.worker_user_id:
            user_ids.append(row.worker_user_id)
        if row.broker_staff_id:
            user_ids.append(row.broker_staff_id)
    users = {}
    if user_ids:
        users = {item.id: item for item in db.query(User).filter(User.id.in_(user_ids)).all()}

    data_list = []
    for row in rows:
        item = row.to_dict()
        item["worker_name"] = user_display_name(users.get(row.worker_user_id))
        item["broker_staff_name"] = user_display_name(users.get(row.broker_staff_id))
        data_list.append(item)

    return ApiResponse.success(
        data={
            "list": data_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "stats": {
                "contract_count": int(total),
                "total_contract_amount": float(total_contract_amount)
            }
        },
        message="获取成功"
    )


@router.post("/create", summary="创建合同")
async def create_contract(
    request: dict,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    required_fields = ["lead_id", "worker_user_id", "customer_name", "customer_phone", "service_address", "service_type", "contract_date"]
    for field in required_fields:
        if not request.get(field):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field}不能为空")

    worker = db.query(User).filter(User.id == request["worker_user_id"], User.role == "worker").first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="阿姨账号不存在")

    lead = db.query(CustomerLead).filter(CustomerLead.id == request["lead_id"]).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="关联线索不存在")
    if user_role == "staff" and lead.owner_staff_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能关联自己的线索")

    contract_date = parse_date(request.get("contract_date"))
    if not contract_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="contract_date格式错误，应为YYYY-MM-DD")

    contract = ServiceContract(
        id=generate_uuid(),
        contract_no=request.get("contract_no") or f"HT{datetime.now().strftime('%Y%m%d%H%M%S')}",
        lead_id=request["lead_id"],
        customer_user_id=request.get("customer_user_id"),
        worker_user_id=request["worker_user_id"],
        broker_staff_id=user_id,
        customer_name=request["customer_name"],
        customer_phone=request["customer_phone"],
        customer_source=request.get("customer_source"),
        service_address=request["service_address"],
        service_type=request["service_type"],
        demand_detail=request.get("demand_detail"),
        contract_date=contract_date,
        sign_date=parse_datetime(request.get("sign_date")),
        start_date=parse_datetime(request.get("start_date")),
        end_date=parse_datetime(request.get("end_date")),
        actual_end_date=parse_datetime(request.get("actual_end_date")),
        status=request.get("status") or "pending_start",
        replace_status=request.get("replace_status"),
        contract_amount=request.get("contract_amount"),
        discount_rate=request.get("discount_rate"),
        actual_received=request.get("actual_received"),
        worker_salary_desc=request.get("worker_salary_desc"),
        worker_salary_amount=request.get("worker_salary_amount"),
        service_fee=request.get("service_fee"),
        referral_fee=request.get("referral_fee"),
        refund_amount=request.get("refund_amount"),
        refund_reason=request.get("refund_reason"),
        remark=request.get("remark")
    )

    db.add(contract)
    lead.status = "signed"
    lead.latest_follow_up_at = datetime.now()
    db.commit()
    db.refresh(contract)

    return ApiResponse.success(data=build_contract_detail(db, contract), message="合同创建成功")


@router.get("/staff-summary", summary="管理员查看按员工合同汇总")
async def get_contract_staff_summary(
    status_filter: Optional[str] = Query(None, alias="status", description="合同状态"),
    service_type: Optional[str] = Query(None, description="订单类型"),
    broker_staff_id: Optional[str] = Query(None, description="签单员工ID"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问")

    query = db.query(ServiceContract).filter(ServiceContract.broker_staff_id.isnot(None))
    if status_filter:
        query = query.filter(ServiceContract.status == status_filter)
    if service_type:
        query = query.filter(ServiceContract.service_type == service_type)
    if broker_staff_id:
        query = query.filter(ServiceContract.broker_staff_id == broker_staff_id)

    start = parse_date(start_date)
    end = parse_date(end_date)
    if start:
        query = query.filter(ServiceContract.contract_date >= start)
    if end:
        query = query.filter(ServiceContract.contract_date <= end)

    rows = query.with_entities(
        ServiceContract.broker_staff_id.label("staff_id"),
        func.count(ServiceContract.id).label("contract_count"),
        func.coalesce(func.sum(ServiceContract.contract_amount), 0).label("total_contract_amount"),
    ).group_by(ServiceContract.broker_staff_id).all()

    staff_ids = [item.staff_id for item in rows if item.staff_id]
    users = {}
    if staff_ids:
        users = {item.id: item for item in db.query(User).filter(User.id.in_(staff_ids)).all()}

    summary_list = []
    total_count = 0
    total_amount = 0.0
    for item in rows:
        count = int(item.contract_count or 0)
        amount = float(item.total_contract_amount or 0)
        total_count += count
        total_amount += amount
        user = users.get(item.staff_id)
        summary_list.append({
            "staff_id": item.staff_id,
            "staff_name": user_display_name(user),
            "contract_count": count,
            "total_contract_amount": amount,
            "avg_contract_amount": round(amount / count, 2) if count else 0
        })

    summary_list.sort(key=lambda x: (x["total_contract_amount"], x["contract_count"]), reverse=True)
    for idx, item in enumerate(summary_list, start=1):
        item["rank"] = idx

    return ApiResponse.success(
        data={
            "list": summary_list,
            "total_contract_count": total_count,
            "total_contract_amount": round(total_amount, 2)
        },
        message="获取成功"
    )


@router.get("/{contract_id}", summary="获取合同详情")
async def get_contract_detail(
    contract_id: str,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    contract = db.query(ServiceContract).filter(ServiceContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="合同不存在")
    ensure_contract_access(contract, user_role, user_id)

    return ApiResponse.success(data=build_contract_detail(db, contract), message="获取成功")


@router.get("/{contract_id}/followups", summary="获取合同回访记录")
async def get_contract_followups(
    contract_id: str,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    contract = db.query(ServiceContract).filter(ServiceContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="合同不存在")
    ensure_contract_access(contract, user_role, user_id)

    rows = db.query(ContractFollowup).filter(ContractFollowup.contract_id == contract_id).order_by(
        ContractFollowup.created_at.desc()
    ).all()

    staff_ids = [item.staff_id for item in rows if item.staff_id]
    staffs = {}
    if staff_ids:
        staffs = {item.id: item for item in db.query(User).filter(User.id.in_(staff_ids)).all()}

    data_list = []
    for row in rows:
        item = row.to_dict()
        item["staff_name"] = user_display_name(staffs.get(row.staff_id))
        data_list.append(item)

    return ApiResponse.success(data=data_list, message="获取成功")


@router.post("/{contract_id}/followups", summary="新增合同回访记录")
async def create_contract_followup(
    contract_id: str,
    request: dict,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    ensure_staff_or_admin(user_role)

    contract = db.query(ServiceContract).filter(ServiceContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="合同不存在")
    ensure_contract_access(contract, user_role, user_id)

    if not request.get("content"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="回访内容不能为空")

    followup = ContractFollowup(
        id=generate_uuid(),
        contract_id=contract_id,
        staff_id=user_id,
        follow_type=request.get("follow_type") or "other",
        planned_at=parse_datetime(request.get("planned_at")),
        followed_at=parse_datetime(request.get("followed_at")) or datetime.now(),
        result=request.get("result"),
        content=request.get("content"),
        need_action=bool(request.get("need_action"))
    )

    db.add(followup)
    contract.latest_follow_up_at = followup.followed_at or datetime.now()
    if "status" in request and request.get("status"):
        contract.status = request["status"]
    db.commit()
    db.refresh(followup)

    followup_dict = followup.to_dict()
    staff = db.query(User).filter(User.id == user_id).first()
    followup_dict["staff_name"] = user_display_name(staff)
    return ApiResponse.success(data=followup_dict, message="回访记录创建成功")
