from .models import *
from datetime import datetime, timezone,timedelta
import random

def read_card(order_id):
    card_datas = {}
    card = Card.objects.filter(order_id=order_id)[0]
    card_datas['name'] = card.package.description
    card_datas['offered_days'] = card.package.offered_days
    card_datas['package_price'] = card.package.package_price
    card_datas['order_id'] = order_id
    if card.coupon is not None:
        card_datas['coupon'] = 'True'
        card_datas['coupon_code'] = card.coupon.name
        card_datas['percentage'] = card.coupon.percentage
        card_datas['discount_price'] = int(card.package.package_price * card.coupon.percentage / 100)
        card_datas['total_order_value']  = str(int(card.package.package_price - card.package.package_price * card.coupon.percentage / 100))
    else:
        card_datas['total_order_value'] = str(int(card.package.package_price))

    #shopier
    card_datas['buyer_name'] = card.main_user.first_name
    card_datas['buyer_surname'] = card.main_user.last_name
    card_datas['buyer_email'] = card.main_user.email
    card_datas['callback'] = 'https://socinsta.com/payment/callback/'
    card_datas['API_key'] = 'ace799f66843eb449cd0712466cbc3b3'
    card_datas['product_type'] = '0'
    card_datas['currency'] = '0'
    card_datas['platform'] = '0'
    card_datas['billing_city']= 'istanbul'
    card_datas['billing_country'] = 'turkey'
    card_datas['shipping_city']= 'istanbul'
    card_datas['shipping_country'] = 'turkey'
    card_datas['platform_order_id'] = str(order_id)
    card_datas['random_nr'] = str(random.randint(100000, 999999))
    card_datas['signature'] = create_signature(card_datas['random_nr'],card_datas['platform_order_id'],card_datas['total_order_value'],card_datas['currency'])
    card.signature = card_datas['signature']
    card.updated_time= datetime.now(timezone.utc)
    card.save()
    return card_datas


def create_signature(random_nr,order_id,total_order_value,currency):
    import hmac,hashlib
    import random
    import base64
    import binascii
    secret_key='4a3e4f80d26bc64c45d0a435d4e8888e'

    data = str(random_nr) + str(order_id)+ str(total_order_value)+ str(currency)
    message = bytes(data, 'utf-8')
    secret = bytes(secret_key, 'utf-8')

    signature_raw = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
    signature = str(signature_raw,'utf-8')
    return signature
