import paho.mqtt.client as mqtt
import signal
import time

# Variable per acabar l'execució amb CTRL+C
is_finished = False

def on_sigint(signal_received, frame):
    global is_finished
    is_finished = True

def on_connect(client, userdata, flags, rc):
    print("Connectat al servidor!")

def on_message(client, userdata, message):
    # Imprimir el missatge rebut
    topic = message.topic
    msg = message.payload.decode()
    print(f"Missatge='{msg}' rebut al tema='{topic}'.")

def main():
    global is_finished

    # Configura les dades de connexió
    mqtt_server = "broker.hivemq.com"  # Substitueix amb el teu broker
    mqtt_port = 1883
    mqtt_topic = "esupt"  # Tema per subscriure's

    # Registra la interrupció del teclat CTRL+C
    signal.signal(signal.SIGINT, on_sigint)

    # Crear client MQTT
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Connectar el client al servidor MQTT
    mqtt_client.connect(mqtt_server, port=mqtt_port)

    # Subscripció al tema amb QoS=0
    mqtt_client.subscribe(mqtt_topic, qos=0)

    # Iniciar el bucle MQTT en un fil separat
    mqtt_client.loop_start()

    # Executa fins que l'usuari premi CTRL+C
    while not is_finished:
        time.sleep(0.1)

    print("CTRL+C premut, aturant l'execució del programa!")

    # Desconnectar i aturar el fil del client MQTT
    mqtt_client.disconnect()
    mqtt_client.loop_stop()

if __name__ == "__main__":
    main()
