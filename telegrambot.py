#! /usr/bin/python3
 
import telegram
import mysql.connector
import datetime
from datetime import date

bot = telegram.Bot(token = '954355522:AAFCJExvswk55znAmYREfc1alS-klYyn8Hk')
chatID = 283463734

mydb = mysql.connector.connect(host = "localhost", user = "admin", passwd = "nWd3cOhlXXGbV4i9V7yJ", database = "rapla")
mycursor = mydb.cursor()

cDate = date.today()
tom = cDate + datetime.timedelta(1)
tomrrw = datetime.datetime.combine(tom,datetime.datetime.min.time())
tom1 = cDate + datetime.timedelta(2)
tomrrw1 = datetime.datetime.combine(tom1,datetime.datetime.min.time())
mycursor.execute('SELECT * FROM teleport')
lastexec = mycursor.fetchall()[0][0]
print(cDate)
print(lastexec.date())

if cDate != lastexec:

	query = 'SELECT time_start FROM eventsG2 WHERE time_start >\"'+str(tomrrw)+'\" AND time_start<\"'+str(tomrrw1)+'\" ORDER BY `eventsG2`.`time_start` ASC'

	mycursor.execute(query)
	result = mycursor.fetchall()
	if len(result) > 0:

		firstt = result[0][0]
		print(str(firstt))
		wakeup = firstt - datetime.timedelta(minutes=15,hours=1)
		print(str(wakeup))
		bedtime = wakeup - datetime.timedelta(hours=8)
		print(bedtime)
		print(datetime.datetime.now())
		if datetime.datetime.now() >= bedtime:
			bot.send_message(chat_id = chatID, text = "Go to bed! yout have to get up tomorrow at "+str(wakeup.hour)+":"+str(wakeup.minute))
