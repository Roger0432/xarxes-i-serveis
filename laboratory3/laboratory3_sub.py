import paho.mqtt.client as mqtt
from bottle import route, run, template
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json
import config

# Emmagatzema els últims n missatges rebuts
data_store = []
n = config.mqtt_config["messages_to_store"]  # Nombre de missatges a emmagatzemar

# Funció per processar el missatge rebut i afegir-lo a data_store
def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode())
    data_store.append(payload)
    if len(data_store) > n:
        data_store.pop(0)  # Elimina el més antic per mantenir els últims n

# Funció per configurar el client MQTT
def setup_mqtt_client(server, port, topic):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(server, port, 60)
    client.subscribe(topic)
    client.loop_start()
    return client

# Funció per generar gràfics en format base64
def create_plot(data, title, ylabel):
    plt.figure()
    x = range(len(data))
    plt.plot(x, data, marker='o')
    plt.title(title)
    plt.xlabel('Mesures')
    plt.ylabel(ylabel)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# Ruta de la pàgina web per mostrar els gràfics
@route('/')
def index():
    if not data_store:
        return "<p>No hi ha dades disponibles.</p>"

    temperatures = [data['temperature'] for data in data_store]
    humidities = [data['humidity'] for data in data_store]
    pressures = [data['pressure'] for data in data_store]

    temp_img = create_plot(temperatures, "Temperatura", "°C")
    hum_img = create_plot(humidities, "Humitat", "%")
    pres_img = create_plot(pressures, "Pressió", "hPa")

    return template('''
        <h1>Gràfics de dades meteorològiques</h1>
        <h2>Temperatura</h2>
        <img src="data:image/png;base64,{{temp_img}}" />
        <h2>Humitat</h2>
        <img src="data:image/png;base64,{{hum_img}}" />
        <h2>Pressió</h2>
        <img src="data:image/png;base64,{{pres_img}}" />
    ''', temp_img=temp_img, hum_img=hum_img, pres_img=pres_img)

def main():
    mqtt_server = config.mqtt_config["mqtt_server"]
    mqtt_port = config.mqtt_config["mqtt_port"]
    mqtt_topic = config.mqtt_config["mqtt_topic"]

    client = setup_mqtt_client(mqtt_server, mqtt_port, mqtt_topic)

    try:
        run(host='localhost', port=8080, debug=True)
    except KeyboardInterrupt:
        print("\nFinalitzant el programa...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
