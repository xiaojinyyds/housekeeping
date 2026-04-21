#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""管理员API"""
import secrets

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, cast, String as SAString
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id, get_current_user_role
from app.models.business import CustomerLead, ServiceContract
from app.models.user import User
from app.models.worker import WorkerProfile, WorkerApplication, WorkerExperience
from app.schemas.response import ApiResponse
from app.utils.helpers import generate_uuid

router = APIRouter()


WORKER_DEFAULT_PASSWORD_LENGTH = 12


def normalize_list_field(value, field_name: str):
    if value is None:
        return None
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{field_name} 格式不正确"
    )


def build_worker_login_email(id_card: str, phone: Optional[str] = None):
    base = (id_card or phone or secrets.token_hex(6)).strip()
    return f"{base}@worker.local"


def build_worker_login_password():
    return secrets.token_urlsafe(WORKER_DEFAULT_PASSWORD_LENGTH)


def normalize_experience_items(items):
    if items is None:
        return []
    if not isinstance(items, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_experiences 格式不正确"
        )

    normalized = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="work_experiences 格式不正确"
            )
        job_content = (item.get("job_content") or "").strip()
        if not job_content:
            continue
        normalized.append({
            "start_date": item.get("start_date") or None,
            "end_date": item.get("end_date") or None,
            "company_name": (item.get("company_name") or "").strip() or None,
            "job_content": job_content,
            "sort_order": item.get("sort_order", index)
        })
    return normalized


def replace_worker_experiences(db: Session, worker_profile_id: str, items):
    normalized_items = normalize_experience_items(items)
    db.query(WorkerExperience).filter(
        WorkerExperience.worker_profile_id == worker_profile_id
    ).delete()

    for item in normalized_items:
        db.add(WorkerExperience(
            id=generate_uuid(),
            worker_profile_id=worker_profile_id,
            start_date=item["start_date"],
            end_date=item["end_date"],
            company_name=item["company_name"],
            job_content=item["job_content"],
            sort_order=item["sort_order"]
        ))


@router.get("/users", summary="获取用户列表（管理员）")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    role: Optional[str] = Query(None, description="角色筛选: user/worker/admin"),
    status: Optional[str] = Query(None, description="状态筛选: active/disabled"),
    keyword: Optional[str] = Query(None, description="搜索关键词（邮箱/手机/昵称）"),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（管理员专用）
    
    支持筛选：
    - role: 角色
    - status: 状态
    - keyword: 搜索关键词
    """
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问"
        )
    
    # 构建查询
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if status:
        query = query.filter(User.status == status)
    
    if keyword:
        query = query.filter(
            (User.email.like(f"%{keyword}%")) |
            (User.id_card.like(f"%{keyword}%")) |
            (User.phone.like(f"%{keyword}%")) |
            (User.nickname.like(f"%{keyword}%"))
        )
    
    # 总数
    total = query.count()
    
    # 分页
    users = query.order_by(
        User.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return ApiResponse.success(
        data={
            "list": [user.to_dict() for user in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        },
        message="获取成功"
    )


@router.get("/users/{user_id}", summary="获取用户详情（管理员）")
async def get_user_detail(
    user_id: str,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """获取用户详细信息（管理员专用）"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return ApiResponse.success(
        data=user.to_dict(),
        message="获取成功"
    )


@router.put("/users/{user_id}/status", summary="修改用户状态（管理员）")
async def update_user_status(
    user_id: str,
    new_status: str = Query(..., description="新状态: active/disabled"),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """修改用户状态（管理员专用）"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    if new_status not in ['active', 'disabled']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="状态值无效"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        user.status = new_status
        db.commit()
        db.refresh(user)
        
        return ApiResponse.success(
            data=user.to_dict(),
            message=f"用户已{'启用' if new_status == 'active' else '禁用'}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )


@router.get("/workers/list", summary="获取阿姨列表/管理端")
async def get_workers_admin(
    page: int = Query(1, ge=1, description="??"),
    page_size: int = Query(10, ge=1, le=100, description="????"),
    is_available: Optional[bool] = Query(None, description="?????"),
    keyword: Optional[str] = Query(None, description="??????/???/????"),
    address: Optional[str] = Query(None, description="????"),
    service_area: Optional[str] = Query(None, description="????"),
    job_type: Optional[str] = Query(None, description="????"),
    current_status: Optional[str] = Query(None, description="????"),
    min_age: Optional[int] = Query(None, ge=0, description="????"),
    max_age: Optional[int] = Query(None, ge=0, description="????"),
    user_role: str = Depends(get_current_user_role),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )

    query = db.query(WorkerProfile)

    # 员工只能看自己录入的阿姨
    if user_role == "staff":
        query = query.filter(WorkerProfile.recorder_staff_id == current_user_id)

    if is_available is not None:
        query = query.filter(WorkerProfile.is_available == is_available)

    if keyword:
        query = query.filter(
            or_(
                WorkerProfile.real_name.like(f"%{keyword}%"),
                WorkerProfile.phone.like(f"%{keyword}%"),
                WorkerProfile.id_card.like(f"%{keyword}%")
            )
        )

    if address:
        query = query.filter(WorkerProfile.address.like(f"%{address}%"))

    if service_area:
        query = query.filter(cast(WorkerProfile.service_areas, SAString).like(f"%{service_area}%"))

    if job_type:
        query = query.filter(cast(WorkerProfile.job_types, SAString).like(f"%{job_type}%"))

    if current_status:
        query = query.filter(WorkerProfile.current_status == current_status)

    if min_age is not None:
        query = query.filter(WorkerProfile.age >= min_age)

    if max_age is not None:
        query = query.filter(WorkerProfile.age <= max_age)

    total = query.count()
    workers = query.order_by(
        WorkerProfile.created_at.desc(),
        WorkerProfile.rating.desc(),
        WorkerProfile.completed_orders.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return ApiResponse.success(
        data={
            "list": [worker.to_dict() for worker in workers],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        },
        message="获取成功"
    )


@router.put("/workers/{worker_id}/available", summary="修改阿姨接单状态（管理员）")
async def update_worker_available(
    worker_id: str,
    is_available: bool = Query(..., description="是否接单"),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """修改阿姨接单状态（管理员专用）"""
    # 检查权限
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    worker = db.query(WorkerProfile).filter(WorkerProfile.id == worker_id).first()
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="阿姨不存在"
        )
    
    try:
        worker.is_available = is_available
        db.commit()
        db.refresh(worker)
        
        return ApiResponse.success(
            data=worker.to_dict(),
            message=f"已{'上架' if is_available else '下架'}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )


@router.put("/workers/{worker_id}/recommend", summary="设置阿姨首页推荐（管理员）")
async def update_worker_recommend(
    worker_id: str,
    is_recommended: bool = Query(..., description="是否首页推荐"),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    设置阿姨是否首页推荐（管理员专用）
    
    功能：
    - 管理员可以设置优秀阿姨在首页展示
    - 首页推荐的阿姨会优先展示给用户
    """
    # 检查权限
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    worker = db.query(WorkerProfile).filter(WorkerProfile.id == worker_id).first()
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="阿姨不存在"
        )
    
    try:
        worker.is_recommended = is_recommended
        db.commit()
        db.refresh(worker)
        
        return ApiResponse.success(
            data=worker.to_dict(),
            message=f"已{'设为' if is_recommended else '取消'}首页推荐"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )


@router.get("/statistics", summary="获取统计数据")
async def get_statistics(
    user_role: str = Depends(get_current_user_role),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )

    try:
        now = datetime.now()
        today = now.date()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        seven_days = [(today - timedelta(days=offset)) for offset in range(6, -1, -1)]
        seven_day_labels = [item.strftime("%m-%d") for item in seven_days]

        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar() or 0
        today_users = db.query(func.count(User.id)).filter(func.date(User.created_at) == today).scalar() or 0
        month_users = db.query(func.count(User.id)).filter(User.created_at >= month_start).scalar() or 0

        role_distribution = {}
        for role in ["user", "staff", "worker", "admin"]:
            role_distribution[role] = db.query(func.count(User.id)).filter(User.role == role).scalar() or 0

        total_workers = db.query(func.count(WorkerProfile.id)).scalar() or 0
        available_workers = db.query(func.count(WorkerProfile.id)).filter(WorkerProfile.is_available == True).scalar() or 0
        today_workers = db.query(func.count(WorkerProfile.id)).filter(func.date(WorkerProfile.created_at) == today).scalar() or 0
        avg_rating = db.query(func.avg(WorkerProfile.rating)).scalar() or 0

        pending_applications = db.query(func.count(WorkerApplication.id)).filter(WorkerApplication.status == "pending").scalar() or 0
        approved_applications = db.query(func.count(WorkerApplication.id)).filter(WorkerApplication.status == "approved").scalar() or 0
        rejected_applications = db.query(func.count(WorkerApplication.id)).filter(WorkerApplication.status == "rejected").scalar() or 0
        today_applications = (
            db.query(func.count(WorkerApplication.id))
            .filter(func.date(WorkerApplication.created_at) == today)
            .scalar()
            or 0
        )

        contract_base_query = db.query(ServiceContract)
        lead_base_query = db.query(CustomerLead)
        worker_add_base_query = db.query(WorkerProfile)

        if user_role == "staff":
            contract_base_query = contract_base_query.filter(ServiceContract.broker_staff_id == current_user_id)
            lead_base_query = lead_base_query.filter(CustomerLead.owner_staff_id == current_user_id)
            worker_add_base_query = worker_add_base_query.filter(WorkerProfile.recorder_staff_id == current_user_id)

        month_contract_query = contract_base_query.filter(ServiceContract.contract_date >= month_start.date())
        month_lead_query = lead_base_query.filter(CustomerLead.lead_date >= month_start.date())
        month_worker_query = worker_add_base_query.filter(WorkerProfile.created_at >= month_start)

        month_contract_amount = month_contract_query.with_entities(
            func.coalesce(func.sum(ServiceContract.contract_amount), 0)
        ).scalar() or 0
        month_contract_count = month_contract_query.with_entities(func.count(ServiceContract.id)).scalar() or 0
        month_lead_count = month_lead_query.with_entities(func.count(CustomerLead.id)).scalar() or 0
        month_worker_add_count = month_worker_query.with_entities(func.count(WorkerProfile.id)).scalar() or 0

        daily_contract_rows = (
            contract_base_query.filter(ServiceContract.contract_date >= seven_days[0])
            .with_entities(
                ServiceContract.contract_date.label("day"),
                func.coalesce(func.sum(ServiceContract.contract_amount), 0).label("amount"),
                func.count(ServiceContract.id).label("count")
            )
            .group_by(ServiceContract.contract_date)
            .all()
        )
        daily_contract_map = {
            row.day.isoformat() if row.day else "": {
                "amount": float(row.amount or 0),
                "count": int(row.count or 0)
            }
            for row in daily_contract_rows
        }

        daily_lead_rows = (
            lead_base_query.filter(CustomerLead.lead_date >= seven_days[0])
            .with_entities(
                CustomerLead.lead_date.label("day"),
                func.count(CustomerLead.id).label("count")
            )
            .group_by(CustomerLead.lead_date)
            .all()
        )
        daily_lead_map = {
            row.day.isoformat() if row.day else "": int(row.count or 0)
            for row in daily_lead_rows
        }

        daily_worker_rows = (
            worker_add_base_query.filter(WorkerProfile.created_at >= seven_days[0])
            .with_entities(
                func.date(WorkerProfile.created_at).label("day"),
                func.count(WorkerProfile.id).label("count")
            )
            .group_by(func.date(WorkerProfile.created_at))
            .all()
        )
        daily_worker_map = {str(row.day): int(row.count or 0) for row in daily_worker_rows}

        daily_metrics = []
        for item in seven_days:
            key = item.isoformat()
            contract_item = daily_contract_map.get(key, {"amount": 0, "count": 0})
            daily_metrics.append({
                "date": key,
                "label": item.strftime("%m-%d"),
                "contract_amount": contract_item["amount"],
                "contract_count": contract_item["count"],
                "lead_count": daily_lead_map.get(key, 0),
                "worker_add_count": daily_worker_map.get(key, 0)
            })

        staff_ranking = []
        if user_role == "admin":
            staff_rows = (
                db.query(
                    ServiceContract.broker_staff_id.label("staff_id"),
                    func.count(ServiceContract.id).label("contract_count"),
                    func.coalesce(func.sum(ServiceContract.contract_amount), 0).label("contract_amount")
                )
                .filter(
                    ServiceContract.contract_date >= month_start.date(),
                    ServiceContract.broker_staff_id.isnot(None)
                )
                .group_by(ServiceContract.broker_staff_id)
                .order_by(
                    func.coalesce(func.sum(ServiceContract.contract_amount), 0).desc(),
                    func.count(ServiceContract.id).desc()
                )
                .all()
            )
            staff_ids = [row.staff_id for row in staff_rows if row.staff_id]
            staff_map = {}
            if staff_ids:
                staffs = db.query(User).filter(User.id.in_(staff_ids)).all()
                staff_map = {item.id: item for item in staffs}

            lead_rows = (
                db.query(
                    CustomerLead.owner_staff_id.label("staff_id"),
                    func.count(CustomerLead.id).label("lead_count")
                )
                .filter(
                    CustomerLead.lead_date >= month_start.date(),
                    CustomerLead.owner_staff_id.isnot(None)
                )
                .group_by(CustomerLead.owner_staff_id)
                .all()
            )
            lead_map = {row.staff_id: int(row.lead_count or 0) for row in lead_rows}

            worker_rows = (
                db.query(
                    WorkerProfile.recorder_staff_id.label("staff_id"),
                    func.count(WorkerProfile.id).label("worker_add_count")
                )
                .filter(
                    WorkerProfile.created_at >= month_start,
                    WorkerProfile.recorder_staff_id.isnot(None)
                )
                .group_by(WorkerProfile.recorder_staff_id)
                .all()
            )
            worker_map = {row.staff_id: int(row.worker_add_count or 0) for row in worker_rows}

            for index, row in enumerate(staff_rows, start=1):
                staff_user = staff_map.get(row.staff_id)
                staff_ranking.append({
                    "rank": index,
                    "staff_id": row.staff_id,
                    "staff_name": (
                        staff_user.real_name or staff_user.nickname or staff_user.email
                        if staff_user else row.staff_id
                    ),
                    "contract_amount": float(row.contract_amount or 0),
                    "contract_count": int(row.contract_count or 0),
                    "lead_count": lead_map.get(row.staff_id, 0),
                    "worker_add_count": worker_map.get(row.staff_id, 0)
                })

        return ApiResponse.success(
            data={
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "today": today_users,
                    "month": month_users,
                    "role_distribution": role_distribution
                },
                "workers": {
                    "total": total_workers,
                    "available": available_workers,
                    "today": today_workers,
                    "avg_rating": round(float(avg_rating), 2)
                },
                "applications": {
                    "pending": pending_applications,
                    "approved": approved_applications,
                    "rejected": rejected_applications,
                    "today": today_applications,
                    "total": pending_applications + approved_applications + rejected_applications
                },
                "dashboard": {
                    "scope": "all" if user_role == "admin" else "self",
                    "month": month_start.strftime("%Y-%m"),
                    "month_contract_amount": round(float(month_contract_amount), 2),
                    "month_contract_count": int(month_contract_count),
                    "month_lead_count": int(month_lead_count),
                    "month_worker_add_count": int(month_worker_add_count),
                    "daily_metrics": daily_metrics,
                    "daily_labels": seven_day_labels,
                    "staff_ranking": staff_ranking
                }
            },
            message="获取成功"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )


@router.post("/users/create", summary="创建用户（管理员）")
async def create_user(
    request: dict,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    创建用户（管理员专用）
    
    参数：
    - email: 邮箱
    - password: 密码
    - nickname: 昵称（可选）
    - phone: 手机号（可选）
    - role: 角色（user/worker/admin，默认user）
    """
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    email = (request.get("email") or "").strip()
    id_card = (request.get("id_card") or "").strip()
    password = request.get("password")
    
    if not id_card or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱和密码不能为空"
        )
    
    # 检查邮箱是否已存在
    login_email = email or f"{id_card}@staff.local"

    existing_id_card = db.query(User).filter(User.id_card == id_card).first()
    if existing_id_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该身份证号已被注册"
        )

    existing_user = db.query(User).filter(User.email == login_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 检查手机号是否已存在
    phone = request.get("phone")
    if phone:
        existing_phone = db.query(User).filter(User.phone == phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被注册"
            )
    
    try:
        from app.core.security import get_password_hash
        from app.utils.helpers import generate_uuid
        
        # 创建用户
        new_user = User(
            id=generate_uuid(),
            email=login_email,
            id_card=id_card,
            password_hash=get_password_hash(password),
            nickname=request.get("nickname") or request.get("real_name"),
            real_name=request.get("real_name"),
            phone=phone,
            avatar_url=request.get("avatar_url"),
            role=request.get("role", "user") if request.get("role", "user") in ["user", "staff", "worker", "admin"] else "user",
            status="active"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return ApiResponse.success(
            data=new_user.to_dict(),
            message="用户创建成功"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建失败: {str(e)}"
        )


@router.put("/users/{user_id}/info", summary="修改用户信息（管理员）")
async def update_user_info(
    user_id: str,
    request: dict,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    修改用户信息（管理员专用）
    
    可修改：
    - nickname: 昵称
    - phone: 手机号
    - avatar_url: 头像
    - role: 角色
    """
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        # 更新字段
        if "nickname" in request:
            user.nickname = request["nickname"]
        
        if "phone" in request:
            # 检查手机号是否已被其他用户使用
            if request["phone"]:
                existing = db.query(User).filter(
                    User.phone == request["phone"],
                    User.id != user_id
                ).first()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="该手机号已被使用"
                    )
            user.phone = request["phone"]
        
        if "avatar_url" in request:
            user.avatar_url = request["avatar_url"]
        
        if "role" in request:
            if request["role"] not in ["user", "staff", "worker", "admin"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色值无效"
                )
            user.role = request["role"]
        
        db.commit()
        db.refresh(user)
        
        return ApiResponse.success(
            data=user.to_dict(),
            message="更新成功"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}"
        )


@router.post("/users/{user_id}/reset-password", summary="重置用户密码（管理员）")
async def admin_reset_password(
    user_id: str,
    request: dict,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    管理员重置用户密码（无需验证码）
    
    参数：
    - new_password: 新密码
    """
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    new_password = request.get("new_password")
    
    if not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能为空"
        )
    
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度不能少于6位"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        from app.core.security import get_password_hash
        
        user.password_hash = get_password_hash(new_password)
        db.commit()
        
        return ApiResponse.success(message="密码重置成功")
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重置失败: {str(e)}"
        )


@router.delete("/users/{user_id}", summary="删除用户（管理员）")
async def delete_user(
    user_id: str,
    user_role: str = Depends(get_current_user_role),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除用户（管理员专用）"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    # 不能删除自己
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        # 先删除关联的阿姨档案
        db.query(WorkerProfile).filter(WorkerProfile.user_id == user_id).delete()
        
        # 删除关联的阿姨申请
        db.query(WorkerApplication).filter(WorkerApplication.user_id == user_id).delete()
        
        # 删除关联的阿姨时间段设置
        from app.models.worker import WorkerTimeSlot, WorkerService
        db.query(WorkerTimeSlot).filter(WorkerTimeSlot.worker_id == user_id).delete()
        db.query(WorkerService).filter(WorkerService.worker_id == user_id).delete()
        
        # 最后删除用户
        db.delete(user)
        db.commit()
        
        return ApiResponse.success(message="用户已删除")
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )


@router.post("/workers/create", summary="创建阿姨档案/管理端")
async def create_worker(
    request: dict,
    user_role: str = Depends(get_current_user_role),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )

    experience_years = request.get("experience_years", request.get("work_years"))
    id_card_front = request.get("id_card_front", request.get("id_card_front_url"))
    id_card_back = request.get("id_card_back", request.get("id_card_back_url"))
    health_certificate = request.get("health_certificate", request.get("health_certificate_url"))

    normalized_request = {
        **request,
        "experience_years": experience_years,
        "id_card_front": id_card_front,
        "id_card_back": id_card_back,
        "health_certificate": health_certificate
    }

    required_fields = [
        "real_name", "phone", "id_card", "gender", "age", "address",
        "skills", "introduction", "id_card_front", "id_card_back"
    ]
    for field in required_fields:
        if normalized_request.get(field) in [None, "", []]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"缺少必要字段: {field}"
            )

    if normalized_request.get("experience_years") in [None, ""]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少从业年限"
        )

    existing_phone = db.query(User).filter(User.phone == normalized_request["phone"]).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已被注册"
        )

    existing_id_card = db.query(WorkerProfile).filter(WorkerProfile.id_card == normalized_request["id_card"]).first()
    if existing_id_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该身份证号已被注册"
        )

    existing_user_id_card = db.query(User).filter(User.id_card == normalized_request["id_card"]).first()
    if existing_user_id_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该身份证号已被使用"
        )

    try:
        from app.core.security import get_password_hash

        skills = normalize_list_field(normalized_request.get("skills"), "skills") or []
        service_areas = normalize_list_field(normalized_request.get("service_areas"), "service_areas") or []
        job_types = normalize_list_field(normalized_request.get("job_types"), "job_types") or []
        other_certificates = normalize_list_field(normalized_request.get("other_certificates"), "other_certificates") or []
        recommended_reasons = normalize_list_field(normalized_request.get("recommended_reasons"), "recommended_reasons") or []
        work_experiences = normalized_request.get("work_experiences")

        login_email = build_worker_login_email(normalized_request["id_card"], normalized_request.get("phone"))
        while db.query(User).filter(User.email == login_email).first():
            login_email = build_worker_login_email(
                f"{normalized_request['id_card']}_{generate_uuid()[:6]}",
                normalized_request.get("phone")
            )

        login_password = build_worker_login_password()

        user = User(
            id=generate_uuid(),
            email=login_email,
            id_card=normalized_request["id_card"],
            password_hash=get_password_hash(login_password),
            nickname=normalized_request["real_name"],
            real_name=normalized_request["real_name"],
            phone=normalized_request["phone"],
            avatar_url=normalized_request.get("avatar_url"),
            role="worker",
            status="active"
        )
        db.add(user)
        db.flush()

        worker_profile = WorkerProfile(
            id=generate_uuid(),
            user_id=user.id,
            recorder_staff_id=current_user_id,
            real_name=normalized_request["real_name"],
            phone=normalized_request["phone"],
            id_card=normalized_request["id_card"],
            gender=normalized_request["gender"],
            age=int(normalized_request["age"]),
            wechat=normalized_request.get("wechat"),
            emergency_contact=normalized_request.get("emergency_contact"),
            emergency_phone=normalized_request.get("emergency_phone"),
            address=normalized_request["address"],
            experience_years=int(normalized_request["experience_years"]),
            skills=skills,
            job_types=job_types,
            can_drive=bool(normalized_request.get("can_drive", False)),
            introduction=normalized_request["introduction"],
            recommended_reasons=recommended_reasons,
            internal_remark=normalized_request.get("internal_remark"),
            service_areas=service_areas,
            service_area_codes=normalized_request.get("service_area_codes") or [],
            hourly_rate=(normalized_request.get("hourly_rate") or None),
            expected_salary=(normalized_request.get("expected_salary") or None),
            current_status=normalized_request.get("current_status") or "available",
            health_certificate=normalized_request.get("health_certificate"),
            health_report=normalized_request.get("health_report"),
            practice_certificate=normalized_request.get("practice_certificate"),
            other_certificates=other_certificates,
            id_card_front=normalized_request["id_card_front"],
            id_card_back=normalized_request["id_card_back"],
            is_available=bool(normalized_request.get("is_available", True)),
            is_recommended=bool(normalized_request.get("is_recommended", False)),
            rating=5.0,
            total_orders=0,
            completed_orders=0
        )

        db.add(worker_profile)
        db.flush()  # 触发 ID 生成
        replace_worker_experiences(db, worker_profile.id, work_experiences)
        db.commit()
        db.refresh(worker_profile)
        db.refresh(user)

        return ApiResponse.success(
            data={
                "user": user.to_dict(),
                "worker_profile": worker_profile.to_dict(),
                "internal_account": {
                    "email": login_email
                }
            },
            message="阿姨档案创建成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )

@router.put("/workers/{worker_id}", summary="更新阿姨档案/管理端")
async def update_worker(
    worker_id: str,
    request: dict,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )

    worker = db.query(WorkerProfile).filter(WorkerProfile.user_id == worker_id).first()
    user = db.query(User).filter(User.id == worker_id).first()

    if not worker or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="阿姨不存在"
        )

    normalized_request = dict(request or {})

    phone = normalized_request.get("phone")
    if phone and phone != worker.phone:
        existing_phone = db.query(User).filter(User.phone == phone, User.id != worker_id).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被使用"
            )

    id_card = normalized_request.get("id_card")
    if id_card and id_card != worker.id_card:
        existing_id_card = db.query(WorkerProfile).filter(
            WorkerProfile.id_card == id_card,
            WorkerProfile.user_id != worker_id
        ).first()
        if existing_id_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该身份证号已被注册"
            )
        existing_user_id_card = db.query(User).filter(User.id_card == id_card, User.id != worker_id).first()
        if existing_user_id_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该身份证号已被使用"
            )

    try:
        if "real_name" in normalized_request:
            worker.real_name = normalized_request["real_name"]
            user.nickname = normalized_request["real_name"]
            user.real_name = normalized_request["real_name"]
        if "phone" in normalized_request:
            worker.phone = normalized_request["phone"]
            user.phone = normalized_request["phone"]
        if "id_card" in normalized_request:
            worker.id_card = normalized_request["id_card"]
            user.id_card = normalized_request["id_card"]
        if "gender" in normalized_request:
            worker.gender = normalized_request["gender"]
        if "age" in normalized_request:
            worker.age = int(normalized_request["age"]) if normalized_request["age"] not in [None, ""] else None
        if "experience_years" in normalized_request:
            worker.experience_years = int(normalized_request["experience_years"]) if normalized_request["experience_years"] not in [None, ""] else None
        if "wechat" in normalized_request:
            worker.wechat = normalized_request["wechat"]
        if "emergency_contact" in normalized_request:
            worker.emergency_contact = normalized_request["emergency_contact"]
        if "emergency_phone" in normalized_request:
            worker.emergency_phone = normalized_request["emergency_phone"]
        if "address" in normalized_request:
            worker.address = normalized_request["address"]
        if "introduction" in normalized_request:
            worker.introduction = normalized_request["introduction"]
        if "internal_remark" in normalized_request:
            worker.internal_remark = normalized_request["internal_remark"]
        if "hourly_rate" in normalized_request:
            worker.hourly_rate = normalized_request["hourly_rate"] if normalized_request["hourly_rate"] not in [""] else None
        if "expected_salary" in normalized_request:
            worker.expected_salary = normalized_request["expected_salary"] if normalized_request["expected_salary"] not in [""] else None
        if "skills" in normalized_request:
            worker.skills = normalize_list_field(normalized_request.get("skills"), "skills") or []
        if "job_types" in normalized_request:
            worker.job_types = normalize_list_field(normalized_request.get("job_types"), "job_types") or []
        if "service_areas" in normalized_request:
            worker.service_areas = normalize_list_field(normalized_request.get("service_areas"), "service_areas") or []
        if "service_area_codes" in normalized_request:
            worker.service_area_codes = normalized_request.get("service_area_codes") or []
        if "recommended_reasons" in normalized_request:
            worker.recommended_reasons = normalize_list_field(
                normalized_request.get("recommended_reasons"),
                "recommended_reasons"
            ) or []
        if "other_certificates" in normalized_request:
            worker.other_certificates = normalize_list_field(normalized_request.get("other_certificates"), "other_certificates") or []
        if "current_status" in normalized_request:
            worker.current_status = normalized_request["current_status"] or worker.current_status
        if "can_drive" in normalized_request:
            worker.can_drive = bool(normalized_request["can_drive"])
        if "id_card_front" in normalized_request:
            worker.id_card_front = normalized_request["id_card_front"]
        if "id_card_back" in normalized_request:
            worker.id_card_back = normalized_request["id_card_back"]
        if "health_certificate" in normalized_request:
            worker.health_certificate = normalized_request["health_certificate"]
        if "health_report" in normalized_request:
            worker.health_report = normalized_request["health_report"]
        if "practice_certificate" in normalized_request:
            worker.practice_certificate = normalized_request["practice_certificate"]
        if "is_available" in normalized_request:
            worker.is_available = bool(normalized_request["is_available"])
        if "is_recommended" in normalized_request:
            worker.is_recommended = bool(normalized_request["is_recommended"])
        if "avatar_url" in normalized_request:
            user.avatar_url = normalized_request["avatar_url"]
        if "work_experiences" in normalized_request:
            replace_worker_experiences(db, worker.id, normalized_request.get("work_experiences"))

        db.commit()
        db.refresh(worker)
        db.refresh(user)

        worker_dict = worker.to_dict()
        worker_dict["avatar_url"] = user.avatar_url

        return ApiResponse.success(
            data=worker_dict,
            message="阿姨档案更新成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )


@router.delete("/workers/{worker_id}", summary="删除阿姨档案")
async def delete_worker(
    worker_id: str,
    user_role: str = Depends(get_current_user_role),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除阿姨档案（管理员/员工可删除自己录入的）"""
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )

    worker = db.query(WorkerProfile).filter(WorkerProfile.id == worker_id).first()
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="阿姨档案不存在"
        )

    # 员工只能删除自己录入的阿姨
    if user_role == "staff" and worker.recorder_staff_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己录入的阿姨档案"
        )

    try:
        user_id = worker.user_id

        if user_id:
            # 清理访客留资中的阿姨引用
            from app.models.appointment import GuestLead
            db.query(GuestLead).filter(GuestLead.worker_id == user_id).update({"worker_id": None})

            # 清理阿姨时间段和服务设置
            from app.models.worker import WorkerTimeSlot, WorkerService
            db.query(WorkerTimeSlot).filter(WorkerTimeSlot.worker_id == user_id).delete()
            db.query(WorkerService).filter(WorkerService.worker_id == user_id).delete()

        # 删除阿姨档案
        db.delete(worker)

        db.commit()
        return ApiResponse.success(message="阿姨档案已删除")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )


@router.delete("/staffs/{staff_id}", summary="删除员工账号")
async def delete_staff(
    staff_id: str,
    user_role: str = Depends(get_current_user_role),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除员工账号（仅管理员）"""
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )

    if staff_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )

    user = db.query(User).filter(User.id == staff_id, User.role == "staff").first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )

    try:
        # 删除员工
        db.delete(user)
        db.commit()
        return ApiResponse.success(message="员工账号已删除")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )
