"""
Modèle pour le journal d'audit des actions admin.
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class AdminAuditLog(Base):
    """Journal des actions effectuées par les administrateurs."""
    __tablename__ = "admin_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)  # user_patch, exercise_create, etc.
    resource_type = Column(String(30), nullable=True, index=True)  # user, exercise, challenge
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON string avec infos complémentaires
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    admin_user = relationship("User", foreign_keys=[admin_user_id])
