from app.repositories import QianlimaBiddingDetailHeadRepository
from app.integrations import add_sale_clue_crm
from app.repositories import QianlimaBiddingDetailsToCrmRepository
from datetime import datetime
import json

async def push_to_crm():
    with QianlimaBiddingDetailHeadRepository() as r:
        results = r.get_bidding_details()
    
    for clue in results:
        response = add_sale_clue_crm(
            company_name=clue.bidding_org,
            describe=clue.content,
            phone_number=clue.telphone,
            province=clue.area,
            user_name=clue.name
        )

        if response["success"]:
            with QianlimaBiddingDetailsToCrmRepository() as repo:
                record_id = repo.create_from_bidding_detail(clue)

            data = {
                'timestamp': datetime.now().isoformat(),
                'content': record_id
            }
            json_data = json.dumps(data, ensure_ascii=False)
            yield f"event: push_to_crm\ndata: {json_data}\n\n"
        else:
            data = {
                'timestamp': datetime.now().isoformat(),
                'content': False
            }
            json_data = json.dumps(data, ensure_ascii=False)
            yield f"event: push_to_crm\ndata: {json_data}\n\n"