import os
import requests
import websocket
import json
from datetime import datetime

currency_term = {
    'btc': ['비트코인', '빗코', '비코', '비트'],
    'eth': ['이더', '이더리움'],
    'bch': ["빗캐", "비트코인캐시", "비캐"], 
    'etc': ["이클", "이더리움클래식"], 
    'xrp': ["리플"], 
    'qtum': ["퀀텀", "큐텀"], 
    'iota': ["아이오타"], 
    'ltc': ["라코", "라이트코인"], 
    'btg': ["빗골", "비트코인골드"] 
}

def on_message(ws, message):
    message = json.loads(message)
    if 'type' in message.keys() and message['type'] != 'message':
        return 

    # 첫 단어가 '코인원'이어야 함
    if not message['text'].startswith("코인원"):
        return

    currency = message["text"].split()
    # 이 코드로 '코인원' 만 입력했을 때에는 답하지 않는다.
    if len(currency) < 2:
        return

    # 코인이름 뒤에 개수(숫자) 입력시 mult에 저장
    mult = currency[2] if len(currency) > 2 else None

    # 코인이름 저장
    currency = currency[1]

    # 코인이름으로 coin_symbol을 판별, currency에 저장한다.
    for coin_symbol, coin_nick in currency_term.items():
        currency = coin_symbol if currency in coin_nick else currency
    
    # Ticker
    coin_url = "https://api.coinone.co.kr/ticker/?currency={}".format(currency)
    coin_response = requests.get(coin_url)
    
    # 응답 status code가 200 (OK)가 아닐 시 다른 메시지로 응답
    if coin_response.status_code != 200:
        return_message = "현재 통신이 원활하지 않습니다. 아마 점검중일지도? https://coinone.co.kr/"
    else:
        # 응답 status code가 200(OK)일 때
        response_dict = json.loads(coin_response.text)
        last = response_dict.get('last', None)
        return_message = '요청하신 값이 없습니다.'

        # coin symbol이 정상적이지 않으면 last에 값이 들어오지 않는다.
        if last:
            time_stamp = datetime.fromtimestamp(int(response_dict.get('timestamp')))
            return_message = "{} 기준 가격 *KRW {:,}*".format(time_stamp.strftime('%Y-%m-%d %H:%M:%S'), int(last))

        # 코인 개수 있을경우
        if mult and mult.isnumeric():
            return_message += " {}개 *KRW {:,}*".format(mult, int(last) * int(mult))

    # 메시지 구성
    return_msg = {
        'channel': message['channel'],
        'type': 'message',
        'text': return_message
    }

    # 메시지 전송
    ws.send(json.dumps(return_msg))
