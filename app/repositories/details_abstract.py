from typing import List
from datetime import datetime
from app.models import QianlimaBiddingDetailAbstract
from sqlalchemy.exc import IntegrityError
from app.db import id_generator
from .base import BaseRepository
import json
import logging

logger = logging.getLogger(__name__)

class QianlimaBiddingDetailAbstractRepository(BaseRepository):
    def create_records_from_json(
        self, json_str: str, head_id: int
    ) -> List[QianlimaBiddingDetailAbstract]:
        try:
            data_list = json.loads(json_str)
            created_ids = []

            for data in data_list:
                registration_ddl = None
                if data.get("registration_ddl", None):
                    try:
                        registration_ddl = datetime.strptime(data["registration_ddl"], "%Y年%m月%d日").date()
                    except ValueError:
                        logger.info(f"Date {registration_ddl} can't be converted to.")
                        pass

                bidding_ddl = None
                if data.get("bidding_ddl", None):
                    try:
                        bidding_ddl = datetime.strptime(data["bidding_ddl"], "%Y年%m月%d日").date()
                    except ValueError:
                        logger.info(f"Date {bidding_ddl} can't be converted to.")
                        pass

                record = QianlimaBiddingDetailAbstract(
                    id=id_generator.generate(),
                    head_id=head_id,
                    project_number=data.get("project_number", None),
                    estimated_amount=data.get("estimated_amount", None),
                    bidding_org=data.get("bidding_org", None),
                    agency=data.get("agency", None),
                    registration_ddl=registration_ddl,
                    bidding_ddl=bidding_ddl,
                    type=data.get("type", None),
                    area=data.get("area", None),
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
                    logger.warning(f"Record already exists, skipping: {data['head_id']}")
                    continue

            return created_ids

        except Exception as e:
            self.session.rollback()
            raise Exception(f"An error occurred while creating the record: {e}")
        