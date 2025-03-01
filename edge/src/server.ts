import mqtt from "mqtt";
import { toProcessedData, toValidMqttEnv } from "./helpers";

const env = toValidMqttEnv({
  MQTT_BROKER_HOST: process.env.MQTT_BROKER_HOST,
  MQTT_BROKER_PORT: process.env.MQTT_BROKER_PORT,
  MQTT_TOPIC: process.env.MQTT_TOPIC,
  HUB_MQTT_TOPIC: process.env.HUB_MQTT_TOPIC,
  HUB_PORT: process.env.HUB_PORT,
  HUB_HOST: process.env.HUB_HOST,
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

client.on("message", async (topic, message) => {
  try {
    console.log(`MQTT: Received message on topic ${topic}.`);

    const data = await JSON.parse(message.toString());

    const processedData = toProcessedData(data);

    client.publish(env.HUB_MQTT_TOPIC, JSON.stringify(processedData), (err) => {
      if (!err) {
        console.log(
          `MQTT: Processed data published to topic: ${env.HUB_MQTT_TOPIC}`,
        );
      } else {
        console.error("MQTT: Failed to publish processed data", err);
      }
    });

    console.log("MQTT: message processed.");
  } catch (err: any) {
    console.log(err.message);
  }
});

client.on("error", (err) => {
  console.log(`mqtt://${env.MQTT_BROKER_HOST}:${env.MQTT_BROKER_PORT}`);
  console.error("MQTT: error - ", err);
});

client.on("close", () => {
  console.log("MQTT: connection closed");
});
