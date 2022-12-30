import requests
import base64
from datetime import datetime, timezone


class SafariCom:
    _access_token = ""
    _business_short_code = "174379"
    _pass_key = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

    def __new__(cls, business_name=None, auth=False, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SafariCom, cls).__new__(cls)
        return cls.instance

    def __init__(self, auth=False, **kwargs):
        if auth is True:
            SafariCom.login()
        super(SafariCom, self).__init__()

    @staticmethod
    def login():
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Basic cFJZcjZ6anEwaThMMXp6d1FETUxwWkIzeVBDa2hNc2M6UmYyMkJmWm9nMHFRR2xWOQ=='
        }

        response = requests.get(url='https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
                                headers=headers)
        print(response.text.encode('utf8'))
        print("response: ", response.text)
        if response.status_code == 200:
            data = response.json()
            SafariCom._access_token = data.get('access_token')
            return

        raise Exception(response.text)

    def m_pesa_payment(self, amount, phone_number, account_reference):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._access_token
        }
        now = datetime.now(tz=timezone.utc)
        timestamp = f'{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}'
        password = self._business_short_code + self._pass_key + str(timestamp)
        encoded_password = password.encode("ascii")
        base64_bytes = base64.b64encode(encoded_password)
        base64_password = base64_bytes.decode("ascii")

        print(f"Encoded string: {base64_password}")
        json = {
            "BusinessShortCode": self._business_short_code,
            "Password": base64_password,
            "Timestamp": str(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self._business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://domain.com/callback",
            "AccountReference": account_reference,
            "TransactionDesc": "repay loan"
        }
        print('requests')
        response = requests.post(url='https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
                                 headers=headers, json=json)
        print("response: ", response.text)
        if response.status_code == 200:
            data = response.json()
            return data

        raise Exception(response.text)
