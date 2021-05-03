import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,callbackqueryhandler, ConversationHandler
import requests
from datetime import date
import os
import psycopg2
from dotenv import load_dotenv
from cowin import CoWinAPI
cowin = CoWinAPI()


load_dotenv()


ADD_LINK=range(1)
conn = psycopg2.connect(host=os.environ.get('db_host'),database=os.environ.get('db'), user=os.environ.get('db_user'), password=os.environ.get('db_password'))
cur = conn.cursor()
token=os.environ.get('telegram_key')
def find_vacine_places(pincode,today,age):
    try:
        r=cowin.get_availability_by_pincode(pincode,today)
        sessions=r['sessions']
        cont=""
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
        return cont
    except requests.exceptions.Timeout as e:
        print(e)
    except requests.exceptions.RequestException as e:
        print(e)

def find_vacine(update, context):
    today = date.today().strftime("%d-%m-%Y")
    pincode = context.args[0]
    res=find_vacine_places(pincode,today,45)
    update.message.reply_text(res)

def help(update, context):
    update.message.reply_text("/findvaccine Pincode ")

def insertuser(name,email,pincode,telegramid,age):
    try:
        cur.execute("INSERT INTO users (name,email,pincode,msg_sent,chat_id,age) VALUES ('%s','%s','%d',false,'%d','%d');" % (name,email,int(pincode),telegramid,int(age)) )
        conn.commit()
        return 'Sucess'
    except Exception as e:
        return e

def start(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def registerhandle(update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    kk= context.args
    if len(kk)==0:
        update.message.reply_text("Send as /register Pincode")
    context.user_data['pincode']=kk[0]
    bot.send_message(
            chat_id=chat_id,
            text="Enter name followed by email and age\n Eg: Kishore kishore@example.com 21"
    )
    return ADD_LINK

def register(update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    ove= (update.message.text).split(" ")
    name=""
    age=ove[-1]
    email=ove[len(ove)-2]
    for n in  range(len(ove)-2):
        name+=ove[n]+" "
    insertuser(name,email,context.user_data['pincode'],chat_id,age)
    bot.send_message(
            chat_id=chat_id,
            text="You have registered sucessfully."
    )
    return ConversationHandler.END

def reset_msg_sent():
    cur.execute("UPDATE users SET msg_sent = false;")
    conn.commit()

def check_vaccine_availability():
    cur.execute("SELECT * FROM users;")
    users=cur.fetchall()
    today = date.today().strftime("%d-%m-%Y")
    bot = telegram.Bot(token=token)
    for n in users:
        res=find_vacine_places(n[3],today,int(n[6]))
        if len(res)>10 and n[4]==False:
            bot.sendMessage(chat_id=n[5], text=res)
            cur.execute("UPDATE users SET msg_sent=true where user_id=%s"%n[0])
            conn.commit()

def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    registeration = ConversationHandler(
            entry_points=[
                CommandHandler("register",registerhandle)
            ],
            states={
                ADD_LINK: [
                    MessageHandler(Filters.text, register)
                ]
            },
            fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("findvaccine", find_vacine))
    dp.add_handler(registeration)
    #dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()