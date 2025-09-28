from sqlmodel import SQLModel, Field
from datetime import datetime, date
from typing import Optional

class QianlimaBiddingDetailHead(SQLModel, table=True):
    __tablename__ = "qianlima_bidding_detail_head"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, max_length=255)
    url: str = Field(max_length=2048)
    type: Optional[str] = Field(default=None, max_length=15)
    area: Optional[str] = Field(default=None, max_length=100)
    released_at: Optional[date] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)