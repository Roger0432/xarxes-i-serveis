import paho.mqtt.client as mqtt
from bottle import route, run, template
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json
import config

# Store the last n received messages
data_store = []
n = config.mqtt_config["messages_to_store"]  # Number of messages to store

# Process received messages and add them to data_store
def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode())  # Decode the message payload
    data_store.append(payload)  # Add the new message to the store
    if len(data_store) > n:
        data_store.pop(0)  # Remove the oldest message to maintain the last n messages

# Function to configure the MQTT client
def setup_mqtt_client(server, port, topic):
    client = mqtt.Client()  # Create an MQTT client instance
    client.on_message = on_message  # Set the callback for incoming messages
    client.connect(server, port, 60)  # Connect to the MQTT broker
    client.subscribe(topic)  # Subscribe to the specified topic
    client.loop_start()  # Start the network loop in a separate thread
    return client

# Function to create a plot from the data
def create_plot(data, title, ylabel):
    plt.figure()
    x = range(len(data))
    plt.plot(x, data, marker='o')
    plt.title(title) 
    plt.xlabel('Measurements')
    plt.ylabel(ylabel)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0) 
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# Web route to display the plots
@route('/')
def index():
    if not data_store:  # Check if there is data to display
        return "<p>No data available.</p>"  # Show a message if no data is present

    # Extract data for temperature, humidity, and pressure
    temperatures = [data['temperature'] for data in data_store]
    humidities = [data['humidity'] for data in data_store]
    pressures = [data['pressure'] for data in data_store]

    # Generate plots for each type of data
    temp_img = create_plot(temperatures, "Temperature", "°C")
    hum_img = create_plot(humidities, "Humidity", "%")
    pres_img = create_plot(pressures, "Pressure", "hPa")

    return template('''
        <h1>Weather Data Graphs</h1>
        <h2>Temperature</h2>
        <img src="data:image/png;base64,{{temp_img}}" />
        <h2>Humidity</h2>
        <img src="data:image/png;base64,{{hum_img}}" />
        <h2>Pressure</h2>
        <img src="data:image/png;base64,{{pres_img}}" />
    ''', temp_img=temp_img, hum_img=hum_img, pres_img=pres_img)

# Main function to set up MQTT and start the web server
def main():
    mqtt_server = config.mqtt_config["mqtt_server"]
    mqtt_port = config.mqtt_config["mqtt_port"]
    mqtt_topic = config.mqtt_config["mqtt_topic"]

    client = setup_mqtt_client(mqtt_server, mqtt_port, mqtt_topic)  # Initialize the MQTT client

    try:
        run(host='localhost', port=8080, debug=True)
    except KeyboardInterrupt:
        print("\nTerminating the program...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
