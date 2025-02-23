interface MqttEnvironmentUnchecked {
  MQTT_BROKER_HOST: string | undefined;
  MQTT_BROKER_PORT: string | undefined;
  MQTT_TOPIC: string | undefined;
  HUB_MQTT_TOPIC: string | undefined;
  HUB_HOST: string | undefined;
  HUB_PORT: string | undefined;
}

interface MqttEnvironment {
  MQTT_BROKER_HOST: string;
  MQTT_BROKER_PORT: number;
  MQTT_TOPIC: string;
  HUB_MQTT_TOPIC: string;
  HUB_HOST: string;
  HUB_PORT: number;
}

export function toValidMqttEnv(
  props: MqttEnvironmentUnchecked,
): MqttEnvironment {
  const error = "Invalid env.";
  if (props.MQTT_BROKER_HOST == null) throw error;
  if (props.MQTT_BROKER_PORT == null) throw error;
  if (props.MQTT_TOPIC == null) throw error;

  if (props.HUB_HOST == null) throw error;
  if (props.HUB_PORT == null) throw error;
  if (props.HUB_MQTT_TOPIC == null) throw error;

  return {
    MQTT_BROKER_HOST: props.MQTT_BROKER_HOST,
    MQTT_BROKER_PORT: parseInt(props.MQTT_BROKER_PORT, 10),
    MQTT_TOPIC: props.MQTT_TOPIC,
    HUB_MQTT_TOPIC: props.HUB_MQTT_TOPIC,
    HUB_HOST: props.HUB_HOST,
    HUB_PORT: parseInt(props.HUB_PORT, 10),
  };
}

interface AgentData {
  accelerometer: AgentDataAccelerometer;
  gps: AgentDataGps;
  timestamp: string;
}

interface AgentDataAccelerometer {
  x: number;
  y: number;
  z: number;
}

interface AgentDataGps {
  longitude: number;
  latitude: number;
}

interface ProcessedAgentData {
  road_state: "bad" | "good";
  agent_data: AgentData;
}

export function toProcessedData(props: any): ProcessedAgentData {
  const error = "Invalid data";
  if (typeof props.accelerometer.x !== "number") throw error;
  if (typeof props.accelerometer.y !== "number") throw error;
  if (typeof props.accelerometer.z !== "number") throw error;

  if (typeof props.gps.latitude !== "number") throw error;
  if (typeof props.gps.longitude !== "number") throw error;

  if (typeof props.time !== "string") throw error;

  return {
    road_state: props.accelerometer.z < 15000 ? "bad" : "good",
    agent_data: {
      accelerometer: {
        x: props.accelerometer.x,
        y: props.accelerometer.y,
        z: props.accelerometer.z,
      },
      gps: {
        latitude: props.gps.latitude,
        longitude: props.gps.longitude,
      },
      timestamp: props.time,
    },
  };
}

export async function sendViaRest(props: {
  data: ProcessedAgentData;
  url: string;
}) {
  try {
    const response = await fetch(props.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(props.data),
    });

    if (!response.ok) {
      throw new Error(`HTTP: ${response.status}`);
    }

    const responseData = await response.json();
    console.log("HTTP: Data sent successfully", responseData);
  } catch (error: any) {
    console.error("HTTP: Failed to send data", error.message);
  }
}
