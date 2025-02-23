interface MqttEnvironmentUnchecked {
  MQTT_BROKER_HOST: string | undefined;
  MQTT_BROKER_PORT: string | undefined;
  MQTT_TOPIC: string | undefined;
}

interface MqttEnvironment {
  MQTT_BROKER_HOST: string;
  MQTT_BROKER_PORT: number;
  MQTT_TOPIC: string;
}

export function toValidMqttEnv(
  props: MqttEnvironmentUnchecked,
): MqttEnvironment {
  const error = "Invalid env.";
  if (props.MQTT_BROKER_HOST == null) throw error;
  if (props.MQTT_BROKER_PORT == null) throw error;
  if (props.MQTT_TOPIC == null) throw error;

  return {
    MQTT_BROKER_HOST: props.MQTT_BROKER_HOST,
    MQTT_BROKER_PORT: parseInt(props.MQTT_BROKER_PORT, 10),
    MQTT_TOPIC: props.MQTT_TOPIC,
  };
}
