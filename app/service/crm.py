from app.repositories import QianlimaBiddingDetailHeadRepository
from app.integrations import add_sale_clue_crm, upload_to_ali_oss
from app.repositories import QianlimaBiddingDetailsToCrmRepository
from datetime import datetime
from urllib.parse import quote

import json
import os


DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')
DOWNLOAD_URL = os.getenv('DOWNLOAD_URL')

def sanitize_filename(filename):
    """
    将文件名中的特殊字符转换为安全字符
    规则：
    - 冒号 ':' → 下划线 '_'
    - 空格 ' ' → 加号 '+'
    """
    result = filename.replace(':', '_').replace(' ', '+').replace('/', '_')
    return result

async def push_to_crm():
    with QianlimaBiddingDetailHeadRepository() as r:
        results = r.get_bidding_details()
    
    for clue in results:

        file_name = sanitize_filename(clue.title) + ".pdf"
        print(f"title: {clue.title} file_name: {file_name}")
        file_path = DOWNLOAD_DIR + file_name

        if not upload_to_ali_oss(file_path, file_name):
            return
        
        file_url = DOWNLOAD_URL + quote(file_name, safe='')
        yield f"event: upload_to_ali_oss\ndata: {file_url}\n\n"

        response = add_sale_clue_crm(
            company_name=clue.bidding_org,
            describe=clue.content,
            phone_number=clue.telphone,
            province=clue.area,
            user_name=clue.name,
            file_url=file_url,
            file_name=file_name
        )

        if response["success"]:
            with QianlimaBiddingDetailsToCrmRepository() as repo:
                record_id = repo.create_from_bidding_detail(clue)

            data = {
                "timestamp": datetime.now().isoformat(),
                "content": record_id
            }
            json_data = json.dumps(data, ensure_ascii=False)
            yield f"event: push_to_crm\ndata: {json_data}\n\n"
        else:
            data = {
                "timestamp": datetime.now().isoformat(),
                "content": response["error"]
            }
            json_data = json.dumps(data, ensure_ascii=False)
            yield f"event: push_to_crm\ndata: {json_data}\n\n"