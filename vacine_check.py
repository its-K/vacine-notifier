import telegram
import requests
from datetime import date
import os
import psycopg2
import json
from dotenv import load_dotenv
from cowin import CoWinAPI
import sys

load_dotenv()

cowin = CoWinAPI()
conn = psycopg2.connect(host=os.environ.get('db_host'),database=os.environ.get('db'), user=os.environ.get('db_user'), password=os.environ.get('db_password'))
cur = conn.cursor()
token=os.environ.get('telegram_key')
def find_vacine_places(pincode,today,age,cont):
    try:
        r = cowin.get_availability_by_pincode(pincode,today)
        sessions=r['sessions']
        for n in sessions:
            if n['min_age_limit']<=age:
                kk=""
                cont+="Name: %s, District: %s, State: %s\n"%(n['name'],n['district_name'],n['state_name'])
                cont+="Vaccine: %s, Date: %s\n"%(n['vaccine'],n['date'])
                cont+="Available: %s, Type: %s, Fee: %s, MinAge: %s\n"%(n['available_capacity'],n['fee_type'],n['fee'],n['min_age_limit'])
                for m in n['slots']:
                    kk+=m+", "
                cont+="Slots: "+kk+"\n"
                cont+="*********************************************\n"
        cont+="Always Wear Mask"
        return cont
    except requests.exceptions.Timeout as e:
        print(e)
    except requests.exceptions.RequestException as e:
        print(e)

def check_vaccine_availability():
    cur.execute("SELECT * FROM users;")
    users=cur.fetchall()
    today = date.today().strftime("%d-%m-%Y")
    bot = telegram.Bot(token=token)
    for n in users:
        me="Hey "+n[1]+" 🎉 \nVacine Available 😊\n"
        res=find_vacine_places(n[3],today,int(n[6]),me)
        if len(res)>10 and n[5]==False:
            bot.sendMessage(chat_id=n[6], text=res)
            cur.execute("UPDATE users SET msg_sent=true where user_id=%s"%n[0])
            conn.commit()

def reset_msg_sent():
    cur.execute("UPDATE users SET msg_sent = false;")
    conn.commit()

if __name__ == '__main__':
    globals()[sys.argv[1]]()
