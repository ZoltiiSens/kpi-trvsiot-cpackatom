"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.toValidMqttEnv = toValidMqttEnv;
exports.toProcessedData = toProcessedData;
exports.sendViaRest = sendViaRest;
function toValidMqttEnv(props) {
    const error = "Invalid env.";
    if (props.MQTT_BROKER_HOST == null)
        throw error;
    if (props.MQTT_BROKER_PORT == null)
        throw error;
    if (props.MQTT_TOPIC == null)
        throw error;
    if (props.HUB_HOST == null)
        throw error;
    if (props.HUB_PORT == null)
        throw error;
    if (props.HUB_MQTT_TOPIC == null)
        throw error;
    return {
        MQTT_BROKER_HOST: props.MQTT_BROKER_HOST,
        MQTT_BROKER_PORT: parseInt(props.MQTT_BROKER_PORT, 10),
        MQTT_TOPIC: props.MQTT_TOPIC,
        HUB_MQTT_TOPIC: props.HUB_MQTT_TOPIC,
        HUB_HOST: props.HUB_HOST,
        HUB_PORT: parseInt(props.HUB_PORT, 10),
    };
}
function toProcessedData(props) {
    const error = "Invalid data";
    if (typeof props.accelerometer.x !== "number")
        throw error;
    if (typeof props.accelerometer.y !== "number")
        throw error;
    if (typeof props.accelerometer.z !== "number")
        throw error;
    if (typeof props.gps.latitude !== "number")
        throw error;
    if (typeof props.gps.longitude !== "number")
        throw error;
    if (typeof props.time !== "string")
        throw error;
    return {
        road_state: props.accelerometer.z < 15000 ? "bad" : "good",
        agent_data: {
            user_id: 1,
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
function sendViaRest(props) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const response = yield fetch(props.url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(props.data),
            });
            if (!response.ok) {
                throw new Error(`HTTP: ${response.status}`);
            }
            const responseData = yield response.json();
            console.log("HTTP: Data sent successfully", responseData);
        }
        catch (error) {
            console.error("HTTP: Failed to send data", error.message);
        }
    });
}
