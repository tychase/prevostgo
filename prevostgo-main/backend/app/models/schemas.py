"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class ConditionEnum(str, Enum):
    new = "new"
    pre_owned = "pre-owned"
    preowned = "pre-owned"  # Also accept without hyphen

class PriceStatusEnum(str, Enum):
    available = "available"
    contact_for_price = "contact_for_price"

class TimeframeEnum(str, Enum):
    immediate = "immediate"
    three_months = "3_months"
    six_months = "6_months"
    planning = "planning"

class FinancingStatusEnum(str, Enum):
    cash = "cash"
    pre_approved = "pre_approved"
    need_financing = "need_financing"

class LeadStatusEnum(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    converted = "converted"

# Coach Schemas
class CoachBase(BaseModel):
    title: str
    year: int
    model: Optional[str] = None
    chassis_type: Optional[str] = None
    converter: Optional[str] = None
    condition: str  # Changed from ConditionEnum to handle various formats
    
    price: Optional[int] = None
    price_display: Optional[str] = None
    price_status: str = "contact_for_price"  # Changed from PriceStatusEnum
    
    mileage: Optional[int] = None
    engine: Optional[str] = None
    slide_count: int = 0
    
    features: List[str] = []
    bathroom_config: Optional[str] = None
    stock_number: Optional[str] = None
    
    images: List[str] = []
    virtual_tour_url: Optional[str] = None
    
    dealer_name: Optional[str] = None
    dealer_state: Optional[str] = None
    dealer_phone: Optional[str] = None
    dealer_email: Optional[str] = None  # Changed from EmailStr to handle invalid emails

class CoachCreate(CoachBase):
    listing_url: Optional[str] = None
    source: str = "prevost-stuff.com"

class CoachUpdate(BaseModel):
    status: Optional[str] = None
    price: Optional[int] = None
    price_display: Optional[str] = None
    price_status: Optional[str] = None  # Changed from PriceStatusEnum

class CoachInDB(CoachBase):
    id: str
    listing_url: Optional[str] = None
    source: str
    status: str = "available"
    scraped_at: datetime
    updated_at: datetime
    views: int = 0
    inquiries: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class CoachResponse(CoachInDB):
    """Response model for API"""
    pass

class CoachListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    coaches: List[CoachResponse]

# Lead Schemas
class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    timeframe: Optional[TimeframeEnum] = None
    financing_status: Optional[FinancingStatusEnum] = None
    
    preferred_models: List[str] = []
    preferred_years: List[int] = []
    must_have_features: List[str] = []

class LeadCreate(LeadBase):
    source: Optional[str] = "direct"
    utm_campaign: Optional[str] = None

class LeadInDB(LeadBase):
    id: int
    coaches_viewed: List[str] = []
    coaches_inquired: List[str] = []
    score: int = 0
    score_factors: Dict[str, Any] = {}
    status: LeadStatusEnum = LeadStatusEnum.new
    assigned_dealer: Optional[str] = None
    assigned_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LeadResponse(LeadInDB):
    """Response model for API"""
    pass

class LeadScoreUpdate(BaseModel):
    score: int
    score_factors: Dict[str, Any]

# Search Schemas
class SearchFilters(BaseModel):
    # Price range
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    
    # Year range
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    
    # Mileage
    mileage_max: Optional[int] = None
    
    # Specific filters
    models: List[str] = []
    converters: List[str] = []
    slide_counts: List[int] = []
    conditions: List[str] = []  # Changed from ConditionEnum
    
    # Features
    must_have_features: List[str] = []
    
    # Dealer location
    dealer_states: List[str] = []
    
    # Sorting
    sort_by: str = "price"  # price, year, mileage, created_at
    sort_order: str = "asc"  # asc, desc
    
    # Pagination
    page: int = 1
    per_page: int = 20

class SearchAlertCreate(BaseModel):
    criteria: SearchFilters
    frequency: str = "immediate"  # immediate, daily, weekly

class SearchAlertResponse(BaseModel):
    id: int
    criteria: Dict[str, Any]
    frequency: str
    active: bool
    last_sent: Optional[datetime] = None
    matches_found: int = 0
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Analytics Schemas
class AnalyticsEvent(BaseModel):
    event_type: str  # view, inquiry, search, filter
    coach_id: Optional[str] = None
    lead_id: Optional[int] = None
    event_data: Dict[str, Any] = {}
    session_id: Optional[str] = None

class InventorySummary(BaseModel):
    total_coaches: int
    by_condition: Dict[str, int]
    by_model: Dict[str, int]
    by_converter: Dict[str, int]
    by_year: Dict[str, int]
    price_ranges: Dict[str, int]
    
# Inquiry Schemas
class InquiryCreate(BaseModel):
    coach_id: str
    lead_info: LeadCreate
    message: Optional[str] = None
    preferred_contact_method: str = "email"  # email, phone

class InquiryResponse(BaseModel):
    success: bool
    message: str
    lead_id: Optional[int] = None
    coach_id: str
