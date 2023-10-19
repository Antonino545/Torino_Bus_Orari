import datetime

import bs4
import pytz
import requests


def printout(data):
    var = ""
    if data is "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    for bus_line, direction, pas, nextpass in data:
        var += "Linea: " + bus_line + " (" + direction + ")<br>"
        var += "Passaggi: " + pas + "<br>"
        if int(nextpass) <= 1:
            var += "Prossimo passaggio: In arrivo" + "<br>"
        else:
            var += "Prossimo passaggio: " + str(nextpass) + " minuti" + "<br>"
    return var


def gttorari_url(url):
    global response
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
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            bus_line = cols[0].find('a').text.strip()
            direction = cols[1].text.strip()
            pas = cols[2].text.replace(
                "Al momento non ci sono previsioni in tempo reale, clicca qui per visualizzare i passaggi programmati.",
                "").strip()
            print(pas)
            if pas != "":
                print(pas)
                if '*' in pas:
                    print("*")
                    time_str = pas.split('*')[0]
                    hours, minutes = map(int, time_str.split(':'))
                else:
                    if '\xa0' in pas:
                        print('\xa0')
                        pas = pas.replace('\xa0', '')
                    time_str = pas.split(' ')[0]
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
