import paho.mqtt.client as mqtt

def main():
    # Configura les dades de connexió
    mqtt_server = "broker.hivemq.com"  # Substitueix amb el teu broker
    mqtt_port = 1883
    mqtt_topic = "esupt"  # Tema on publicar
    mqtt_name = "mqtt_publisher"  # Identificador del client

    # Crear client MQTT
    mqtt_client = mqtt.Client(mqtt_name)
    
    # Connectar el client al servidor MQTT
    mqtt_client.connect(mqtt_server, port=mqtt_port, keepalive=60)

    # Iniciar el bucle MQTT en un fil separat
    mqtt_client.loop_start()

    is_finished = False
    while not is_finished:
        message = input("Escriu el missatge que vols enviar: ")
        if not message:
            print("Cap missatge introduït, acabant el programa!")
            is_finished = True
        else:
            # Publicar el missatge al tema amb QoS=0 i Retain=False
            print(f"Publicant missatge='{message}' al tema='{mqtt_topic}'.")
            mqtt_client.publish(mqtt_topic, payload=message, qos=0, retain=False)

    # Desconnectar i aturar el fil del client MQTT
    mqtt_client.disconnect()
    mqtt_client.loop_stop()

if __name__ == "__main__":
    main()
