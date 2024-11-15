import paho.mqtt.client as mqtt
import json
from datetime import datetime
import time
import random
import config

def main():
    # Configura el client MQTT
    mqtt_server = config.mqtt_config["mqtt_server"]
    mqtt_topic = config.mqtt_config["mqtt_topic"]
    mqtt_port = config.mqtt_config["mqtt_port"]
    mqtt_name = "simulated_publisher"
    
    client = mqtt.Client(mqtt_name)
    client.connect(mqtt_server, port=mqtt_port, keepalive=60)
    client.loop_start()

    try:
        while True:
            # Dades simulades
            data = {
                "node_id": "testnode123",
                "timestamp": datetime.now().isoformat(),
                "temperature": round(random.uniform(15, 30), 2),  # Temperatura simulada entre 15 i 30 °C
                "pressure": random.randint(980, 1050),            # Pressió simulada entre 980 i 1050 hPa
                "humidity": random.randint(30, 90)                # Humitat simulada entre 30% i 90%
            }
            print(f"Publishing: {data}")
            client.publish(mqtt_topic, payload=json.dumps(data), qos=0, retain=False)

            # Espera uns segons abans d'enviar el següent missatge
            time.sleep(5)
    except KeyboardInterrupt:
        print("Simulació interrompuda per l'usuari.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
