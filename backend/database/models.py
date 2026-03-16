# backend/database/models.py
"""
SQLAlchemy ORM Models for Ay11Sutra
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .connection import Base
import uuid
from datetime import datetime


class User(Base):
    """User accounts for multi-tenant support."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    organization = Column(String(255))
    phone = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    audits = relationship("Audit", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Audit(Base):
    """Accessibility audit records."""
    __tablename__ = "audits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    dom_hash = Column(String(64), index=True)
    status = Column(String(20), default="completed")  # pending, running, completed, error
    total_issues = Column(Integer, default=0)
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audits")
    issues = relationship("Issue", back_populates="audit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Audit {self.url[:50]}>"


class Issue(Base):
    """Individual accessibility issues found in audits."""
    __tablename__ = "issues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Issue details
    rule = Column(String(100))
    category = Column(String(20))  # syntax, semantic, visual, interaction
    priority = Column(String(20))
    wcag_sc = Column(String(20))
    description = Column(Text)
    selector = Column(Text)
    html_snippet = Column(Text)
    
    # AI-generated fixes
    ai_explanation = Column(Text)
    ai_fixed_code = Column(Text)
    
    # Relationships
    audit = relationship("Audit", back_populates="issues")
    
    def __repr__(self):
        return f"<Issue {self.rule}>"
