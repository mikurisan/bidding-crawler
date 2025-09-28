from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class QianlimaBiddingDetailsToCrm(SQLModel, table=True):
    __tablename__ = "qianlima_bidding_details_to_crm"

    id: Optional[int] = Field(default=None, primary_key=True)
    head_id: Optional[int] = Field(default=None)
    company_name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=100)
    user_name: Optional[str] = Field(default=None, max_length=100)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)