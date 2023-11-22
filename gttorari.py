import csv
import datetime

import bs4
import pytz
import requests


def next_pass(pas):
    hours, minutes = map(int, pas.split(' ')[0].split(':'))
    rome_timezone = pytz.timezone('Europe/Rome')  # Set the time zone to Rome
    now = datetime.datetime.now(rome_timezone)
    nextpass = (hours * 60 + minutes) - (now.hour * 60 + now.minute)
    return nextpass


def printout(data):
    var = ""
    if data == "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    for bus_line, pas, nextpass in data:
        var += "Linea: " + bus_line + " <br>"
        var += "Passaggi: " + pas + "<br>"
        if nextpass == "Non disponibile":
            var += "Prossimo passaggio: Non disponibile <br>"
        elif int(nextpass) <= 1:
            var += "Prossimo passaggio: In arrivo" + "<br>"
        else:
            var += "Prossimo passaggio: " + str(nextpass) + " minuti" + "<br>"
    return var


def formatta_orario(input_string):
    result = ''
    for i in range(0, len(input_string), 4):
        result += input_string[i:i + 2] + ':' + input_string[i + 2:i + 4] + ' '
    # Rimuovi lo spazio in eccesso alla fine
    result = result[:-1]
    return result


# @todo: fix this
def gttorari_url(url):
    response = None
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        if response.status_code != 401:
            return "Errore: Fermata non trovata o sito non raggiungibile"
    if response.status_code == 401:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            return "Errore: Fermata non trovata o sito non raggiungibile"
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    data = []
    table = soup.find('tbody')
    stop = soup.find('strong').text.strip()

    if table:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            bus_line = cols[0].find('a').text.strip()
            direction = cols[1].text.strip()
            pas = cols[2].text.replace(
                "Al momento non ci sono previsioni in tempo reale, clicca qui per visualizzare i passaggi programmati.",
                "").strip()
            if pas != "":
                pas = ''.join(char for char in pas if char.isdigit())
                if '*' in pas and ":" in pas:
                    time_str = pas.split('*')[0]
                    hours, minutes = map(int, time_str.split(':'))
                    rome_timezone = pytz.timezone('Europe/Rome')  # Set the time zone to Rome
                    now = datetime.datetime.now(rome_timezone)
                    nextpass = (hours * 60 + minutes) - (now.hour * 60 + now.minute)
                else:
                    try:
                        pas = formatta_orario(pas)
                        nextpass = next_pass(pas)
                    except ValueError:
                        nextpass = "Non disponibile"

                data.append((bus_line, direction, pas, nextpass))
    if stop == "":
        stop = "Fermata non trovata"
    if "." in stop:
        stop.replace(".", "")
    print(data, stop)
    return data, stop


# togliere funzione non e piu usata
def gttorari_stop(stop):
    if isinstance(stop, int):
        pre = "https://www.gtt.to.it/cms/percorari/arrivi?palina="
        post = "&bacino="
        url = pre + str(stop) + post
        return gttorari_url(url)
    else:
        return print("La fermata inserita non è valida")


def gttorariAPI(stop):
    dati = api_data(stop)
    orari_unificati = {}
    count = 0

    for passaggio in dati:

        linea = passaggio['line']
        if count <= 4:
            orario_dt = datetime.datetime.strptime(passaggio['hour'], '%H:%M:%S')
            orario = orario_dt.strftime('%H:%M')
            realtime = passaggio['realtime']
        else:
            break
        count = count + 1

        if linea not in orari_unificati:
            orari_unificati[linea] = {'orari': []}
        if realtime:
            orari_unificati[linea]['orari'].append(orario + '*')
        else:
            orari_unificati[linea]['orari'].append(orario)
    risultato = []
    for linea, info in orari_unificati.items():
        passaggi = ' '.join(info['orari'])
        orari = passaggi.replace("*", "")
        risultato.append((linea, passaggi, next_pass(orari)))
    return risultato, NameStop(stop)


def api_data(stop):
    url = "https://gpa.madbob.org/query.php?stop=" + str(stop)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return "Errore: Fermata non trovata o sito non raggiungibile"
    return response.json()


def gttorari_stop_line(stop, line):
    line = str(line)
    data, stop = gttorariAPI(stop)
    if data == "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    else:
        data = [x for x in data if x[0] == line]
        return data, stop


def read_csv(file_path):
    with open(file_path, 'r') as infile:
        reader = csv.reader(infile)
        return list(reader)


def NameStop(stop):
    data = read_csv("Resources/NewStop.csv")
    for row in data:
        if row[0] == str(stop):
            return row[1]
