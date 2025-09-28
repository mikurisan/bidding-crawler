from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class QianlimaBiddingDetailContact(SQLModel, table=True):
    __tablename__ = "qianlima_bidding_detail_contact"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    head_id: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None, max_length=10)
    telphone: Optional[str] = Field(default=None, max_length=100)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)