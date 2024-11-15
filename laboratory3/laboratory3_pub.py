import config
import paho.mqtt.client as mqtt
import requests
import json
from datetime import datetime
import time
import random
import string

# Configuració de l'API d'OpenWeatherMap
API_KEY = "LA_TEVA_CLAU_API"
BASE_URL = "https://api.openweathermap.org/data/2.5/onecall"

def generate_node_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def get_weather_data(lat, lon):
    url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        temperature = data['current']['temp']
        humidity = data['current']['humidity']
        pressure = data['current']['pressure']
        return temperature, humidity, pressure
    else:
        print("Error en obtenir les dades:", data)
        return None, None, None

def main():
    # Recupera informació de configuració MQTT
    mqtt_server = config.mqtt_config["mqtt_server"]
    mqtt_topic = config.mqtt_config["mqtt_topic"]
    mqtt_name = config.mqtt_config["mqtt_name"]
    mqtt_port = config.mqtt_config["mqtt_port"]

    # Crea el client MQTT
    mqtt_client = mqtt.Client(mqtt_name)
    mqtt_client.connect(mqtt_server, port=mqtt_port, keepalive=60)
    mqtt_client.loop_start()

    lat = input("Enter the latitude: ")
    lon = input("Enter the longitude: ")
    period = int(input("Enter the period (in seconds): "))

    node_id = generate_node_id()

    is_finished = False
    while not is_finished:
        temperature, humidity, pressure = get_weather_data(lat, lon)
        if temperature is not None:
            # Genera i publica el missatge JSON
            data = {
                "node_id": node_id,
                "timestamp": datetime.now().isoformat(),
                "temperature": temperature,
                "pressure": pressure,
                "humidity": humidity,
            }
            print(f"Publishing: {data}")
            mqtt_client.publish(mqtt_topic, payload=json.dumps(data), qos=0, retain=False)
        else:
            print("Error retrieving weather data. Retrying...")
        
        time.sleep(period)

    mqtt_client.loop_stop()
    mqtt_client.disconnect()

if __name__ == "__main__":
    main()
