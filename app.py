from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import os
import json


class LineBot:
    def __init__(self, secret = None, token = None):
        self.secret = secret
        self.token = token
        self.init()

    def init(self):
        self.line_bot_api = LineBotApi(self.token)
        self.handler = WebhookHandler(self.secret)
        @self.handler.add(MessageEvent, message=TextMessage)
        def handle_message(event):
            msg = event.message.text
            message = TextSendMessage(text=msg)
            # self.line_bot_api.reply_message(event.reply_token, message)

        @self.handler.add(PostbackEvent)
        def handle_message(event):
            print(event.postback.data)


        @self.handler.add(MemberJoinedEvent)
        def welcome(event):
            uid = event.joined.members[0].user_id
            gid = event.source.group_id
            profile = self.line_bot_api.get_group_member_profile(gid, uid)
            name = profile.display_name
            message = TextSendMessage(text=f'{name}歡迎加入')
            self.line_bot_api.reply_message(event.reply_token, message)
    
    def Broadcast(self, str):
        self.line_bot_api.broadcast(TextSendMessage(text=str))

    def ReplyMsg(self, token, str):
        message = TextSendMessage(text=str)
        self.line_bot_api.reply_message(token, message)
        

class LineService:
    def __init__(self, host = '0.0.0.0', port = 5123, secret = None, token = None):
        self.psw = "!@34001?>f!&&"
        self.host = host
        self.port = int(os.environ.get('PORT', 5123))
        self.bot = LineBot(secret, token)

        self.app = Flask(__name__)
        self.app.add_url_rule("/check", methods=['POST'], view_func= self.check) 
        self.app.add_url_rule("/callback", methods=['POST'], view_func= self.callback) 
        self.app.add_url_rule("/action", methods=['POST'], view_func= self.Action)

        self.actions = {
            "broadcast": self.Broadcast
        }
        

    def check(self):
        text = 'check ok!'
        # self.Broadcast(text)
        return text

    def callback(self):
            # get X-Line-Signature header value
            signature = request.headers['X-Line-Signature']
            # get request body as text
            body = request.get_data(as_text=True)
            self.app.logger.info("Request body: " + body)
            # handle webhook body
            try:
                self.handler.handle(body, signature)
            except InvalidSignatureError:
                abort(400)
            return 'OK'

    def Run(self):
        self.app.run(self.host, self.port)

    def Broadcast(self, text):
        self.bot.Broadcast(text)

    def SendMsg(self, token, text):
        self.bot.ReplyMsg(token, text)

    def Action(self):
        try:
            data = request.data
            obj = json.loads(data)
            print(obj)
            psw = obj["psw"]
            key = obj["key"]
            if self.isAllow(psw) is True:
                if self.actions.get(key) is not None:
                    self.actions[key](obj["value"])
                    print(obj)
            else:
                print("action not Allow!")
            return "ok"
        except:
            print("action except!")
            return "error!"

    def isAllow(self, psw):
        return psw == self.psw


if __name__ == "__main__":
    service = LineService('0.0.0.0', 
        5123,
        'bec7bce0790c54d7d31bc341ef4b89e2',
        'OP7yCzNCTuMaQ7aUDcKHbXLAjGGXdsNHfIWyylxURVytJ0Ych7wUFxQ5AP+/Q6A+7W6lpqF9gb4wf+yPqImfjq8E/kt/C+Cedtv9w7OU3V3jX66r0s/2wse8vWkeSbtLLJHf5nWJaHGXptMrPhe+ZAdB04t89/1O/w1cDnyilFU=')
    service.Run()

