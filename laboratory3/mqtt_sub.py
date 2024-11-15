import config
import signal
import time
import paho.mqtt.client as mqtt

is_finished = False

def on_sigint(signal_received, frame):
    global is_finished
    is_finished = True

def on_connect(client, userdata, flags, rc):
    print("Connected to the server!")

def on_message(client, userdata, message):
    topic = message.topic
    msg = message.payload.decode()
    print("Message='{}' received on topic='{}'.".format(msg, topic))

def main():
    global is_finished

    # Retrieve configuration information
    mqtt_server = config.mqtt_config["mqtt_server"]
    mqtt_topic = config.mqtt_config["mqtt_topic"]
    mqtt_port = config.mqtt_config["mqtt_port"]

    # Register the keyboard interrupt CTRL+C
    signal.signal(signal.SIGINT, on_sigint)

    # Create MQTT client
    mqtt_client = mqtt.Client()

    # Connect the MQTT client to the server
    mqtt_client.connect(mqtt_server, port=mqtt_port)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Read the topic from keyboard
    topic = input("Enter the topic you want to subscribe to: ")

    # If the topic is empty, use the default topic
    if not topic:
        print("Empty topic, using default topic='{}'.".format(mqtt_topic))
        topic = mqtt_topic

    # Subscribe to the topic with QoS=0
    mqtt_client.subscribe(topic, qos=0)

    # Start the MQTT thread
    mqtt_client.loop_start()

    # Loop until the user presses CTRL+C
    while not is_finished:
        # Sleep for 100 ms
        time.sleep(0.1)

    print("You pressed CTRL+C, stopping program execution!")

    # Disconnect from the MQTT server
    mqtt_client.disconnect()

    # Stop the MQTT thread
    mqtt_client.loop_stop()

if __name__ == "__main__":
    main()
