import csv
import datetime
import json
import bs4
import pytz
import requests


# classe fermata


def jsonout(data):
    if data is None:
        print("non ci sono dati di passaggio per questa fermata o non è stata inserita una fermata valida")
    else:
        return json.dumps(data)


def printout(data):
    var = ""
    for bus_line, direction, pas, nextpass in data:
        var += "Linea: " + bus_line +" ("+ direction + ")<br>"
        var += "Passaggi: " + pas + "<br>"
        if nextpass <= 1:
            var += "Prossimo passaggio tra meno di un minuto" + "<br>"
        else:
            var += "Prossimo passaggio: " + str(nextpass) + " minuti" + "<br>"
    return var
def printnextpass(data):
    var=""
    for bus_line, direction, pas, nextpass in data:
        if nextpass <= 1:
            var += "Prossimo passaggio tra meno di un minuto" + "<br>"
        else:
            var += "Prossimo passaggio: " + str(nextpass) + " minuti" + "<br>"

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
