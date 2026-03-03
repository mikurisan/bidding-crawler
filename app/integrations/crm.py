import requests


def add_sale_clue_crm(company_name, describe, phone_number, province, user_name, file_url, file_name):
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
                "attachIndex": file_url,
                "ext": "pdf",
                "filename": file_name
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
        response.raise_for_status()   # 保留，避免出现网络异常却误判为成功
        resp_json = response.json()
    except requests.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }

    data_msg = resp_json.get('data')
    if data_msg == "客户已分配成功":
        return {
            'success': True,
            'status_code': response.status_code,
            'data': data_msg
        }
    else:
        return {
            'success': False,
            'status_code': response.status_code,
            'error': data_msg  # 或者放到 data 中，看你的接口约定
        }