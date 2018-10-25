import json, traceback
import requests
import time
import urllib.parse as uparse
import config
from dbhelper import DBHelper
import datetime
from nbadaily import NSN
from nbastanding import NBAStanding as NSS
from telegram.ext import Updater
from telegram.ext import CommandHandler, Filters
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)




TOKEN = config.token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
RESULTS = ""
LAST_HOUR = 0

db = DBHelper()


def start():
    pass

def get():
    pass

def add_team():
    pass

def remove_team():
    pass

def standing():
    pass

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


def add_team(username,team):
    t = db.get_teams(username)
    if team not in t:
        db.add_team(username,team)


def prepare_message(username, results):
    teams = db.get_teams(username)
    if len(teams) > 0:
        res = ""
        res += "{}<br>".format(date_format(0))
        res += "<table>"
        for result in results:
            if result[0] in teams or result[2] in teams:
                res += "<tr><td>HOME</td><td>{}</td><td>{}</td></tr>".format(result[0], result[1])
                res += "<tr><td>AWAY</td><td>{}</td><td>{}</td></tr>".format(result[2], result[3])
                res += "<tr><td></td><td></td><td></td></tr>"
        res += "</table>"
        pass
    else:
        return "<b>NO FAVORITE TEAM</b>"

def get_username(update):
    chat_info = update["message"]["chat"]
    if chat_info["type"] == "private":
        return chat_info["username"]
    else:
        return chat_info["type"]


def handle_updates(updates):
    global RESULTS
    for update in updates["result"]:
        if "text" in update["message"].keys():
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            print("%s : %s"%(text,chat))
            if text.startswith("/get"):
                RESULTS = NSN().get()
                if len(set(RESULTS).difference(config.current_result)) > 0:
                    config.current_result = RESULTS
                send_message_h(prepare_message(get_username(update),RESULTS), chat)
            elif text == "/start":
                add_user(get_username(update),chat)
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
            elif text.startswith("/add"):
                t = text.split(' ')
                if len(t) != 2:
                    send_message("FALSE", chat)
                add_team(get_username(update),t[1].upper())
            else:
                send_message("FALSE", chat)


def send_message(text, chat_id, reply_markup=None):
    print("Sending : \n"+text)
    text = uparse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def send_message_h(text, chat_id, reply_markup=None):
    #print("Sending : \n"+text)
    #text = uparse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=html".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def send_all():
    users = db.get_users()
    for user in users:
        cid = user[1]
        send_message(date_format(0)+"\n"+config.current_result,cid)

def main_():
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



def start(bot, update, args,job_queue):
    pass

def get(bot, update, args):
    pass

def add_team():
    pass

def remove_team():
    pass

def standing():
    pass


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():

    updater = Updater(token=config.token)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start, pass_job_queue=True)
    get_handler = CommandHandler('get',get,pass_args=True)
    add_handler = CommandHandler('add',add_team,pass_args=True)
    remove_handler = CommandHandler('remove',remove_team,pass_args=True)
    standing_handler = CommandHandler('standing',standing,pass_args=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(get_handler)
    dispatcher.add_handler(add_handler)
    dispatcher.add_handler(remove_handler)
    dispatcher.add_handler(standing_handler)

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()
