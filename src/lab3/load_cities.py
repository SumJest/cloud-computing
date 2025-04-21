import logging

import requests

DEFAULT_CITIES_LIST = ['москва', 'архангельск', 'казань', 'нижний новгород', 'дубна', 'анапа', 'алма-ата', 'астрахань']


def load_russian_cities():
    logging.info("Loading Russian cities...")
    url = "https://raw.githubusercontent.com/pensnarik/russian-cities/refs/heads/master/russian-cities.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        city_names = [entry["name"].strip().lower() for entry in data]
        return list(city_names)
    except requests.RequestException as e:
        logging.error(f"[!] Failed to download city list: {e}")

        logging.info(f"Using default city list: {DEFAULT_CITIES_LIST}")
        return DEFAULT_CITIES_LIST
