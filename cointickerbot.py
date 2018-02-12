import requests
import websocket
import json
from datetime import datetime

currency_term = {
    'btc': ['비트코인', '빗코', '비코'],
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

    if not message['text'].startswith("코인원"):
        return

    currency = message["text"].split()
    

    if len(currency) < 2:
        return

    
    mult = currency[2] if len(currency) > 2 else None
    currency = currency[1]
    for coin_symbol, coin_nick in currency_term.items():
        currency = coin_symbol if currency in coin_nick else currency
    
    coin_url = "https://api.coinone.co.kr/ticker/?currency={}".format(currency)
    coin_response = requests.get(coin_url)
    
    response_dict = json.loads(coin_response.text)
    last = response_dict.get('last', None)

    return_message = '요청하신 값이 없습니다.'
    if last:
        time_stamp = datetime.fromtimestamp(int(response_dict.get('timestamp')))
        return_message = "{} 기준 가격 *KRW {:,}*".format(time_stamp.strftime('%Y-%m-%d %H:%M:%S'), int(last))
        print(mult)
        print(mult.isnumeric())
    if mult.isnumeric():
        return_message += " {}개 *KRW {:,}*".format(mult, int(last) * int(mult))

    return_msg = {
        'channel': message['channel'],
        'type': 'message',
        'text': return_message
    }
    ws.send(json.dumps(return_msg))

token = 'xoxb-313486660738-9LIyL7qpxeBBemsxXsWpeXfM'
get_url = requests.get('https://slack.com/api/rtm.connect?token=' + token)
socket_endpoint = get_url.json()['url']

websocket.enableTrace(True)
ws = websocket.WebSocketApp(socket_endpoint, on_message=on_message)
ws.run_forever()
