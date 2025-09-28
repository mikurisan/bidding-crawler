from sqlmodel import SQLModel, Field
from datetime import datetime, date
from typing import Optional


class QianlimaBiddingDetailAbstract(SQLModel, table=True):
    __tablename__ = "qianlima_bidding_detail_abstract"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    head_id: Optional[int] = Field(default=None)
    project_number: Optional[str] = Field(default=None, max_length=255)
    estimated_amount: Optional[str] = Field(default=None, max_length=255)
    bidding_org: Optional[str] = Field(default=None, max_length=255)
    agency: Optional[str] = Field(default=None, max_length=255)
    registration_ddl: Optional[date] = Field(default=None)
    bidding_ddl: Optional[date] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
