from json import dumps
import requests
import random

class RequestException(Exception):
        def __init__(self, text, code):
            self.txt = text
            self.code = code

class AccessDenied(Exception):
        def __init__(self):
            self.txt = 'VK API returns AccessDenied error.'


class VKEngine():

    token = None
    master = None
    ver = 5.82

    def __init__(self, token, master, ver=5.107):
        self.token = token
        self.master = master
        self.ver = ver

    def _req(self, method, **kwargs):
        r = requests.get('https://api.vk.com/method/' + method,
                         params={**kwargs, 'access_token': self.token, 'v':self.ver, 'lang':'ru'}).json()
        if 'error' in list(r):
            code = r['error']['error_code']
            description = r['error']['error_msg']
            if code == 15:
                raise AccessDenied()
            else:
                raise RequestException(f'VK API Returned an error code {code}: {description}', code)
        else:
            return r['response']

    def fetch_user(self, uid, **kwargs):
        data = self._req('users.get', user_ids=uid, **kwargs)
        if len(data) == 1:
            return data[0]
        return data

    def msg(self, uid, text, keyboard=None, attachments=None, conv=False):
        # print('to {}: {}'.format(uid, text))
        num = random.randint(0, 10000000000000000000000000)
        try:
            if keyboard:
                if conv:
                    self._req('messages.send', message=text, peer_id=uid, random_id=num, keyboard=dumps(keyboard))
                else:
                    self._req('messages.send', message=text, user_id=uid, random_id=num, keyboard=dumps(keyboard))
            else:
                if conv:
                    self._req('messages.send', message=text, peer_id=uid, random_id=num)
                else:
                    self._req('messages.send', message=text, user_id=uid, random_id=num)
                

        except RequestException as e:
            if e.code == 901:
                print('User blocked messages from the bot.')
                return None
            else:
                print('Something bad happened: '+e.txt)

    def report(self, text):
        self.msg(self.master, str(text))

    def send_uploaded(self, uid, fileid):
        self._req('messages.send', user_id=uid, attachment=fileid)

    def upload(self, uid, filepath):
        url = self._req('docs.getMessagesUploadServer', peer_id=uid)['upload_url']
        doc_id = requests.post(url, files={'file': open(filepath,'rb')}).json()
        r = self._req('docs.save', file=doc_id['file'])[0]
        owner_id, media_id = r['owner_id'], r['id']
        return f'doc{owner_id}_{media_id}'

    def get_short(self, link):
        obj = self._req('utils.getShortLink', url=link)
        return obj['short_url']
