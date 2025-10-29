import requests
import os

DOWNLOAD_URL = os.getenv('DOWNLOAD_URL')


def sanitize_filename(filename):
    """
    将文件名中的特殊字符转换为安全字符
    规则：
    - 冒号 ':' → 下划线 '_'
    - 空格 ' ' → 加号 '+'
    """
    result = filename.replace(':', '_').replace(' ', '+')
    return result

def add_sale_clue_crm(company_name, describe, phone_number, province, user_name, title):
    url = "http://172.30.3.80:32110/virtual/addSaleClue"
    
    payload = {
        "applicationArea": "",
        "city": "",
        "clueName": "招标网",
        "coUserId": "",
        "communicateMatter": 0,
        "companyName": company_name,
        "creatorId": "024661606726079850",
        "crmActivityId": "",
        "crmType": "",
        "describe": describe,
        "email": "",
        "files": [
            {
                "attachIndex": DOWNLOAD_URL + sanitize_filename(title) + ".pdf",
                "ext": "pdf",
                "filename": title
            }
        ],
        "isValid": 0,
        "phoneNumber": phone_number,
        "province": province,
        "referee": "招标网",
        "specificRequirements": "",
        "tags": [],
        "userName": user_name,
        "visitorId": ""
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        response.raise_for_status()
        
        return {
            'success': True,
            'status_code': response.status_code,
            'data': response.json() if response.content else None
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }