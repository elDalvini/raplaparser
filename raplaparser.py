#! /usr/bin/python3
# -*- coding: utf-8 -*-
#imports:
from __future__ import unicode_literals
import datetime
from datetime import date
from lxml import html
import requests
import locale
import mysql.connector

#mysql connection:
mydb = mysql.connector.connect(host = "localhost", user = "admin", passwd = "nWd3cOhlXXGbV4i9V7yJ", database = "rapla")
mycursor = mydb.cursor()
#get current date, week Number and set locale
cdate = date.today()-datetime.timedelta(days = 150)
cweek = cdate.isocalendar()[1]
cyear = cdate.year
locale.setlocale(locale.LC_ALL, 'de_DE')

mycursor.execute("TRUNCATE events")
mydb.commit()
sweek = cweek

for j in range(52):
    #count weeks up
    if sweek > 52:
        sweek = 1
        cyear += 1
    #selected Date (for year)
    sdate = datetime.datetime.strptime(str(cyear)+str(sweek)+'Mo', '%Y%W%a')
    # sdate = datetime.datetime(2019,9,30)
    # sweek = cweek
    if sdate > datetime.datetime(2019,9,15):
        #collect web page at current day
        url = 'https://rapla.dhbw-karlsruhe.de/rapla?key=ah9tAVphicaj4FqCtMVJcq5B-fx3fL5vC8Yzp3fNoXCp74P5CA7v840yvix-0x4j&day='+str(sdate.day)+'&month='+str(sdate.month)+'&year='+str(sdate.year)
        page = requests.get(url)
        tree = html.fromstring(page.content)

        #Times and titles:
        Titles = tree.xpath('//a[@href != 0]/span/table/tr[1]/td[2]/text()')
        #Times and days:
        Days = tree.xpath('//a[@href != 0]/span/div[2]/text()')
        #class and rooms:
        #Rooms = tree.xpath('//span[not(contains(,TMT18B1))]/text()')
        #print(Titles)
        # print(Days)
        #print(Rooms)
        i = 0
        for i in range(0,len(Titles)):
            #print(i)
            #print(Titles[i])
            room = tree.xpath('''//span[contains(.,'%s') and contains(.,'%s')]/table/tr[contains(.,"Ressourcen:")]/td[2]/text()''' %(str(Days[i]),str(Titles[i])))
            dozent = tree.xpath('''//span[contains(.,'%s') and contains(.,'%s')]/table/tr[contains(.,"Personen:")]/td[2]/text()''' %(str(Days[i]),str(Titles[i])))
            #current absolute values:
            ttitle = Titles[i]
            if len(dozent) > 0:
                tdozent = dozent[0]
            else:
                tdozent = "Kein Dozent"
                
            tdatestring = Days[i]
            splitstring = tdatestring.split(' ')
            tday = splitstring[0]
            for l in range(1,len(splitstring)):
                if splitstring[l].find("-") != -1:
                    splittime = splitstring[l].split('-')
                    tstarttime = splittime[0]
                    tendtime = splittime[1]

            startstr = tday+'-'+str(sdate.year)+'-'+str(sweek)+'-'+tstarttime
            stopstr = tday+'-'+str(sdate.year)+'-'+str(sweek)+'-'+tendtime
            try:
             tstartdatetime = datetime.datetime.strptime(startstr,'%a-%Y-%W-%H:%M')
             tstopdatetime = datetime.datetime.strptime(stopstr,'%a-%Y-%W-%H:%M')
            except:
             print('Error in time reading')
             continue

            room_av = 0
            if len(room) == 1:
                splitroom = room[0].split(',')
                for k in range(0,len(splitroom)):
                    if (splitroom[k].find('TMT18B')) == -1: 
                        if room_av == 1:
                            troom = [troom,splitroom[k]]
                        else:
                            troom = splitroom[k]
                            room_av = 1
                    if room_av == 0:
                        troom = "Kein Raum"
            elif len(room) == 0:
                troom = "Kein Raum"
            else:
                troom = "Raum nicht lesbar"
                roomcond = tree.xpath('''//span[contains(.,'%s') and contains(.,'%s')]/table/tr[contains(.,"Ressourcen:")]/td[2]/small/text()''' %(str(Days[i]),str(Titles[i])))
                for i in range(0,len(roomcond)):
                    if (roomcond[i].find(str(tstartdatetime.day)+"."+tstartdatetime.strftime("%m")) != -1 ):
                        splitroom = room[i].split(',')
                        for k in range(0,len(splitroom)):
                            if (splitroom[k].find('TMT18B')) == -1: 
                                if room_av == 1:
                                    troom = [troom,splitroom[k]]
                                else:
                                    troom = splitroom[k]
                                    room_av = 1
                            if room_av == 0:
                                troom = "Kein Raum"
                

            mycursor.execute('INSERT INTO events (title, reader, time_start, time_end, room, url, year, week, day, startstr, stopstr) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(str(ttitle), str(tdozent), str(tstartdatetime), str(tstopdatetime), str(troom), str(url), str(sdate.year), str(sweek), str(tday), str(startstr), str(stopstr)))
        mydb.commit()
    sweek += 1
