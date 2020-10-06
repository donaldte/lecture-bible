from datetime import datetime, timedelta, timezone,date
import icalendar
import locale
import sqlite3
from parse_ics import Plan

#Connexion base de données
conn= sqlite3.connect('bibleunanv2.db')
cursor=conn.cursor()


def get_plan_from_ics():
    locale.setlocale(locale.LC_TIME,'fr_FR')
    icalfile = open('plan-2ans.ics', 'rb')
    gcal = icalendar.Calendar.from_ical(icalfile.read())
    increment=0
    year_rank=1
    list_plan=[]
    for component in gcal.walk():
        if component.name == "VEVENT":
            increment+=1
            if(increment)<=365:
                year_rank = 1
            else:
                year_rank = 2

            summary = component.get('summary')
            startdt = component.get('dtstart').dt
            jour=startdt.strftime('%d')
            mois=startdt.strftime('%B')
            jour_mois=jour+' '+mois

            plan=Plan(startdt,summary,2,year_rank)
            list_plan.append(plan)
            
    icalfile.close()
    return list_plan

list_plan_ics = get_plan_from_ics()

def insert_data():
    locale.setlocale(locale.LC_TIME,'fr_FR')
    list_plan=[]
    for key,plan in enumerate(list_plan_ics):
        id=key+1
        mois=plan.date.strftime("%m").lstrip('0')
        jour_temp=plan.date.strftime('%d').lstrip('0')
        nom_mois=plan.date.strftime('%B')
        jour=jour_temp+' '+nom_mois
        chapitre_matin=None
        livre_matin=None
        lecture_soir=plan.lecture_soir
        lecture_soir_splited=lecture_soir.split()
        
        if len(lecture_soir_splited) == 2:
            livre_soir=lecture_soir_splited[0]
            chapitre_soir=lecture_soir_splited[1].replace('-',',')
        elif len(lecture_soir_splited) ==3:
            livre_soir=lecture_soir_splited[0]+' '+lecture_soir_splited[1]
            chapitre_soir=lecture_soir_splited[2].replace('-',',')
        else:
            chapitre_soir='1'
            livre_soir=lecture_soir_splited[0]
        nb_annee=plan.nb_annee
        rang_annee=plan.rang_annee
        record=(id,mois,jour,chapitre_matin,chapitre_soir,livre_matin,livre_soir,nb_annee,rang_annee)
        list_plan.append(record)
        # current_year_rank=plan.rang_annee
        # data="{};{};{};{};{};{};{}\n".format(id,mois,jour,lecture_matin,lecture_soir,livre_matin,livre_soir)
    
    cursor.executemany('INSERT INTO lecture_2ans VALUES(?,?,?,?,?,?,?,?,?)',list_plan)
    conn.commit()

insert_data()

