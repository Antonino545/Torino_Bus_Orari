import csv
import json

import bs4
import pytz
import requests
from google.transit import gtfs_realtime_pb2


# classe fermata


def jsonout(data):
    if data is None:
        print("non ci sono dati di passaggio per questa fermata o non è stata inserita una fermata valida")
    else:
        return json.dumps(data)


def printout(data):
    var = ""
    for bus_line, direction, pas, nextpass in data:
        var += "Linea: " + bus_line + "<br>"
        var += "Direzione: " + direction + "<br>"
        var += "Passaggi: " + pas + "<br>"
        if nextpass <= 1:
            var += "Prossimo passaggio tra meno di un minuto" + "<br>"
        else:
            var += "Prossimo passaggio: " + str(nextpass) + " minuti" + "<br>"
    return var


def gttorari_url(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    data = []
    table = soup.find('tbody')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            bus_line = cols[0].find('a').text.strip()
            direction = cols[1].text.strip()
            pas = cols[2].text.replace(
                "Al momento non ci sono previsioni in tempo reale, clicca qui per visualizzare i passaggi programmati.",
                "").strip()
            time_str = pas.split('*')[0]
            hours, minutes = map(int, time_str.split(':'))
            rome_timezone = pytz.timezone('Europe/Rome')  # Set the time zone to Rome
            now = datetime.datetime.now(rome_timezone)
            nextpass = (hours * 60 + minutes) - (now.hour * 60 + now.minute)
            data.append((bus_line, direction, pas, nextpass))

    return data


def gttorari_stop(stop):
    if isinstance(stop, int):
        pre = "https://www.gtt.to.it/cms/percorari/arrivi?palina="
        post = "&bacino="
        url = pre + str(stop) + post
        return gttorari_url(url)
    else:
        return print("La fermata inserita non è valida")


def gttorari_stop_line(stop, line):
    data = gttorari_stop(stop)
    return [(bus, temp, pas, nextpass) for bus, temp, pas, nextpass in data if bus == str(line)]


# recuperare i dati in tempo reale da GTFS-RT (GTFS Real Time)
import datetime


def analizza_file_binario(filename, fermata_desiderata):
    with open(filename, 'rb') as f:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(f.read())

    fermate_in_arrivo = {}

    for entity in feed.entity:
        if entity.HasField('trip_update') and entity.trip_update.trip.trip_id:
            trip_id = entity.trip_update.trip.trip_id
            linea = trip_id.split(':')[0]

            for stop_time_update in entity.trip_update.stop_time_update:
                stop_sequence = stop_time_update.stop_sequence

                if stop_sequence == fermata_desiderata:
                    orario_di_arrivo_timestamp = int(stop_time_update.departure.time)
                    orario_di_arrivo = datetime.datetime.fromtimestamp(orario_di_arrivo_timestamp)
                    tempo_attesa = orario_di_arrivo - datetime.datetime.now()

                    if linea not in fermate_in_arrivo:
                        fermate_in_arrivo[linea] = []

                    fermate_in_arrivo[linea].append({
                        'fermata': fermata_desiderata,
                        'linea': linea,
                        'orario_di_arrivo': orario_di_arrivo,
                        'tempo_attesa': tempo_attesa
                    })

    return fermate_in_arrivo


# Specifica la fermata desiderata (modifica questa fermata secondo le tue esigenze)
fermata_desiderata = 39  # Ad esempio, fermata 9

# funziona che restituisce il numero della fermata avendo l'id della fermata usando il csv  id si trova nella colonna 0 invece il numero nella colonna 1

# Definisci il nome del tuo file CSV
file_path = 'Resources/gtt_gtfs/stops.txt'

# Crea un dizionario per mappare l'ID alla fermata
id_to_N = {}

# Leggi il file CSV e crea il mapping
with open(file_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        id_fermata = row[1]
        N_fermata = row[0]
        id_to_N[id_fermata] = N_fermata


def find_n_stop(id):
    # Cerca il numero della fermata (N) utilizzando l'ID della fermata
    if id in id_to_N:
        numero_fermata_corrispondente = id_to_N[id]
        return numero_fermata_corrispondente
    else:
        return ""


# Analizza il file binario GTFS Real-Time
# arrivi_per_linea = analizza_file_binario('Resources/trip_update.bin', fermata_desiderata)
def allerts(filename, ):
    with open(filename, 'rb') as f:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(f.read())
    for entity in feed.entity:
        if entity.HasField('alert') and entity.alert.HasField('description_text'):
            description_text = ""
            stops = "Stop Number:"
            for stop in entity.alert.informed_entity:
                a = find_n_stop(stop.stop_id)
                if a != "":
                    stops = stops + " " + a
            if stops != "Stop Number:":
                print(stops)
            for translation in entity.alert.description_text.translation:
                description_text += translation.text + "\n"
            print("Descrizone:", description_text)


# analizza('Resources/trip_update.bin' )
# analizza('Resources/vehicle.bin' )
allerts('Resources/alerts.bin')
