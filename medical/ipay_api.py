import hashlib
import hmac

import requests
import base64
from datetime import datetime, timezone


class IPay:
    _secret_key = "we dont have one :)"
    _vendor_id = "we also dont have this one"

    def __new__(cls, business_name=None, auth=False, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(IPay, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def generate_hash(key, msg):
        return hmac.new(key=key.encode('utf-8'),
                        msg=msg.encode('utf-8'),
                        digestmod=hashlib.sha256).hexdigest()

    def request_payment(self, amount, phone_number, account_reference, email, currency="USD"):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'x-www-form-urlencoded',
        }
        callback_url = "https://domain.com/callback"
        hash = self.generate_hash(key=self._secret_key,
                                  msg=f'{account_reference}.{account_reference}.{amount}.'
                                      f'{phone_number}.{email}.{self._vendor_id}.{currency}.'
                                      f'{callback_url}')
        data = {
            "oid": account_reference,
            "inv": account_reference,
            "amount": int(amount),
            "tel": phone_number,
            "eml": email,
            "vid": self._vendor_id,
            "curr": currency,
            "cbk": callback_url,
            "hash": hash,
        }
        response = requests.post(url='https://apis.ipayafrica.com/payments/v2/transact',
                                 headers=headers, data=data)
        print("response: ", response.text)
        if response.status_code != 200:
            raise Exception(response.text)

        data = response.json()
        sid = data.get('sid')
        hash = self.generate_hash(key='demoCHANGED', msg=f'{sid}.{self._vendor_id}')
        data = {
            "vid": self._vendor_id,
            "sid": sid,
            "hash": hash
        }
        response = requests.post(url='https://apis.ipayafrica.com/payments/v2/transact/mobilemoney',
                                 headers=headers, data=data)

        if response.status_code == 200:
            data = response.json()
            return data

        raise Exception(response.text)

    def verify_payment(self, order_id, ivm, qwh, afd, poi, uyt, ifd):
        url = f"https://www.ipayafrica.com/ipn/?vendor={self._vendor_id}&id={order_id}&ivm={ivm}" \
              f"&qwh={qwh}&afd={afd}&poi={poi}&uyt={uyt}&ifd={ifd}"

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'x-www-form-urlencoded',
        }

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data

        raise Exception(response.text)