import os

from tqdm import tqdm

from gtt import extra
from gtt.extra import api_data_html
from bs4 import BeautifulSoup


def gttallLinepage():
    html = api_data_html("https://www.gtt.to.it/cms/percorari/urbano")
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find("table").find_all("tr")
    data = []
    for row in rows:
        cols = row.find_all('td')

        # Assicurati che ci siano colonne nella riga
        if cols:
            # Estrai il nome della linea dalla prima

            nome_linea = cols[0].strong.text.strip()

            link_percorso = cols[0].a['href']
            data.append((nome_linea, "https://www.gtt.to.it" + str(link_percorso)))
    print("trovate tutte le pagine delle linee")
    return data


def routeline(url):
    html = api_data_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find("table"):
        rows = soup.find("table").find_all("tr")
    else:
        print("La tabella non è presente")
        return []

    data = []
    # Utilizza tqdm per visualizzare una barra di caricamento
    for row in rows:
        cols = row.find_all('td')
        if cols:
            link_percorso = cols[1].a['href']
            direzione = cols[1].a.text.strip()
            data.append((direzione, "https://www.gtt.to.it" + str(link_percorso)))

    return data


def gttallline():
    data = gttallLinepage()
    routes = []
    for line, link in tqdm(data, desc="ricerca delle  fermata per le direzioni delle varie linee", total=len(data)):
        route_data = routeline(link)
        for direzione, url in route_data:
            routes.append((gttstopforline(url), direzione, line))
    return routes


def printout(data):
    var = ""
    if data == "Errore: Fermata non trovata o sito non raggiungibile" or data == "":
        return data
    for fermata, direction, line in data:
        var += "Linea: " + str(line) + " (" + str(direction) + ")\n"
        for stop, Nome, ub in fermata:
            var += "Fermata: " + str(stop) + " -" + str(Nome) + " , "
            var += "Ubicazione: " + str(ub) + "\n"
    return var


def gttstopforline(url):
    html = api_data_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find("table"):
        rows = soup.find("table").find_all("tr")
    else:
        print("La tabella non è presente")
        return []

    data = []
    for row in rows:
        cols = row.find_all('td')
        if cols:
            data.append((cols[0].a.text.strip(), cols[1].text.strip(), cols[2].text.strip()))
    return data


def wtitefile(file_path, data):
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write(data)
        else:
            with open(file_path, 'a') as file:
                file.write(data)
    except Exception as e:
        print(f"Errore nella scrittura del file : {e}")


wtitefile("fermate.text", printout(gttallline()))
