import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

conn = mysql.connector.connect(host=os.environ.get('db_host'),
                                          database=os.environ.get('db'),
                                          user=os.environ.get('db_user'),
                                          password=os.environ.get('db_password'))
cur = conn.cursor()
cur.execute("select * from users;")
users=cur.fetchall()
conn.commit()
for n in users:
    print(n)