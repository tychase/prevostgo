"""
Database models for PrevostGO
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, Table
from app.database import metadata
import datetime

# Coaches table
coaches = Table(
    "coaches",
    metadata,
    Column("id", String, primary_key=True),
    Column("title", String, nullable=False),
    Column("year", Integer, nullable=False),
    Column("make", String, default="Prevost"),
    Column("model", String),
    Column("chassis_type", String),
    Column("converter", String),
    Column("condition", String),
    Column("price", Integer),  # in cents
    Column("price_display", String),
    Column("price_status", String),
    Column("mileage", Integer),
    Column("engine", String),
    Column("slide_count", Integer, default=0),
    Column("features", JSON, default=[]),
    Column("bathroom_config", String),
    Column("stock_number", String),
    Column("images", JSON, default=[]),
    Column("virtual_tour_url", String),
    Column("dealer_name", String),
    Column("dealer_state", String),
    Column("dealer_phone", String),
    Column("dealer_email", String),
    Column("listing_url", String),
    Column("source", String, default="prevost-stuff.com"),
    Column("status", String, default="available"),
    Column("scraped_at", DateTime, default=datetime.datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.datetime.utcnow),
    Column("views", Integer, default=0),
    Column("inquiries", Integer, default=0),
)

# Leads table
leads = Table(
    "leads",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("email", String, nullable=False),
    Column("phone", String),
    Column("company", String),
    Column("budget_min", Integer),
    Column("budget_max", Integer),
    Column("timeframe", String),
    Column("financing_status", String),
    Column("preferred_models", JSON, default=[]),
    Column("preferred_years", JSON, default=[]),
    Column("must_have_features", JSON, default=[]),
    Column("coaches_viewed", JSON, default=[]),
    Column("coaches_inquired", JSON, default=[]),
    Column("score", Integer, default=0),
    Column("score_factors", JSON, default={}),
    Column("status", String, default="new"),
    Column("assigned_dealer", String),
    Column("assigned_at", DateTime),
    Column("source", String),
    Column("utm_campaign", String),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.datetime.utcnow),
    Column("notes", Text),
    Column("last_contacted", DateTime),
    Column("followup_date", DateTime),
)
