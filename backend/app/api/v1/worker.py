#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""家政阿姨申请API"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user_id, get_current_user_role
from app.models.user import User
from app.models.worker import (
    WorkerApplication, WorkerProfile, 
    WorkerTimeSlot, WorkerService, TimeSlot, Service, WorkerExperience
)
from app.models.appointment import Review
from sqlalchemy import desc
from app.schemas.worker import (
    WorkerApplicationCreate,
    WorkerApplicationUpdate,
    WorkerApplicationReview,
    WorkerProfileUpdate,
    WorkerScheduleUpdate,
    WorkerServiceCreate,
    WorkerServiceUpdate
)
from app.schemas.response import ApiResponse
from app.utils.helpers import generate_uuid

router = APIRouter()


PUBLIC_STATUS_TEXT = {
    "available": "想接单",
    "paused": "不接单",
    "on_job": "上户中",
    "pending_confirm": "待确认",
    "blacklisted": "不接单",
    "inactive": "不接单"
}


def mask_worker_name(name: str):
    if not name:
        return ""
    return f"{name[:1]}**"


@router.post("/apply", summary="提交家政阿姨申请")
async def create_application(
    application: WorkerApplicationCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提交家政阿姨申请
    
    要求：
    - 用户必须已登录
    - 用户角色必须是普通用户（user）
    - 不能重复申请（已有待审核或已通过的申请）
    """
    # 1. 检查用户角色
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经是家政阿姨或管理员，无需再次申请"
        )
    
    # 2. 检查是否已有申请
    existing_application = db.query(WorkerApplication).filter(
        WorkerApplication.user_id == user_id,
        WorkerApplication.status.in_(['pending', 'approved'])
    ).first()
    
    if existing_application:
        if existing_application.status == 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已有待审核的申请，请耐心等待"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经是家政阿姨"
            )
    
    # 3. 创建申请
    try:
        new_application = WorkerApplication(
            id=generate_uuid(),
            user_id=user_id,
            real_name=application.real_name,
            id_card=application.id_card,
            age=application.age,
            gender=application.gender,
            address=application.address,
            phone=application.phone,
            experience_years=application.experience_years,
            skills=application.skills,
            introduction=application.introduction,
            id_card_front=application.id_card_front,
            id_card_back=application.id_card_back,
            health_certificate=application.health_certificate,
            health_report=application.health_report,
            practice_certificate=application.practice_certificate,
            other_certificates=application.other_certificates,
            status='pending'
        )
        
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        
        return ApiResponse.success(
            data=new_application.to_dict(),
            message="申请提交成功，请等待审核"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"申请提交失败: {str(e)}"
        )


@router.get("/my-application", summary="查看我的申请")
async def get_my_application(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """查看当前用户的家政阿姨申请"""
    application = db.query(WorkerApplication).filter(
        WorkerApplication.user_id == user_id
    ).order_by(WorkerApplication.created_at.desc()).first()
    
    if not application:
        return ApiResponse.success(
            data=None,
            message="暂无申请记录"
        )
    
    return ApiResponse.success(
        data=application.to_dict(),
        message="获取成功"
    )


@router.put("/application/{application_id}", summary="更新申请信息")
async def update_application(
    application_id: str,
    update_data: WorkerApplicationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新申请信息（仅待审核状态可更新）
    """
    # 查找申请
    application = db.query(WorkerApplication).filter(
        WorkerApplication.id == application_id,
        WorkerApplication.user_id == user_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="申请不存在"
        )
    
    # 只有待审核状态可以更新
    if application.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待审核的申请可以修改"
        )
    
    # 更新字段
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(application, key, value)
    
    try:
        db.commit()
        db.refresh(application)
        
        return ApiResponse.success(
            data=application.to_dict(),
            message="更新成功"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}"
        )


@router.get("/applications", summary="获取申请列表（管理员）")
async def get_applications(
    status: Optional[str] = Query(None, description="筛选状态: pending/approved/rejected"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    获取家政阿姨申请列表（管理员专用）
    """
    # 检查权限
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问"
        )
    
    # 构建查询
    query = db.query(WorkerApplication)
    
    if status:
        query = query.filter(WorkerApplication.status == status)
    
    # 总数
    total = query.count()
    
    # 分页
    applications = query.order_by(
        WorkerApplication.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return ApiResponse.success(
        data={
            "list": [app.to_dict() for app in applications],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        },
        message="获取成功"
    )


@router.post("/applications/{application_id}/review", summary="审核申请（管理员）")
async def review_application(
    application_id: str,
    review: WorkerApplicationReview,
    user_id: str = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    审核家政阿姨申请（管理员专用）
    
    审核通过后：
    1. 更新申请状态为approved
    2. 创建家政阿姨档案（worker_profiles）
    3. 更新用户角色为worker
    """
    # 检查权限
    if user_role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    # 查找申请
    application = db.query(WorkerApplication).filter(
        WorkerApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="申请不存在"
        )
    
    if application.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该申请已被审核"
        )
    
    # 验证拒绝原因
    if review.status == 'rejected' and not review.reject_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="拒绝申请时必须填写拒绝原因"
        )
    
    try:
        # 更新申请状态
        application.status = review.status
        application.reject_reason = review.reject_reason
        application.reviewed_by = user_id
        application.reviewed_at = datetime.now()
        
        # 如果审核通过
        if review.status == 'approved':
            # 1. 创建家政阿姨档案
            worker_profile = WorkerProfile(
                id=generate_uuid(),
                user_id=application.user_id,
                real_name=application.real_name,
                id_card=application.id_card,
                age=application.age,
                gender=application.gender,
                phone=application.phone,
                address=application.address,
                experience_years=application.experience_years,
                skills=application.skills,
                introduction=application.introduction,
                id_card_front=application.id_card_front,
                id_card_back=application.id_card_back,
                health_certificate=application.health_certificate,
                health_report=application.health_report,
                practice_certificate=application.practice_certificate,
                rating=5.0,
                total_orders=0,
                completed_orders=0,
                is_available=True
            )
            db.add(worker_profile)
            
            # 2. 更新用户角色
            user = db.query(User).filter(User.id == application.user_id).first()
            if user:
                user.role = 'worker'
        
        db.commit()
        db.refresh(application)
        
        message = "审核通过，已成功成为家政阿姨" if review.status == 'approved' else "申请已被拒绝"
        
        return ApiResponse.success(
            data=application.to_dict(),
            message=message
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审核失败: {str(e)}"
        )


@router.get("/profile", summary="获取我的家政阿姨档案")
async def get_my_profile(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取当前用户的家政阿姨档案"""
    profile = db.query(WorkerProfile).filter(
        WorkerProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="档案不存在"
        )
    
    return ApiResponse.success(
        data=profile.to_dict(),
        message="获取成功"
    )


@router.put("/profile", summary="更新我的档案")
async def update_my_profile(
    update_data: WorkerProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新家政阿姨档案"""
    profile = db.query(WorkerProfile).filter(
        WorkerProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="档案不存在"
        )
    
    # 更新字段
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(profile, key, value)
    
    try:
        db.commit()
        db.refresh(profile)
        
        return ApiResponse.success(
            data=profile.to_dict(),
            message="更新成功"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}"
        )


@router.get("/workers", summary="????????")
async def get_workers(
    page: int = Query(1, ge=1, description="??"),
    page_size: int = Query(10, ge=1, le=100, description="????"),
    is_available: Optional[bool] = Query(None, description="????"),
    is_recommended: Optional[bool] = Query(None, description="??????"),
    skills: Optional[str] = Query(None, description="????????????"),
    city: Optional[str] = Query(None, description="????"),
    keyword: Optional[str] = Query(None, description="????????"),
    job_type: Optional[str] = Query(None, description="????"),
    service_area: Optional[str] = Query(None, description="????"),
    db: Session = Depends(get_db)
):
    query = db.query(WorkerProfile)

    from sqlalchemy import cast, String, or_
    service_areas_str = cast(WorkerProfile.service_areas, String)
    job_types_str = cast(WorkerProfile.job_types, String)
    skills_str = cast(WorkerProfile.skills, String)

    if is_available is not None:
        query = query.filter(WorkerProfile.is_available == is_available)

    if is_recommended is not None:
        query = query.filter(WorkerProfile.is_recommended == is_recommended)

    if keyword:
        query = query.filter(
            or_(
                WorkerProfile.real_name.like(f"%{keyword}%"),
                WorkerProfile.address.like(f"%{keyword}%"),
                service_areas_str.like(f"%{keyword}%")
            )
        )

    if job_type:
        query = query.filter(job_types_str.like(f"%{job_type}%"))

    if service_area:
        query = query.filter(
            or_(
                WorkerProfile.address.like(f"%{service_area}%"),
                service_areas_str.like(f"%{service_area}%")
            )
        )

    if city:
        city_parts = city.split('/')
        if len(city_parts) == 1:
            query = query.filter(service_areas_str.like(f'%{city_parts[0]}%'))
        elif len(city_parts) == 2:
            query = query.filter(service_areas_str.like(f'%{city_parts[0]}/{city_parts[1]}%'))
        else:
            query = query.filter(service_areas_str.like(f'%{city}%'))

    if skills:
        for skill in [item.strip() for item in skills.replace("?", ",").split(",") if item.strip()]:
            query = query.filter(skills_str.like(f"%{skill}%"))

    total = query.count()
    workers = query.order_by(
        WorkerProfile.is_recommended.desc(),
        WorkerProfile.rating.desc(),
        WorkerProfile.completed_orders.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    result_list = []
    for w in workers:
        d = w.to_dict()
        u = db.query(User).filter(User.id == w.user_id).first()
        d["avatar_url"] = u.avatar_url if u else ""
        d["display_name"] = mask_worker_name(w.real_name)
        d["status_text"] = PUBLIC_STATUS_TEXT.get(w.current_status, "???")
        result_list.append(d)

    return ApiResponse.success(
        data={
            "list": result_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        },
        message="????"
    )


@router.get("/workers/{worker_id}", summary="获取家政阿姨详情")
async def get_worker_detail(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """获取家政阿姨详细信息（公开接口）"""
    worker = db.query(WorkerProfile).filter(
        WorkerProfile.user_id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家政阿姨不存在"
        )

    # 获取阿姨提供的服务
    services = db.query(Service, WorkerService.price).join(
        WorkerService, Service.id == WorkerService.service_id
    ).filter(
        WorkerService.worker_id == worker.user_id,
        WorkerService.is_active == True
    ).all()
    experiences = (
        db.query(WorkerExperience)
        .filter(WorkerExperience.worker_profile_id == worker.id)
        .order_by(WorkerExperience.sort_order.asc(), WorkerExperience.start_date.desc())
        .all()
    )

    worker_dict = worker.to_dict()
    worker_user = db.query(User).filter(User.id == worker.user_id).first()
    worker_dict["avatar_url"] = worker_user.avatar_url if worker_user else ""
    worker_dict["display_name"] = mask_worker_name(worker.real_name)
    worker_dict["status_text"] = PUBLIC_STATUS_TEXT.get(worker.current_status, "待确认")
    worker_dict["recommended_reasons"] = worker.recommended_reasons or []
    worker_dict["work_experiences"] = [item.to_dict() for item in experiences]
    worker_dict["services"] = [
        {
            **service.to_dict(),
            "price": float(price)
        }
        for service, price in services
    ]

    return ApiResponse.success(
        data=worker_dict,
        message="获取成功"
    )


# ============ 时间段管理 API ============

@router.get("/time-slots", summary="获取所有可用时间段")
async def get_time_slots(
    db: Session = Depends(get_db)
):
    """获取系统所有可用的时间段配置"""
    time_slots = db.query(TimeSlot).filter(
        TimeSlot.is_active == True
    ).order_by(TimeSlot.sort_order).all()
    
    return ApiResponse.success(
        data=[slot.to_dict() for slot in time_slots],
        message="获取成功"
    )


@router.get("/schedule", summary="获取我的可预约时间段")
async def get_my_schedule(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前阿姨的可预约时间段设置
    
    返回格式：按星期分组的时间段列表
    """
    # 验证是否是阿姨
    profile = db.query(WorkerProfile).filter(
        WorkerProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是家政阿姨"
        )
    
    # 获取所有时间段
    all_time_slots = db.query(TimeSlot).filter(
        TimeSlot.is_active == True
    ).order_by(TimeSlot.sort_order).all()
    
    # 获取阿姨已设置的时间段
    worker_slots = db.query(WorkerTimeSlot).filter(
        WorkerTimeSlot.worker_id == user_id
    ).all()
    
    # 构建响应：按星期分组
    worker_slot_map = {
        (ws.day_of_week, ws.time_slot_id): ws.is_available 
        for ws in worker_slots
    }
    
    # 构建完整的时间表
    schedule = {}
    for day in range(7):  # 0-6 周日到周六
        schedule[day] = []
        for slot in all_time_slots:
            is_available = worker_slot_map.get((day, slot.id), False)
            schedule[day].append({
                "time_slot_id": slot.id,
                "name": slot.name,
                "start_time": str(slot.start_time),
                "end_time": str(slot.end_time),
                "is_available": is_available
            })
    
    return ApiResponse.success(
        data={
            "schedule": schedule,
            "time_slots": [slot.to_dict() for slot in all_time_slots]
        },
        message="获取成功"
    )


@router.put("/schedule", summary="设置我的可预约时间段")
async def update_my_schedule(
    schedule_data: WorkerScheduleUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    批量设置阿姨的可预约时间段
    
    传入需要设置的时间段列表，会覆盖之前的设置
    """
    # 验证是否是阿姨
    profile = db.query(WorkerProfile).filter(
        WorkerProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是家政阿姨"
        )
    
    try:
        # 处理每个时间段
        for slot_item in schedule_data.slots:
            # 检查是否已存在
            existing = db.query(WorkerTimeSlot).filter(
                WorkerTimeSlot.worker_id == user_id,
                WorkerTimeSlot.day_of_week == slot_item.day_of_week,
                WorkerTimeSlot.time_slot_id == slot_item.time_slot_id
            ).first()
            
            if existing:
                # 更新
                existing.is_available = slot_item.is_available
            else:
                # 新增
                new_slot = WorkerTimeSlot(
                    id=str(uuid.uuid4()),
                    worker_id=user_id,
                    day_of_week=slot_item.day_of_week,
                    time_slot_id=slot_item.time_slot_id,
                    is_available=slot_item.is_available
                )
                db.add(new_slot)
        
        db.commit()
        return ApiResponse.success(message="排班设置成功")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"设置排班失败: {str(e)}"
        )


@router.get("/workers/{worker_id}/schedule", summary="获取阿姨的排班表")
async def get_worker_public_schedule(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """获取指定阿姨的排班表（公开接口）"""
    # 获取基础时间段
    all_time_slots = db.query(TimeSlot).filter(TimeSlot.is_active == True).order_by(TimeSlot.sort_order).all()
    
    # 获取阿姨设置
    worker_slots = db.query(WorkerTimeSlot).filter(
        WorkerTimeSlot.worker_id == worker_id,
        WorkerTimeSlot.is_available == True
    ).all()
    
    # 转换为可用性映射: {day_of_week: [slot_id, ...]}
    availability = {}
    for ws in worker_slots:
        if ws.day_of_week not in availability:
            availability[ws.day_of_week] = []
        availability[ws.day_of_week].append(ws.time_slot_id)
        
    print(f"DEBUG SCHEDULE: worker_id={worker_id}, slots_count={len(worker_slots)}, availability={availability}")
        
    return ApiResponse.success(data={
        "time_slots": [slot.to_dict() for slot in all_time_slots],
        "availability": availability
    })



@router.get("/workers/{worker_id}/reviews", summary="获取阿姨的评价列表")
async def get_worker_reviews(
    worker_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取指定阿姨的评价列表"""
    query = db.query(Review).filter(Review.worker_id == worker_id)
    total = query.count()
    
    reviews = query.order_by(desc(Review.created_at))\
        .offset((page - 1) * page_size).limit(page_size).all()
        
    result = []
    for review in reviews:
        review_dict = review.to_dict()
        # 获取评价人信息
        reviewer = db.query(User).filter(User.id == review.user_id).first()
        if review.is_anonymous:
            review_dict['user_name'] = "匿名用户"
            review_dict['user_avatar'] = ""
        else:
            review_dict['user_name'] = reviewer.nickname if reviewer and reviewer.nickname else (reviewer.phone if reviewer else "未知用户")
            review_dict['user_avatar'] = reviewer.avatar_url if reviewer else ""
            
        result.append(review_dict)
    
    return ApiResponse.success(data={
        "list": result,
        "total": total,
        "page": page,
        "page_size": page_size
    })

# ============ 服务定价管理 API ============

@router.get("/all-services", summary="获取所有服务项目")
async def get_all_services(
    db: Session = Depends(get_db)
):
    """获取系统所有可用的服务项目"""
    services = db.query(Service).filter(
        Service.is_active == True
    ).order_by(Service.sort_order).all()
    
    return ApiResponse.success(
        data=[svc.to_dict() for svc in services],
        message="获取成功"
    )


@router.get("/my-services", summary="获取我提供的服务")
async def get_my_services(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取当前阿姨提供的服务及定价"""
    # 验证是否是阿姨
    profile = db.query(WorkerProfile).filter(
        WorkerProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是家政阿姨"
        )
    
    # 获取阿姨的服务
    worker_services = db.query(WorkerService).filter(
        WorkerService.worker_id == user_id
    ).all()
    
    # 获取服务详情
    result = []
    for ws in worker_services:
        service = db.query(Service).filter(Service.id == ws.service_id).first()
        if service:
            result.append({
                "id": ws.id,
                "worker_id": ws.worker_id,
                "service_id": ws.service_id,
                "service_name": service.name,
                "service_icon": service.icon,
                "service_category": service.category,
                "default_price": float(service.price) if service.price else None,
                "price": float(ws.price) if ws.price else None,
                "unit": service.unit,
                "is_active": ws.is_active
            })
    
    return ApiResponse.success(
        data=result,
        message="获取成功"
    )


@router.post("/my-services", summary="添加/更新我的服务")
async def add_my_service(
    service_data: WorkerServiceCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    添加或更新阿姨提供的服务
    
    如果已存在则更新价格和状态
    """
    # 验证是否是阿姨
    profile = db.query(WorkerProfile).filter(
        WorkerProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是家政阿姨"
        )
    
    # 验证服务是否存在
    service = db.query(Service).filter(
        Service.id == service_data.service_id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务项目不存在"
        )
    
    try:
        # 检查是否已存在
        existing = db.query(WorkerService).filter(
            WorkerService.worker_id == user_id,
            WorkerService.service_id == service_data.service_id
        ).first()
        
        if existing:
            # 更新
            existing.price = service_data.price
            existing.is_active = service_data.is_active
            message = "服务更新成功"
        else:
            # 新增
            new_service = WorkerService(
                id=generate_uuid(),
                worker_id=user_id,
                service_id=service_data.service_id,
                price=service_data.price,
                is_active=service_data.is_active
            )
            db.add(new_service)
            message = "服务添加成功"
        
        db.commit()
        
        return ApiResponse.success(
            data=None,
            message=message
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )


@router.delete("/my-services/{service_id}", summary="移除我的服务")
async def remove_my_service(
    service_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """移除阿姨提供的服务"""
    # 验证是否是阿姨
    profile = db.query(WorkerProfile).filter(
        WorkerProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是家政阿姨"
        )
    
    # 查找并删除
    worker_service = db.query(WorkerService).filter(
        WorkerService.worker_id == user_id,
        WorkerService.service_id == service_id
    ).first()
    
    if not worker_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    try:
        db.delete(worker_service)
        db.commit()
        
        return ApiResponse.success(
            data=None,
            message="服务已移除"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )
