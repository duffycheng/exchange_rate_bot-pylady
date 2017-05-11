# encoding: utf-8
import time, os, traceback, requests, subprocess
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage 
)

LINE_BOT_SECRET = ''
LINE_BOT_TOKEN = ''

app = Flask(__name__)
handler = WebhookHandler(LINE_BOT_SECRET)
line_bot_api = LineBotApi(LINE_BOT_TOKEN) 

def multicast_to_user(users, msg):
    line_bot_api.multicast(users, TextSendMessage(text=msg))

from MyLineBot import MyLineBot
bot = MyLineBot({'push_callback': multicast_to_user})

@app.route('/')
def index():
    body = "<table border='1' style='text-align:center;'><tr><td style='padding:5px;width:210px;'>table update at</td><td style='padding:5px;'>" + str(bot.get_table_update_timestamp()) + \
    "</td></tr><tr><td style='padding:5px;'>exchange_rate_table</td><td style='padding:5px;'>" + str(bot.get_exchange_rate_table()) + \
    "</td></tr><tr><td style='padding:5px;'>notify_list</td><td style='padding:5px;'>" + str(bot.get_notify_list()) + \
    "</td></tr><tr><td style='padding:5px;'>force update table now</td><td style='padding:5px;'>" + \
    "<button style='margin:20px;' onclick='xhttp = new XMLHttpRequest();xhttp.open(\"GET\", \"/update-exchange-rate-table/now\", true);xhttp.send();'>Update Now</button></td></tr></table>"
    return body

@app.route('/update-exchange-rate-table/now')
def update_exchange_rate_table_now():
    bot.update_exchange_rate_table()
    return 'ok'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except LineBotApiError as e:
        abort(500)
    except Exception as e:
        traceback.print_exc()
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):        
    # line bot server check
    if event.reply_token == '00000000000000000000000000000000':
        return 'ok'
    if event.message.text == 'myid':
        message = event.source.user_id
    else:
        message = bot.parse_message(event.source.user_id, event.message.text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

if __name__ == "__main__":
    subprocess.Popen(['python3', 'crontab_job.py'])
    app.run(host='0.0.0.0',port=os.environ['PORT'])
    