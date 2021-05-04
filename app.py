from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
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

def find_vaccine_places_pin(pincode,today):
    try:
        r=cowin.get_availability_by_pincode(pincode,today)
        sessions=r['sessions']
        cont=""
        for n in sessions:
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

def find_vaccine_places_week(pincode,today):
    try:
        r=cowin.get_availability_by_pincode_week(pincode,today)
        sessions=r['centers']
        cont=""
        for n in sessions: 
            cont+="Name: %s, District: %s, State: %s\n"%(n['name'],n['district_name'],n['state_name'])
            cont+="Available slots:\n"
            for p in n['sessions']:
                kk=""
                cont+="\nDate: %s, Vaccine: %s\n"%(p['date'],p['vaccine'])
                cont+="Available: %s, Type: %s, MinAge: %s\n"%(p['available_capacity'],n['fee_type'],p['min_age_limit'])
                for m in p['slots']:
                    kk+=m+", "
                cont+="Slots: "+kk+"\n"
            cont+="*********************************************\n"
        cont+="Always Wear Mask"
        return cont
    except requests.exceptions.Timeout as e:
        print(e)
    except requests.exceptions.RequestException as e:
        print(e)

def find_vaccine(update, context):
    today = date.today().strftime("%d-%m-%Y")
    if context.args:
        pincode = context.args[0]
        res=find_vaccine_places_pin(pincode,today)
        if len(res)>20:
            update.message.reply_text(res)
        else:
            update.message.reply_text("No slots found")
    else:
        update.message.reply_text("Incorrect pincode\n eg: /findvaccine 642122")

def find_vaccine_week(update, context):
    today = date.today().strftime("%d-%m-%Y")
    if context.args:
        pincode = context.args[0]
        res=find_vaccine_places_week(pincode,today)
        if len(res)>20:
            update.message.reply_text(res)
        else:
            update.message.reply_text("No slots found")
    else:
        update.message.reply_text("Incorrect pincode\n eg: /findvaccineweek 642122")

def help(update, context):
    update.message.reply_text("/findvaccine Pincode -gets vacine availability details\n/register Pincode -register for notification when vacine available\n/findvaccineweek Pincode -gets vacine availability details for a week\n/unregister - Unregister for vacine availabilty notifications\n/status - Know your registeration status\n/info - About")

def check_user(chat_id):
    cur.execute("select * from users where chat_id=%d"%chat_id)
    users=cur.fetchall()
    conn.commit()
    if users:
        return True
    return False

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

def status(update,context):
    chat_id = update.message.chat.id
    if check_user(chat_id):
        update.message.reply_text("Hurray 🎉\nYou are registered for notifications")
    else:
        update.message.reply_text("Oops ! You are not registered for notifications\nTo register /register")

def bot_info(update,context):
    update.message.reply_text("This Bot is created and maintained by Kishore 😎\nTo fork this project visit https://github.com/its-K/vacine-notifier .")

def registerhandle(update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    kk= context.args
    if len(kk)==0:
        update.message.reply_text("Send as /register Pincode")
    else:
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
    if len(ove)>=3:
        name=""
        age=ove[-1]
        email=ove[len(ove)-2]
        for n in  range(len(ove)-2):
            name+=ove[n]+" "
        if not check_user(chat_id):
            insertuser(name,email,context.user_data['pincode'],chat_id,age)
            bot.send_message(
                    chat_id=chat_id,
                    text="You have registered sucessfully."
            )
        else:
            bot.send_message(
                    chat_id=chat_id,
                    text="You have already registered."
            )
        return ConversationHandler.END
    else:
        bot.send_message(
                    chat_id=chat_id,
                    text="Incorrect format.\n Eg: Kishore kishore@example.com 21"
            )

def unregister(update, context):
    chat_id = update.message.chat.id
    if check_user(chat_id):
        cur.execute("Delete from users where chat_id=%d"%chat_id)
        conn.commit()
        update.message.reply_text("You have unregistered for notifications")
    else:
        update.message.reply_text("You are not registered.")

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
    dp.add_handler(CommandHandler("findvaccine", find_vaccine))
    dp.add_handler(CommandHandler("unregister", unregister))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("info", bot_info))
    dp.add_handler(CommandHandler("findvaccineweek", find_vaccine_week))
    dp.add_handler(registeration)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()