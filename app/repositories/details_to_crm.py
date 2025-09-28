from app.schemas import BiddingDetailResponse
from app.models import QianlimaBiddingDetailsToCrm
from app.db import id_generator
from .base import BaseRepository
import logging

logger = logging.getLogger(__name__)
        
class QianlimaBiddingDetailsToCrmRepository(BaseRepository):
    def create_from_bidding_detail(self, bidding_detail: BiddingDetailResponse) -> QianlimaBiddingDetailsToCrm:
        new_record = QianlimaBiddingDetailsToCrm(
            id=id_generator.generate(),
            head_id=bidding_detail.id,
            company_name=bidding_detail.bidding_org,
            description=bidding_detail.content,
            phone_number=bidding_detail.telphone,
            province=bidding_detail.area,
            user_name=bidding_detail.name
        )
        
        self.session.add(new_record)
        self.session.commit()
        self.session.refresh(new_record)
        
        return new_record.id