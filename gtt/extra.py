import requests


def api_data_json(url):
    timeout = 5
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        print(f'Status code={response.status_code}')
    except requests.exceptions.RequestException as err:
        print(err)
        return f"Errore: Impossibile ottenere i dati dall'API ({err})"
    return response.json()


def api_data_html(url):
    timeout = 5
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(err)
        return f"Errore: Impossibile ottenere i dati dall'API ({err})"
    return response.text


def NameStop(stop, df):
    result = df[df.iloc[:, 0].astype(str) == str(stop)]
    if not result.empty:
        return result.iloc[0, 1]
    return None
