#!/usr/bin/python3

# ------------------------------------------------------------------
# Name:  steam_reviews.py
#
# Description:  Mit diesem Programm können verschiedene Funktionen ausgeführt werden im Zusammenhang mit Steam Reviews darunter sind:
#               -Bestimmte Anzahl Reviews anzeigen für ein Game auf Steam
#               -Bestimmte Anzahl Reviews als CSV speichern für ein Game auf Steam
#               -Interaktive Version
#
# Autor: Lukas Pfyl
#
# History:
# 30-Nov-2022   Lukas Pfyl      Initial Version
# 07-Dec-2022   Lukas Pfyl      Menü hinzugefügt und Überarbeitung des gesamten Codes
# 14-Dec-2022   Lukas Pfyl      Option 1 Angefangen zu Programmieren, Option 3 geschrieben
# 15-Dec-2022   Lukas Pfyl      Option 1 fertiggestellt und angefangen mit Option 2
# 16-Dec-2022   Lukas Pfyl      Option 2 fertiggestellt und Kommenentare hinzugefügt, Komplettübererbeitung print Befehle

# ------------------------------------------------------------------

# =============
# Packages
# =============

import requests                     #HTTP requests machen
from bs4 import BeautifulSoup       #Informationen von Web Pages scrapen bs4 -> Beautiful Soup 4
import random                       #Zufällige Nummer, Listen shuffeln etc
import csv                          #CSV Files erstellen
import datetime                     #Datums Formate formatieren
import textwrap

# =============
# Functions
# =============

#Mit dieser Funktion wird der Name des Games umgewandelt in dessen zugehörige App ID, jedes Game auf Steam hat eine App ID
def get_app_id(game_name):
    #Abfrage machen auf die Steam Store Website und die Antwort als Variable "response" speichern
    response = requests.get(url=f'https://store.steampowered.com/search/?term={game_name}&category1=998', headers={'User-Agent': 'Mozilla/5.0'})
    #Parsed das HTML dokument und erstellt ein neues Beautiful Soup Objekt
    soup = BeautifulSoup(response.text, 'html.parser')
    #Sucht in dem geparsten HTML Dokument nach "data-ds-appid" und speicher den Wert als "app_id" ab
    app_id = soup.find(class_='search_result_row')['data-ds-appid']
    #Die Variable "app_id" wird zurückgegeben
    return app_id

#Diese Funktion macht eine Request um die Reviews für ein Game zu bekommen dafür braucht es den Parameter "appid", params ist standardmässig json das man die Ausgabe als JSON Struktur bekommt
def get_reviews(appid, params={'json':1}):
        #Definiert die Variable url die Angegebene Addresse ist die Standard url für die Steam App Review API
        url = 'https://store.steampowered.com/appreviews/'
        #Mit der "requests.get()" Funktion wird eine HTTP GET request geschikt zusammen mit den Definierten Query parameter und "User-Agent" Header
        response = requests.get(url=url+appid, params=params, headers={'User-Agent': 'Mozilla/5.0'})
        #Die JSON formatierten Review Daten werden zurückgegeben
        return response.json()

#Diese Funktion holt eine bestimmte Anzahl Reviews für eine Bestimmte App auf Steam, dafür braucht es den Parameter "appid" und "amount", appid ist selbsterklärend und amount ist die Anzahl an Reviews die man haben möchte
def get_n_reviews(appid, amount):
    #Definiert eine leere Liste "reviews" die später gefüllt wird
    reviews = []
    #Die Variable cursor wird gebraucht um durch die Reviews zu navigieren
    cursor = '*'
    #Dictionary mit Parametern die in der Variable gespeichert werden
    params = {
            'json' : 1,
            'filter' : 'all',
            'language' : 'english',
            'day_range' : 9223372036854775807,
            'review_type' : 'all',
            'purchase_type' : 'all'
            }

    #While loop die lauft solang amount grösser als 0 ist
    while amount > 0:
        #Das params dictionary wird modifiziert, ein neues key-value pair für cursor und num_per_page hinzugefügt, der wert für num_per_page ist mindestens 100 und der momentane Wert von amount
        params['cursor'] = cursor.encode()
        params['num_per_page'] = min(100, amount)
        #amount = amount - 100
        amount -= 100

        #Die funktion get_reviews() wird gecallt mit der appid und den modifizierten Parametern und speichert die Antwort als response
        response = get_reviews(appid, params)
        #Der Wert von cursor wird geupdatet zu dem Wert der in den params zuvor angegeben wurde
        cursor = response['cursor']
        #Die leere Liste reviews wird gefüllt mit dem Wert reviews aus dem Dictionary response
        reviews += response['reviews']

        #Wenn ein Review Länger als 100 Symbole ist wird ein break gemacht
        if len(response['reviews']) < 100: break

    #Das Dictionary reviews wird zurückgegeben
    return reviews

#Das heutige datum wird mit der Funktion datetime.date.today() geholt und mit .strftime() formatiert das es so aussieht -> 16_12_2022
def _getToday():
    return datetime.date.today().strftime("%d_%m_%Y")

#Printed das Menü
def print_menu():
    print('1 -- Bestimmte Anzahl Reviews anzeigen für ein Game auf Steam')
    print('2 -- Bestimmte Anzahl Reviews als CSV speichern für ein Game auf Steam')
    print('3 -- Was kann ich mit diesem Programm tun?')
    #print('4 --')
    print('0 -- Beenden')
    print('')

#Definert Option 1 im Menü '1 -- Bestimmte Anzahl Reviews anzeigen für ein Game auf Steam'
def option1():
    print('')
    print('1 -- Bestimmte Anzahl Reviews anzeigen für ein Game auf Steam')
    print('------------------------------------------------------------------')
    print('')
    # Den User fragen wie das Game heisst und das als Variable game_name abspeichern
    game_name = input('Von welchem Game möchtest du die Reviews sehen?: ')
    print('')


    #Nach der Menge von Reviews fragen diese in einen int umwandeln mit der int() Funktion und dann als Variable amount speichern
    amount = int(input('Wie viele Reviews möchtest du sehen?: '))
    print('')

    #Die appid holen mit der Funktion get_app_id der die zuvor definierte Variable game_name mitgegeben wird
    appid = get_app_id(game_name)

    #Eine Bestimmte Anzahl Reviews holen mit der Funktion get_n_reviews und die zuvor definierten Variablen appid und amount mitgeben
    reviews = get_n_reviews(appid, amount)

    #For loop mit der die Reviews in leserlicher Form ausgegeben werden die range amount ist die Anzahl und mit i in range wird der Loop so oft wiederholt wie die amount ist
    #Dabei wird i jedes mal eins grösser
    for i in range(amount):
        #Damit man weiss welches Review welches ist wird hier die Zahl geprinted im format: Review 1:, das +1 nach i ist da weil es sonst bei 0 beginnen würde
        print('Review ' + str(i+1) + ':')
        print('------------------------------------------------------------------')
        wrapped_text = textwrap.wrap(reviews[i]['review'], width=100)
        #Aus der Liste von Dictionaries wird das i-te Item aus Reviews geprinted das den Wert review hat
        for line in wrapped_text:
            print(line)
        if i != amount:
            input()

#Definiert Option 2 im Menü '2 -- Bestimmte Anzahl Reviews als CSV speichern für ein Game auf Steam'
def option2():
    print('')
    print('2 -- Bestimmte Anzahl Reviews als CSV speichern für ein Game auf Steam')
    print('------------------------------------------------------------------')
    print('')
    game_name = input('Von welchem Game möchtest du die Reviews sehen?: ')
    print('')
    amount = int(input('Wie viele Reviews möchtest du sehen?: '))
    print('')
    file_path = input('Wo soll das CSV-File gespeichert werden? (Muss auf der gleichen Partition sein): ')
    print('')

    appid = get_app_id(game_name)
    reviews = get_n_reviews(appid, amount)
    csv_name = "%s_%s.%s" % (game_name, _getToday() ,".csv")
    full_path = str(file_path + csv_name)

    with open(full_path, 'w', encoding='utf-8', newline='\n') as csvfile:

        writer = csv.writer(csvfile, quotechar='"')

        writer.writerow(reviews[0].keys())

        for dictionary in reviews:
            writer.writerow(dictionary.values())

    print('CSV-File erfolgreich erstellt! :D')
    input()

def option3():
    print('')
    print('Was kann ich mit diesem Programm tun?')
    print('------------------------------------------------------------------')
    print('Du kannst die Reviews eines Games anzeigen lassen und dir diese auch als csv speichern lassen.')
    print('Somit kannst du herausfinden, was andere von diesem Game halten und diese Daten auch so abspeichern, dass du sie später in einem Excel o. Ä analysieren kannst.')
    print('')
    input()

def option4():
    """""
    # Make an API call to get a list of all available games on Steam
    response = requests.get("http://api.steampowered.com/ISteamApps/GetAppList/v2")
    app_list = response.json()['applist']['apps']

    # Choose a random game from the list of available games
    random_app = random.choice(app_list)
    appid = str(random_app['appid'])

    reviews = get_reviews(appid)

    sorted_reviews = sorted(reviews, key=lambda x: x['voted_up'], reverse=True)

    print(sorted_reviews[0]['review'])
    """
def option0():
    print('')
    words = ["Tschüsseldorf",
             "Tschöö mit Ö",
             "Ciao Kakao",
             "Tschüssikowski"
             ]
    random.shuffle(words)
    print(words[0])

# =============
# Hauptprogramm
# =============

while (True):
    print_menu()

    option = int(input('Auswahl eingeben: '))
    if option == 1:
        option1()
    elif option == 2:
        option2()
    elif option == 3:
        option3()
    #elif option == 4:
        #option4()
    elif option == 0:
        option0()
        exit()
    else:
        print('Fehler, Bitte eine Zahl zwischen 1 und 3 eingeben.')
