import config
import paho.mqtt.client as mqtt

def main():
    # Retrieve MQTT configuration information
    mqtt_server = config.mqtt_config["mqtt_server"]
    mqtt_topic = config.mqtt_config["mqtt_topic"]
    mqtt_name = config.mqtt_config["mqtt_name"]
    mqtt_port = config.mqtt_config["mqtt_port"]

    # Create MQTT client
    mqtt_client = mqtt.Client(mqtt_name)

    # Connect the client to the MQTT server
    mqtt_client.connect(mqtt_server, port=mqtt_port, keepalive=60, bind_address="")

    # Start the MQTT thread
    mqtt_client.loop_start()

    # Read the topic from keyboard
    topic = input("Enter the topic you want to publish to: ")

    # If the topic is empty, use the default one
    if not topic:
        print("Empty topic, using the default topic (topic={})".format(mqtt_topic))
        topic = mqtt_topic

    is_finished = False
    while not is_finished:
        message = input("Enter the message you want to send: ")
        if not message:
            # Mark the end of the program
            print("No message entered, ending the program!")
            is_finished = True
        else:
            # Publish message to the topic with QoS=0 and Retain=False
            print("Publishing message='{}' to topic='{}'.".format(message, topic))
            mqtt_client.publish(topic, payload=message, qos=0, retain=False)

    # Disconnect from the MQTT server
    mqtt_client.disconnect()

    # Stop the MQTT thread
    mqtt_client.loop_stop()

if __name__ == "__main__":
    main()
