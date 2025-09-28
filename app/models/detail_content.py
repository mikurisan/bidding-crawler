from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class QianlimaBiddingDetailContent(SQLModel, table=True):
    __tablename__ = "qianlima_bidding_detail_content"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    head_id: Optional[int] = Field(default=None)
    content: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)