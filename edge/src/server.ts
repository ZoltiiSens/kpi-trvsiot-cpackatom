import mqtt from "mqtt";

const MQTT_BROKER_HOST = "test.mosquitto.org";
const MQTT_BROKER_PORT = 1883;
const MQTT_TOPIC = "agent_data_topic";

const client = mqtt.connect(`mqtt://${MQTT_BROKER_HOST}:${MQTT_BROKER_PORT}`);

client.on("connect", () => {
  console.log("Connected to MQTT broker");
  client.subscribe(MQTT_TOPIC, (err) => {
    if (!err) {
      console.log(`MQTT: Subscribed to topic: ${MQTT_TOPIC}`);
    } else {
      console.error("MQTT: Failed to subscribe to topic", err);
    }
  });
});

client.on("message", (topic, message) => {
  console.log(
    `MQTT: Received message on topic ${topic}: ${message.toString()}`,
  );
});

client.on("error", (error) => {
  console.error("MQTT: error - ", error);
});

client.on("close", () => {
  console.log("MQTT: connection closed");
});
