import config
import paho.mqtt.client as mqtt
import requests
import json
from datetime import datetime
import time
import random
import string

# OpenWeatherMap API configuration
API_KEY = "b29796a429fbe946f851a5faccc71712"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Function to generate a unique node ID
def generate_node_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # Random alphanumeric ID

# Function to retrieve weather data from the OpenWeatherMap API
def get_weather_data(lat, lon):
    url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url) 
    data = response.json()
    if response.status_code == 200: 
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        return temperature, humidity, pressure
    else:
        print("Error retrieving data:", data)
        return None, None, None

# Main function to publish weather data via MQTT
def main():
    # Retrieve MQTT configuration from the config file
    mqtt_server = config.mqtt_config["mqtt_server"]
    mqtt_topic = config.mqtt_config["mqtt_topic"]
    mqtt_name = config.mqtt_config["mqtt_name"]
    mqtt_port = config.mqtt_config["mqtt_port"]

    # Create an MQTT client instance
    mqtt_client = mqtt.Client(mqtt_name)
    mqtt_client.connect(mqtt_server, port=mqtt_port, keepalive=60)  # Connect to the MQTT broker
    mqtt_client.loop_start()  # Start the MQTT client loop

    # Prompt the user for geographic coordinates and the publishing period
    lat = input("Enter the latitude: ")
    lon = input("Enter the longitude: ")
    period = int(input("Enter the period (in seconds): "))  # Time interval between data retrievals

    # Generate a unique node ID for the sensor
    node_id = generate_node_id()

    is_finished = False
    while not is_finished:
        # Retrieve weather data for the specified location
        temperature, humidity, pressure = get_weather_data(lat, lon)
        if temperature is not None:
            # Generate a JSON message with the weather data
            data = {
                "node_id": node_id,
                "timestamp": datetime.now().isoformat(),  # Add the current timestamp
                "temperature": temperature,
                "pressure": pressure,
                "humidity": humidity,
            }
            print(f"Publishing: {data}")  # Log the message being published
            mqtt_client.publish(mqtt_topic, payload=json.dumps(data), qos=0, retain=False)
        else:
            print("Error retrieving weather data. Retrying...")
        
        time.sleep(period)

    mqtt_client.loop_stop()
    mqtt_client.disconnect()

# Entry point of the program
if __name__ == "__main__":
    main()
