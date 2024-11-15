import requests
import json

# No tocar, clau privada per tal de fer les peticions a la API de OpenWeatherMap
# Només es poden fer 60 peticions/minut, pero us podeu registrar gratuitament a https://openweathermap.org/
api_key = "15d8c89a79ce8bbf11e3431de98c5e86"

# Definim la latitud i longitud on volem les dades
lat = "41.501507"
lon = "2.106929"

# Generem la URL amb els paràmetres indicats
url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&appid={}".format(lat, lon, api_key)

def main():
    # Llencem una peticio HTTP a la URL i capturem la resposta
    response = requests.get(url)

    # Recuperem les dades de la resposta a la peticio HTTP
    data = json.loads(response.text)

    # Imprimim les dades per pantalla
    print(data)

if __name__ == "__main__":
    main()
