from typing import List
from datetime import datetime
from app.models import  QianlimaBiddingDetailContact
from sqlalchemy.exc import IntegrityError
from app.db import id_generator
from .base import BaseRepository
import json
import logging

logger = logging.getLogger(__name__)
        
class QianlimaBiddingDetailContactRepository(BaseRepository):
    def create_records_from_json(
        self, json_str: str, head_id: int
    ) -> List[QianlimaBiddingDetailContact]:
        try:
            data_list = json.loads(json_str)
            created_ids = []

            for data in data_list:
                if data.get("error"):
                    return created_ids

                record = QianlimaBiddingDetailContact(
                    id=id_generator.generate(),
                    head_id=head_id,
                    name=data.get("name", None),
                    telphone=data.get("telphone", None),
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