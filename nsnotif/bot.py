import json, traceback
import requests
import time
import urllib.parse as uparse
import config
from dbhelper import DBHelper
import datetime
from nbadaily import NSN
from nbastanding import NBAStanding as NSS

TOKEN = config.token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
RESULTS = ""
LAST_HOUR = 0

db = DBHelper()


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def should_be_update_info_by_hour():
    global LAST_HOUR
    res = LAST_HOUR != datetime.datetime.now().hour
    if res:
        LAST_HOUR = datetime.datetime.now().hour
        return True
    return False


def should_be_update_info():
    if datetime.datetime.now().hour == 6:
        return True
    return False


def date_format(d):
    dd = datetime.datetime.now() - datetime.timedelta(d)
    return str(dd.year) + "-" + str(dd.month) + "-" + str(dd.day)


def add_user(username,cid):
    user = db.get_user(username)
    if not user:
        db.add_user(username, cid)


def handle_updates(updates):
    global RESULTS
    for update in updates["result"]:
        if "text" in update["message"].keys():
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            print("%s : %s"%(text,chat))
            if text.startswith("/get"):
                RESULTS = NSN().get()
                if config.current_result != RESULTS:
                    config.current_result = RESULTS
                send_message(date_format(0) + "\n" + RESULTS, chat)
            elif text == "/start":
                chat_info = update["message"]["chat"]
                if chat_info["type"] == "private":
                    add_user(chat_info["username"], chat)
                else:
                    add_user(chat_info["type"]+str(chat), chat)

                send_message("/get\tGet today's NBA scores!", chat)
                time.sleep(0.5)
                send_message(date_format(0) + "\n" + RESULTS, chat)
            elif text.startswith("/standing"):
                n = NSS()
                ts = text.split(' ')
                ll = len(ts)
                if ll == 1:
                    send_message(n.get_standings(), chat)
                elif ts[1].lower().startswith('w'):
                    send_message(n.get_standings("WEST"), chat)
                else:
                    send_message(n.get_standings("EAST"), chat)
            elif text == "/help":
                send_message("/get\tGet today's NBA scores!", chat)
            else:
                send_message("FALSE", chat)


def send_message(text, chat_id, reply_markup=None):
    print("Sending : \n"+text)
    text = uparse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def send_all():
    users = db.get_users()
    for user in users:
        cid = user[1]
        send_message(date_format(0)+"\n"+config.current_result,cid)

def main():
    global RESULTS
    db.setup()
    last_update_id = None
    while True:
        try:
            time.sleep(0.5)
            if should_be_update_info():
                RESULTS = NSN().get()
                if config.current_result != RESULTS:
                    config.current_result = RESULTS
                    send_all()
            updates = get_updates(last_update_id)
            if "result" in updates.keys() and len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
                handle_updates(updates)
            time.sleep(0.5)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            continue


if __name__ == '__main__':
    main()
