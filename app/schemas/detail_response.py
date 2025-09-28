from sqlmodel import SQLModel
from typing import Optional

class BiddingDetailResponse(SQLModel):
    id: Optional[int]
    bidding_org: Optional[str]
    content: Optional[str]
    telphone: Optional[str]
    area: Optional[str]
    name: Optional[str]