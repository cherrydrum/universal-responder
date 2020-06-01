from vk_api import VKEngine
import requests
import random

# Insert your credentials, including your VK ID
token = ""
masterid = None
vk = VKEngine(token, masterid)

def chew(text):
    filtered = '!,?;:<>()[]}{.'
    for symbol in filtered:
        if symbol in text:
            text = text.replace(symbol, '')
    return text

def process(text, uid, user, conversation=False):
    print(text)
    request = text.lower()
    request = chew(request)
    if request.endswith(' да') or request == 'да':
        vk.msg(uid, "пизда", conv=conversation)
    elif request.endswith(' пизда') or request == 'пизда':
        vk.msg(uid, "да", conv=conversation)
    elif not conversation:
        vk.msg(user, "ты думаешь мы тут шутки шутим? пошёл нахуй пидор грязный", conv=False)

data = vk._req('groups.getLongPollServer', group_id='195903845')
server, key, ts = data['server'], data['key'], data['ts']

while True:
    
    longpoll = requests.get(server, params={'act':'a_check', 'key': key, 'ts': ts, 'wait': 5}).json()
    ts = longpoll['ts']

    if not longpoll.get('updates'):
        continue

    updates = ( a['object'] for a in longpoll['updates'] if a['type'] == 'message_new' )

    for update in updates:
        update = update['message']
        uid = update.get('peer_id')
        user = update.get('from_id')
        text = update.get('text')
        if uid != user:
            process(text, uid, user, conversation=True)
        else:
            process(text, uid, user)