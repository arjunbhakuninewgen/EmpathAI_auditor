# backend/database/crud.py
"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from uuid import UUID
from . import models


# ==================== USER CRUD ====================

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(
    db: Session,
    email: str,
    password_hash: str,
    name: str = None,
    organization: str = None,
    phone: str = None
) -> models.User:
    """Create a new user."""
    user = models.User(
        email=email,
        password_hash=password_hash,
        name=name,
        organization=organization,
        phone=phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ==================== AUDIT CRUD ====================

def create_audit(
    db: Session,
    user_id: UUID,
    url: str,
    dom_hash: str,
    total_issues: int = 0,
    cached: bool = False
) -> models.Audit:
    """Create a new audit record."""
    audit = models.Audit(
        user_id=user_id,
        url=url,
        dom_hash=dom_hash,
        total_issues=total_issues,
        cached=cached,
        status="completed"
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def get_audit_by_id(db: Session, audit_id: UUID) -> Optional[models.Audit]:
    """Get audit by ID."""
    return db.query(models.Audit).filter(models.Audit.id == audit_id).first()


def get_audits_by_user(db: Session, user_id: UUID, limit: int = 50, url_filter: str = None, include_cached: bool = False) -> List[models.Audit]:
    """
    Get user's audit history, newest first.
    By default (include_cached=False), only returns full server-side audits (non-cached).
    """
    query = db.query(models.Audit).filter(models.Audit.user_id == user_id)
    
    if not include_cached:
        query = query.filter(models.Audit.cached == False)
    
    if url_filter:
        query = query.filter(models.Audit.url.ilike(f"%{url_filter}%"))
        
    return query.order_by(desc(models.Audit.created_at)).limit(limit).all()


def get_cached_audit(db: Session, url: str, dom_hash: str) -> Optional[models.Audit]:
    """Check if we have a cached audit for this URL + DOM hash."""
    return db.query(models.Audit)\
        .filter(models.Audit.url == url, models.Audit.dom_hash == dom_hash)\
        .order_by(desc(models.Audit.created_at))\
        .first()


# ==================== ISSUE CRUD ====================

def create_issue(db: Session, audit_id: UUID, issue_data: dict) -> models.Issue:
    """Create an issue linked to an audit."""
    issue = models.Issue(
        audit_id=audit_id,
        rule=issue_data.get("rule"),
        category=issue_data.get("category"),
        priority=issue_data.get("fix_priority"),
        wcag_sc=issue_data.get("wcag_sc"),
        description=issue_data.get("description"),
        selector=issue_data.get("selector"),
        html_snippet=issue_data.get("html_snippet"),
        ai_explanation=issue_data.get("ai_explanation"),
        ai_fixed_code=issue_data.get("ai_fixed_code")
    )
    db.add(issue)
    return issue


def bulk_create_issues(db: Session, audit_id: UUID, issues: List[dict]) -> List[models.Issue]:
    """Create multiple issues for an audit."""
    db_issues = []
    for issue_data in issues:
        issue = create_issue(db, audit_id, issue_data)
        db_issues.append(issue)
    db.commit()
    return db_issues


def get_issues_by_audit(db: Session, audit_id: UUID) -> List[models.Issue]:
    """Get all issues for an audit."""
    return db.query(models.Issue)\
        .filter(models.Issue.audit_id == audit_id)\
        .all()
