#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""客户线索与业务跟进模型"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Enum, DECIMAL, ForeignKey, Boolean, Date
from sqlalchemy import func
from app.core.database import Base


class CustomerLead(Base):
    """客户线索表"""
    __tablename__ = "customer_leads"

    id = Column(String(36), primary_key=True)
    lead_no = Column(String(32), unique=True, nullable=True)
    owner_staff_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    source = Column(String(50), nullable=True)
    source_detail = Column(String(100), nullable=True)
    lead_name = Column(String(100), nullable=True)
    lead_type = Column(String(50), nullable=True)
    lead_date = Column(Date, nullable=True)
    customer_name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    wechat = Column(String(50), nullable=True)
    service_type = Column(String(50), nullable=True)
    demand_address = Column(String(255), nullable=True)
    demand_detail = Column(Text, nullable=True)
    budget = Column(DECIMAL(10, 2), nullable=True)
    lead_category = Column(Enum("A", "B"), default="B", nullable=True)
    status = Column(
        Enum("new", "contacting", "invalid", "interviewing", "signed", "closed"),
        default="new",
        nullable=True
    )
    invalid_reason = Column(String(255), nullable=True)
    latest_follow_up_at = Column(TIMESTAMP, nullable=True)
    next_follow_up_at = Column(TIMESTAMP, nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "lead_no": self.lead_no,
            "owner_staff_id": self.owner_staff_id,
            "source": self.source,
            "source_detail": self.source_detail,
            "lead_name": self.lead_name,
            "lead_type": self.lead_type,
            "lead_date": self.lead_date.isoformat() if self.lead_date else None,
            "customer_name": self.customer_name,
            "phone": self.phone,
            "wechat": self.wechat,
            "service_type": self.service_type,
            "demand_address": self.demand_address,
            "demand_detail": self.demand_detail,
            "budget": float(self.budget) if self.budget is not None else None,
            "lead_category": self.lead_category,
            "status": self.status,
            "invalid_reason": self.invalid_reason,
            "latest_follow_up_at": self.latest_follow_up_at.isoformat() if self.latest_follow_up_at else None,
            "next_follow_up_at": self.next_follow_up_at.isoformat() if self.next_follow_up_at else None,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class LeadFollowRecord(Base):
    """客户线索跟进记录表"""
    __tablename__ = "lead_follow_records"

    id = Column(String(36), primary_key=True)
    lead_id = Column(String(36), ForeignKey("customer_leads.id"), nullable=False)
    staff_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    follow_type = Column(Enum("phone", "wechat", "visit", "other"), default="phone", nullable=True)
    follow_result = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    next_action = Column(String(255), nullable=True)
    next_follow_up_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "staff_id": self.staff_id,
            "follow_type": self.follow_type,
            "follow_result": self.follow_result,
            "content": self.content,
            "next_action": self.next_action,
            "next_follow_up_at": self.next_follow_up_at.isoformat() if self.next_follow_up_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }



class ServiceContract(Base):
    """?????????"""
    __tablename__ = "service_contracts"

    id = Column(String(36), primary_key=True)
    contract_no = Column(String(32), unique=True, nullable=False)
    lead_id = Column(String(36), ForeignKey("customer_leads.id"), nullable=True)
    customer_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    worker_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    broker_staff_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    customer_name = Column(String(50), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_source = Column(String(50), nullable=True)
    service_address = Column(String(255), nullable=False)
    service_type = Column(String(50), nullable=False)
    demand_detail = Column(Text, nullable=True)
    contract_date = Column(Date, nullable=True)
    sign_date = Column(TIMESTAMP, nullable=True)
    start_date = Column(TIMESTAMP, nullable=True)
    end_date = Column(TIMESTAMP, nullable=True)
    actual_end_date = Column(TIMESTAMP, nullable=True)
    status = Column(
        Enum("pending_start", "serving", "paused", "completed", "terminated", "refunded"),
        default="pending_start",
        nullable=True
    )
    replace_status = Column(String(100), nullable=True)
    contract_amount = Column(DECIMAL(10, 2), nullable=True)
    discount_rate = Column(DECIMAL(5, 2), nullable=True)
    actual_received = Column(DECIMAL(10, 2), nullable=True)
    worker_salary_desc = Column(String(255), nullable=True)
    worker_salary_amount = Column(DECIMAL(10, 2), nullable=True)
    service_fee = Column(DECIMAL(10, 2), nullable=True)
    referral_fee = Column(DECIMAL(10, 2), nullable=True)
    refund_amount = Column(DECIMAL(10, 2), nullable=True)
    refund_reason = Column(String(255), nullable=True)
    latest_follow_up_at = Column(TIMESTAMP, nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "contract_no": self.contract_no,
            "lead_id": self.lead_id,
            "customer_user_id": self.customer_user_id,
            "worker_user_id": self.worker_user_id,
            "broker_staff_id": self.broker_staff_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "customer_source": self.customer_source,
            "service_address": self.service_address,
            "service_type": self.service_type,
            "demand_detail": self.demand_detail,
            "contract_date": self.contract_date.isoformat() if self.contract_date else None,
            "sign_date": self.sign_date.isoformat() if self.sign_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "actual_end_date": self.actual_end_date.isoformat() if self.actual_end_date else None,
            "status": self.status,
            "replace_status": self.replace_status,
            "contract_amount": float(self.contract_amount) if self.contract_amount is not None else None,
            "discount_rate": float(self.discount_rate) if self.discount_rate is not None else None,
            "actual_received": float(self.actual_received) if self.actual_received is not None else None,
            "worker_salary_desc": self.worker_salary_desc,
            "worker_salary_amount": float(self.worker_salary_amount) if self.worker_salary_amount is not None else None,
            "service_fee": float(self.service_fee) if self.service_fee is not None else None,
            "referral_fee": float(self.referral_fee) if self.referral_fee is not None else None,
            "refund_amount": float(self.refund_amount) if self.refund_amount is not None else None,
            "refund_reason": self.refund_reason,
            "latest_follow_up_at": self.latest_follow_up_at.isoformat() if self.latest_follow_up_at else None,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ContractFollowup(Base):
    """??????????"""
    __tablename__ = "contract_followups"

    id = Column(String(36), primary_key=True)
    contract_id = Column(String(36), ForeignKey("service_contracts.id"), nullable=False)
    staff_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    follow_type = Column(Enum("d1", "d7", "d30", "after_sale", "other"), default="other", nullable=True)
    planned_at = Column(TIMESTAMP, nullable=True)
    followed_at = Column(TIMESTAMP, nullable=True)
    result = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    need_action = Column(Boolean, default=False, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "staff_id": self.staff_id,
            "follow_type": self.follow_type,
            "planned_at": self.planned_at.isoformat() if self.planned_at else None,
            "followed_at": self.followed_at.isoformat() if self.followed_at else None,
            "result": self.result,
            "content": self.content,
            "need_action": bool(self.need_action),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
