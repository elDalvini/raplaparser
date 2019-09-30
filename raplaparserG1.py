#! /usr/bin/python3

#imports:
import datetime
from datetime import date
from lxml import html
import requests
import locale
import mysql.connector

#mysql connection:
mydb = mysql.connector.connect(host = "localhost", user = "admin", passwd = "nWd3cOhlXXGbV4i9V7yJ", database = "rapla")
mycursor = mydb.cursor()
#get currant date, week Number and set locale
cdate = date.today()-datetime.timedelta(days = 150)
cweek = cdate.isocalendar()[1]
cyear = cdate.year
locale.setlocale(locale.LC_ALL, 'de_DE')

mycursor.execute("TRUNCATE eventsG1")
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
        page = requests.get('https://rapla.dhbw-karlsruhe.de/rapla?key=ah9tAVphicaj4FqCtMVJck1IPTyWNL7sCUaIN7ywI1HrATh0wE9uofal7KGMWCF4&day='+str(sdate.day)+'&month='+str(sdate.month)+'&year='+str(sdate.year))
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
            if Titles[i].find("Gruppe 2") == -1:
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
                
                room_av = 0
                if len(room) > 0:
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
                else:
                    troom = "Kein Raum"
                
                tdatestring = Days[i]
                splitstring = tdatestring.split(' ')
                tday = splitstring[0]
                for l in range(1,len(splitstring)):
                    if splitstring[l].find("-") != -1:
                        splittime = splitstring[l].split('-')
                        tstarttime = splittime[0]
                        tendtime = splittime[1]
                tstartdatetime = datetime.datetime.strptime(tday+str(sdate.year)+str(sweek)+tstarttime,'%a%Y%W%H:%M')
                tstopdatetime = datetime.datetime.strptime(tday+str(sdate.year)+str(sweek)+tendtime,'%a%Y%W%H:%M')
                mycursor.execute('INSERT INTO eventsG1 (title, reader, time_start, time_end, room) VALUES (%s,%s,%s,%s,%s)',(str(ttitle), str(tdozent), str(tstartdatetime), str(tstopdatetime), str(troom)))
        mydb.commit()
    sweek += 1
