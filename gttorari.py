import datetime

import bs4
import pytz
import requests


def printout(data):
    var = ""
    if data == "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    for bus_line, direction, pas, nextpass in data:
        var += "Linea: " + bus_line + " (" + direction + ")<br>"
        var += "Passaggi: " + pas + "<br>"
        if nextpass == "Non disponibile":
            var += "Prossimo passaggio: Non disponibile <br>"
        elif int(nextpass) <= 1:
            var += "Prossimo passaggio: In arrivo" + "<br>"
        else:
            var += "Prossimo passaggio: " + str(nextpass) + " minuti" + "<br>"
    return var


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

                if '*' in pas:
                    time_str = pas.split('*')[0]
                    hours, minutes = map(int, time_str.split(':'))
                    rome_timezone = pytz.timezone('Europe/Rome')  # Set the time zone to Rome
                    now = datetime.datetime.now(rome_timezone)
                    nextpass = (hours * 60 + minutes) - (now.hour * 60 + now.minute)
                else:
                    nextpass = "Non disponibile"
                data.append((bus_line, direction, pas, nextpass))
    if stop == "":
        stop = "Fermata non trovata"
    if "." in stop:
        stop.replace(".", "")

    return data, stop


def gttorari_stop(stop):
    if isinstance(stop, int):
        pre = "https://www.gtt.to.it/cms/percorari/arrivi?palina="
        post = "&bacino="
        url = pre + str(stop) + post
        return gttorari_url(url)
    else:
        return print("La fermata inserita non è valida")


def gttorari_stop_line(stop, line):
    data, stop = gttorari_stop(stop)
    if data == "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    else:
        data = [x for x in data if x[0] == line]
        return data, stop



