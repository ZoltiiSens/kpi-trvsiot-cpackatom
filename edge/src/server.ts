import mqtt from "mqtt";
import { toValidMqttEnv } from "./helpers";

const env = toValidMqttEnv({
  MQTT_BROKER_HOST: process.env.MQTT_BROKER_HOST,
  MQTT_BROKER_PORT: process.env.MQTT_BROKER_PORT,
  MQTT_TOPIC: process.env.MQTT_TOPIC,
});

const client = mqtt.connect(
  `mqtt://${env.MQTT_BROKER_HOST}:${env.MQTT_BROKER_PORT}`,
);

client.on("connect", () => {
  console.log("Connected to MQTT broker");
  client.subscribe(env.MQTT_TOPIC, (err) => {
    if (!err) {
      console.log(`MQTT: Subscribed to topic: ${env.MQTT_TOPIC}`);
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
