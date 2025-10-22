import requests

def add_sale_clue_crm(company_name, describe, phone_number, province, user_name):
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