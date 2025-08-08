"""
Leads and inquiry management router
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from app.models.database import get_db, Lead, Coach, Analytics
from app.models.schemas import (
    LeadCreate, LeadResponse, LeadScoreUpdate,
    InquiryCreate, InquiryResponse, LeadStatusEnum
)

router = APIRouter()

def calculate_lead_score(lead_data: dict) -> tuple[int, dict]:
    """Calculate lead score based on various factors"""
    score = 0
    factors = {}
    
    # Budget factors
    if lead_data.get('budget_min') and lead_data.get('budget_max'):
        budget_range = lead_data['budget_max'] - lead_data['budget_min']
        if lead_data['budget_max'] >= 1000000:  # $1M+
            score += 30
            factors['high_budget'] = 30
        elif lead_data['budget_max'] >= 500000:  # $500k+
            score += 20
            factors['medium_budget'] = 20
        else:
            score += 10
            factors['standard_budget'] = 10
            
    # Timeframe factors
    timeframe = lead_data.get('timeframe')
    if timeframe == 'immediate':
        score += 25
        factors['immediate_buyer'] = 25
    elif timeframe == '3_months':
        score += 15
        factors['near_term_buyer'] = 15
    elif timeframe == '6_months':
        score += 10
        factors['mid_term_buyer'] = 10
    else:
        score += 5
        factors['long_term_buyer'] = 5
        
    # Financing factors
    financing = lead_data.get('financing_status')
    if financing == 'cash':
        score += 20
        factors['cash_buyer'] = 20
    elif financing == 'pre_approved':
        score += 15
        factors['pre_approved'] = 15
    else:
        score += 5
        factors['needs_financing'] = 5
        
    # Contact info completeness
    if lead_data.get('phone'):
        score += 10
        factors['has_phone'] = 10
    if lead_data.get('company'):
        score += 5
        factors['has_company'] = 5
        
    # Engagement factors (would be updated later)
    # - Coaches viewed
    # - Time on site
    # - Return visits
    
    return score, factors

async def send_lead_notification(lead: Lead, coach: Optional[Coach], db: AsyncSession):
    """Send email notification for new lead (background task)"""
    # In production, use proper email service (SendGrid, AWS SES, etc.)
    # This is a placeholder
    
    try:
        # Get dealer email
        dealer_email = coach.dealer_email if coach else os.getenv("DEFAULT_DEALER_EMAIL")
        if not dealer_email:
            return
            
        # Create email
        subject = f"New PrevostGO Lead: {lead.first_name} {lead.last_name}"
        
        body = f"""
        New lead received from PrevostGO:
        
        Name: {lead.first_name} {lead.last_name}
        Email: {lead.email}
        Phone: {lead.phone or 'Not provided'}
        Company: {lead.company or 'Not provided'}
        
        Budget: ${lead.budget_min:,} - ${lead.budget_max:,}
        Timeframe: {lead.timeframe}
        Financing: {lead.financing_status}
        
        Lead Score: {lead.score}
        
        """
        
        if coach:
            body += f"""
        Inquired about:
        {coach.year} {coach.converter} {coach.model}
        Stock #: {coach.stock_number}
        Price: {coach.price_display}
        """
        
        # Log the notification (in production, actually send email)
        print(f"Would send email to {dealer_email}:")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        
    except Exception as e:
        print(f"Error sending lead notification: {str(e)}")

@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create new lead"""
    
    # Check if lead already exists
    result = await db.execute(
        select(Lead).where(Lead.email == lead_data.email)
    )
    existing_lead = result.scalar_one_or_none()
    
    if existing_lead:
        # Update existing lead
        for field, value in lead_data.model_dump(exclude_unset=True).items():
            setattr(existing_lead, field, value)
        existing_lead.updated_at = datetime.utcnow()
        lead = existing_lead
    else:
        # Calculate lead score
        score, factors = calculate_lead_score(lead_data.model_dump())
        
        # Create new lead
        lead = Lead(
            **lead_data.model_dump(),
            score=score,
            score_factors=factors
        )
        db.add(lead)
        
    await db.commit()
    await db.refresh(lead)
    
    # Send notification in background
    background_tasks.add_task(send_lead_notification, lead, None, db)
    
    return LeadResponse.model_validate(lead)

@router.post("/inquiry", response_model=InquiryResponse)
async def create_inquiry(
    inquiry: InquiryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create inquiry for specific coach"""
    
    # Get coach
    coach_result = await db.execute(
        select(Coach).where(Coach.id == inquiry.coach_id)
    )
    coach = coach_result.scalar_one_or_none()
    
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
        
    # Create or update lead
    lead_result = await db.execute(
        select(Lead).where(Lead.email == inquiry.lead_info.email)
    )
    lead = lead_result.scalar_one_or_none()
    
    if lead:
        # Update existing lead
        for field, value in inquiry.lead_info.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)
        lead.updated_at = datetime.utcnow()
    else:
        # Calculate lead score
        score, factors = calculate_lead_score(inquiry.lead_info.model_dump())
        
        # Create new lead
        lead = Lead(
            **inquiry.lead_info.model_dump(),
            score=score,
            score_factors=factors
        )
        db.add(lead)
        
    # Add coach to inquired list
    if inquiry.coach_id not in lead.coaches_inquired:
        lead.coaches_inquired.append(inquiry.coach_id)
        
    # Update coach inquiry count
    coach.inquiries += 1
    
    # Log analytics event
    analytics = Analytics(
        event_type="inquiry",
        coach_id=inquiry.coach_id,
        lead_id=lead.id,
        event_data={
            "message": inquiry.message,
            "contact_method": inquiry.preferred_contact_method
        }
    )
    db.add(analytics)
    
    await db.commit()
    
    # Send notification in background
    background_tasks.add_task(send_lead_notification, lead, coach, db)
    
    return InquiryResponse(
        success=True,
        message="Inquiry submitted successfully",
        lead_id=lead.id,
        coach_id=inquiry.coach_id
    )

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get lead by ID (admin only - add auth later)"""
    
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return LeadResponse.model_validate(lead)

@router.put("/{lead_id}/score", response_model=LeadResponse)
async def update_lead_score(
    lead_id: int,
    score_update: LeadScoreUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update lead score (admin only - add auth later)"""
    
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lead.score = score_update.score
    lead.score_factors = score_update.score_factors
    lead.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(lead)
    
    return LeadResponse.model_validate(lead)

@router.put("/{lead_id}/status")
async def update_lead_status(
    lead_id: int,
    status: LeadStatusEnum,
    assigned_dealer: Optional[str] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Update lead status (admin only - add auth later)"""
    
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lead.status = status
    lead.updated_at = datetime.utcnow()
    
    if assigned_dealer:
        lead.assigned_dealer = assigned_dealer
        lead.assigned_at = datetime.utcnow()
        
    if notes:
        lead.notes = notes
        
    await db.commit()
    
    return {
        "success": True,
        "message": f"Lead status updated to {status}",
        "lead_id": lead_id
    }

@router.post("/{lead_id}/track-view")
async def track_coach_view(
    lead_id: int,
    coach_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Track when a lead views a coach"""
    
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Add to viewed list if not already there
    if coach_id not in lead.coaches_viewed:
        lead.coaches_viewed.append(coach_id)
        lead.updated_at = datetime.utcnow()
        
        # Log analytics
        analytics = Analytics(
            event_type="lead_view",
            coach_id=coach_id,
            lead_id=lead_id,
            event_data={"repeat_view": False}
        )
        db.add(analytics)
    else:
        # Log repeat view
        analytics = Analytics(
            event_type="lead_view",
            coach_id=coach_id,
            lead_id=lead_id,
            event_data={"repeat_view": True}
        )
        db.add(analytics)
        
    await db.commit()
    
    return {"success": True, "message": "View tracked"}

@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    status: Optional[LeadStatusEnum] = None,
    min_score: Optional[int] = None,
    assigned_dealer: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get leads with filters (admin only - add auth later)"""
    
    query = select(Lead)
    
    if status:
        query = query.where(Lead.status == status)
    if min_score is not None:
        query = query.where(Lead.score >= min_score)
    if assigned_dealer:
        query = query.where(Lead.assigned_dealer == assigned_dealer)
        
    query = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    leads = result.scalars().all()
    
    return [LeadResponse.model_validate(lead) for lead in leads]
