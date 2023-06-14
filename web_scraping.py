#!/usr/bin/python3

# ------------------------------------------------------------------
# Name:  web_scraping.py
#
# Description:  Script um bestimmte Anzahl von Steam Reviews zu holen und diese in einem CSV abzuspeichern dies ist die Version,
#               die für die Automatisierung gebraucht werden kann.
#
# Autor: Lukas Pfyl
#
# History:
# 03-Feb-2023   Lukas Pfyl  Initial Version
# 06-Feb-2023   Abstand zwischen Abfragen hinzugefügt
#
# ------------------------------------------------------------------

# =============
# Packages
# =============

import requests                     #HTTP requests machen
from bs4 import BeautifulSoup       #Informationen von Web Pages scrapen bs4 -> Beautiful Soup 4
import csv                          #CSV Files erstellen
import datetime                     #Datums Formate formatieren
import time

# =============
# Functions
# =============

#Mit dieser Funktion wird der Name des Games umgewandelt in dessen zugehörige App ID, jedes Game auf Steam hat eine App ID
def get_app_id(game_name):
    try:
        #Abfrage machen auf die Steam Store Website und die Antwort als Variable "response" speichern
        response = requests.get(url=f'https://store.steampowered.com/search/?term={game_name}&category1=998', headers={'User-Agent': 'Mozilla/5.0'})
        #Parsed das HTML dokument und erstellt ein neues Beautiful Soup Objekt
        soup = BeautifulSoup(response.text, 'html.parser')
        #Sucht in dem geparsten HTML Dokument nach "data-ds-appid" und speicher den Wert als "app_id" ab
        app_id = soup.find(class_='search_result_row')['data-ds-appid']
        #Die Variable "app_id" wird zurückgegeben
        return app_id
    except:
        print("Game/Tool nicht vorhanden auf Steam")
        print('------------------------------------------------------------------')

#Diese Funktion macht eine Request um die Reviews für ein Game zu bekommen dafür braucht es den Parameter "appid", params ist standardmässig json das man die Ausgabe als JSON Struktur bekommt
def get_reviews(appid, params={'json':1}):
    try:
        #Definiert die Variable url die Angegebene Addresse ist die Standard url für die Steam App Review API
        url = 'https://store.steampowered.com/appreviews/'
        #Mit der "requests.get()" Funktion wird eine HTTP GET request geschikt zusammen mit den Definierten Query parameter und "User-Agent" Header
        response = requests.get(url=url+appid, params=params, headers={'User-Agent': 'Mozilla/5.0'})
        #Die JSON formatierten Review Daten werden zurückgegeben
        return response.json()
    except:
        print("Fehler beim machen der Abfrage, stimmt die AppID?")
        print('------------------------------------------------------------------')

#Diese Funktion holt eine bestimmte Anzahl Reviews für eine Bestimmte App auf Steam, dafür braucht es den Parameter "appid" und "amount", appid ist selbsterklärend und amount ist die Anzahl an Reviews die man haben möchte
def get_n_reviews(appid, amount):
    try:
        #Definiert eine leere Liste "reviews" die später gefüllt wird
        review_data = []
        #Die Variable cursor wird gebraucht um durch die Reviews zu navigieren
        cursor = '*'
        #Dictionary mit Parametern die in der Variable gespeichert werden
        params = {
            'json': 1,
            'filter': 'all',
            'language': 'all',
            'day_range': 9223372036854775807,
            'review_type': 'all',
            'purchase_type': 'all',
            'cursor': cursor
        }

        requests_per_minute = 120
        elapsed_time = 0

        #While loop die lauft solang amount grösser als 0 ist
        while amount > 0:
            start_time = time.perf_counter()

            reviews = get_reviews(appid, params)

            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            batch_reviews = reviews['reviews']
            cursor = reviews['cursor']

            review_data.extend(batch_reviews)

            wait_time = 60 / requests_per_minute - elapsed_time

            if wait_time < 0:
                wait_time = 0
            
            time.sleep(wait_time)

            amount -= len(batch_reviews)
            params['cursor'] = cursor

        #Das Dictionary reviews wird zurückgegeben
        return review_data
    except:
        print("Fehler beim machen der Abfrage, stimmt die AppID?")
        print('------------------------------------------------------------------')
        
#Das heutige datum wird mit der Funktion datetime.date.today() geholt und mit .strftime() formatiert das es so aussieht -> 16_12_2022
def _getToday():
    return datetime.date.today().strftime("%d_%m_%Y")

# =============
# Hauptprogramm
# =============

file_path = "/home/sky/Downloads/"      #Pfad angeben wo das .csv File gespeichert wird
game_name = "Celeste"   #Name des Spieles
amount = 10            #Anzahl der Reviews

appid = get_app_id(game_name)
reviews = get_n_reviews(appid, amount)
#csv_name = "%s_%s.%s" % (game_name, _getToday() ,"csv")
csv_name = 'reviews.csv'
full_path = str(file_path + csv_name)

with open(full_path, 'w', encoding='utf-8', newline='\n') as csvfile:

    writer = csv.writer(csvfile, quotechar='"')

    writer.writerow(reviews[0].keys())

    for dictionary in reviews:
        writer.writerow(dictionary.values())

print('CSV-File erfolgreich erstellt! :D')


