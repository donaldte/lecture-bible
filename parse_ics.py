from datetime import datetime, timedelta, timezone,date
import icalendar
from dateutil.rrule import *
import locale
import sqlite3

#Connexion base de données
conn= sqlite3.connect('bibleunanv2.db')
cursor=conn.cursor()


def import_books():
    books_fr=[]
    with open('files/books_fr.csv','r') as f:
        for line in f:
            line_sp=line.strip().split(';')
            name_fr=line_sp[0]
            name_en=line_sp[1]
            books_fr.append((name_fr,name_en))
    cursor.executemany('INSERT INTO book_fr VALUES(?,?)',books_fr)
    conn.commit()            
def parse_recurrences(recur_rule, start, exclusions):
    """ Find all reoccuring events """
    rules = rruleset()
    first_rule = rrulestr(recur_rule, dtstart=start)
    rules.rrule(first_rule)
    if not isinstance(exclusions, list):
        exclusions = [exclusions]
        for xdate in exclusions:
            try:
                rules.exdate(xdate.dts[0].dt)
            except AttributeError:
                pass
    now = datetime.now(timezone.utc)
    this_year = now + timedelta(days=60)
    dates = []
    for rule in rules.between(now, this_year):
        dates.append(rule.strftime("%D %H:%M UTC "))
    return dates

class Plan:
    def __init__(self,date,lecture_soir,nb_annee=1,rang_annee=1):
        self.date=date
        self.lecture_soir=lecture_soir
        self.nb_annee=nb_annee
        self.rang_annee=rang_annee

    def __str__(sel):
        return str(self.date)

def get_plan_from_ics():
    locale.setlocale(locale.LC_TIME,'fr_FR')
    icalfile = open('plan-3ans.ics', 'rb')
    gcal = icalendar.Calendar.from_ical(icalfile.read())
    increment=0
    year_rank=1
    list_plan=[]
    for component in gcal.walk():
        if component.name == "VEVENT":
            increment+=1
            if(increment)<=366:
                year_rank = 1
            elif(increment>366 and increment<=732):
                year_rank = 2
            else:
                year_rank = 3

            summary = component.get('summary')
            startdt = component.get('dtstart').dt
            jour=startdt.strftime('%d')
            mois=startdt.strftime('%B')
            jour_mois=jour+' '+mois

            plan=Plan(startdt,summary)
            list_plan.append(plan)
            
            # print("{}|{}|{}|{}".format(increment,jour_mois,summary,year_rank))
    icalfile.close()
    return list_plan

class Planfinal:
    object_rank=0
    def __init__(self,date,lecture_soir,nb_annee=3,rang_annee=1):
        self.date=date
        self.lecture_soir=lecture_soir
        self.nb_annee=nb_annee
        self.rang_annee=rang_annee

    def __str__(self):
        return str(self.date)

def get_current_year_rank(index):
    if index<=365:
        current_year_rank=1
    elif(index>365 and index<=730):
        current_year_rank=2
    else:
        current_year_rank=3

    return current_year_rank

def generate_3_years():
    """ Générer 3ans * 365 jours, donc 1095 jours """
    day_start=date(2020,12,31)
    list_plan_final=[]
    for i in range(1,1096):
        the_date=day_start+timedelta(days=i)
        plan_final = Planfinal(the_date,None)
        plan_final.rang_annee=get_current_year_rank(i)
        Planfinal.object_rank+=1
        plan_final.object_rank=Planfinal.object_rank
        list_plan_final.append(plan_final)
    return list_plan_final

lp=get_plan_from_ics()
list_plan_final=generate_3_years()

list_date_lecture_ok=[]
for plan in lp:
    list_date_lecture_ok.append(plan.date)

for plan_final in list_plan_final:
    if plan_final.date in list_date_lecture_ok:
        index=list_date_lecture_ok.index(plan_final.date)
        plan=lp[index]
        plan_final.lecture_soir=plan.lecture_soir

def insert_data():
    locale.setlocale(locale.LC_TIME,'fr_FR')
    list_plan=[]
    for key,y in enumerate(list_plan_final):
        id=key+1
        mois=y.date.strftime("%m").lstrip('0')
        jour_temp=y.date.strftime('%d').lstrip('0')
        nom_mois=y.date.strftime('%B')
        jour=jour_temp+' '+nom_mois
        chapitre_matin=None
        lecture_soir=y.lecture_soir
        if lecture_soir is not None:
            lecture_soir_splited=lecture_soir.split()
            
            if len(lecture_soir_splited) == 2:
                livre_soir=lecture_soir_splited[0]
                chapitre_soir=lecture_soir_splited[1]
            elif len(lecture_soir_splited) ==3:
                livre_soir=lecture_soir_splited[0]+' '+lecture_soir_splited[1]
                chapitre_soir=lecture_soir_splited[2]
            else:
                chapitre_soir='1'
                livre_soir=lecture_soir_splited[0]
        else:
            livre_soir = None
            chapitre_soir = None
        livre_matin=None
        nb_annee=y.nb_annee
        rang_annee=y.rang_annee
        record=(id,mois,jour,chapitre_matin,chapitre_soir,livre_matin,livre_soir,nb_annee,rang_annee)
        list_plan.append(record)
        # current_year_rank=y.rang_annee
        # data="{};{};{};{};{};{};{}\n".format(id,mois,jour,lecture_matin,lecture_soir,livre_matin,livre_soir)
    
    cursor.executemany('INSERT INTO lecture_new VALUES(?,?,?,?,?,?,?,?,?)',list_plan)
    conn.commit()

# insert_data()



