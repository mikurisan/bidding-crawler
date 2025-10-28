from typing import List
from datetime import datetime
from app.models import QianlimaBiddingDetailHead, QianlimaBiddingDetailAbstract
from app.models import QianlimaBiddingDetailContent, QianlimaBiddingDetailContact
from app.models import QianlimaBiddingDetailsToCrm
from app.schemas import BiddingDetailResponse
from sqlalchemy.exc import IntegrityError
from app.db import id_generator
from .base import BaseRepository
from sqlmodel import select, func
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class QianlimaBiddingDetailHeadRepository(BaseRepository):
    def create_records_from_json(
        self, json_str: str, url: str
    ) -> List[QianlimaBiddingDetailHead]:
        try:
            data_list = json.loads(json_str)
            created_ids = []

            for data in data_list:
                released_at = None
                if data.get("date", None):
                    try:
                        released_at = datetime.strptime(data["date"], "%Y/%m/%d").date()
                    except ValueError:
                        logger.info(f"Date {released_at} can't be converted to.")
                        pass
                
                record = QianlimaBiddingDetailHead(
                    id=id_generator.generate(),
                    title=data["title"],
                    url=url,
                    type=data.get("type", None),
                    area=data.get("area", None),
                    released_at=released_at,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                try:
                    self.session.add(record)
                    self.session.commit()
                    self.session.refresh(record)
                    created_ids.append(record.id)
                except IntegrityError:
                    self.session.rollback()
                    logger.warning(f"Record already exists, skipping: {data['title']}")
                    continue

            return created_ids

        except Exception as e:
            self.session.rollback()
            raise Exception(f"An error occurred while creating the record: {e}")
        
    def get_bidding_details(self):
        try:
            statement = select(
                QianlimaBiddingDetailHead.id,
                QianlimaBiddingDetailAbstract.bidding_org,
                QianlimaBiddingDetailContent.content,
                QianlimaBiddingDetailContact.telphone,
                func.substring_index(QianlimaBiddingDetailHead.area, '-', 1).label('area_prefix'),
                QianlimaBiddingDetailContact.name,
                QianlimaBiddingDetailHead.title
            ).select_from(QianlimaBiddingDetailHead)\
            .outerjoin(
                QianlimaBiddingDetailAbstract, 
                QianlimaBiddingDetailHead.id == QianlimaBiddingDetailAbstract.head_id
            ).outerjoin(
                QianlimaBiddingDetailContent,
                QianlimaBiddingDetailHead.id == QianlimaBiddingDetailContent.head_id
            ).outerjoin(
                QianlimaBiddingDetailContact,
                QianlimaBiddingDetailHead.id == QianlimaBiddingDetailContact.head_id
            ).where(
                QianlimaBiddingDetailHead.id.not_in(
                    select(QianlimaBiddingDetailsToCrm.head_id).where(
                        QianlimaBiddingDetailsToCrm.head_id.is_not(None)
                        )
                    ),
                QianlimaBiddingDetailHead.released_at >= datetime.now().date() - timedelta(days=7),
                QianlimaBiddingDetailContact.telphone.not_like('%*%') 
            )

            results = self.session.exec(statement).all()
            
            return [
                BiddingDetailResponse(
                    id=result.id,
                    bidding_org=result.bidding_org,
                    content=result.content,
                    telphone=result.telphone,
                    area=result.area_prefix,
                    name=result.name
                )
                for result in results
            ]

        except Exception as e:
            raise Exception(f"An error occurred while querying bidding details: {e}")