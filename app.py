from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
from datetime import date
import os

def find_vacine(update, context):
    today = date.today().strftime("%d-%m-%Y")
    pincode = context.args[0]
    r=requests.get(("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=%s&date=%s" % (pincode,today))).json()
    sessions=r['sessions']
    cont=""
    for n in sessions:
        kk=""
        cont+="Location: %s, District: %s, State: %s\n"%(n['name'],n['district_name'],n['state_name'])
        cont+="Vaccine: %s, Date: %s\n"%(n['vaccine'],n['date'])
        cont+="Available: %s, Type: %s, Fee: %s, MinAge: %s\n"%(n['available_capacity'],n['fee_type'],n['fee'],n['min_age_limit'])
        for m in n['slots']:
            kk+=m+", "
        cont+="Slots: "+kk+"\n"
        cont+="*********************************************\n"
    update.message.reply_text(cont)

def help(update, context):
    update.message.reply_text("/findvaccine Pincode")


def start(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(os.environ['telegramkey'], use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("findvaccine", find_vacine))
    #dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()