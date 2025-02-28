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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mqtt_1 = __importDefault(require("mqtt"));
const helpers_1 = require("./helpers");
const env = (0, helpers_1.toValidMqttEnv)({
    MQTT_BROKER_HOST: process.env.MQTT_BROKER_HOST,
    MQTT_BROKER_PORT: process.env.MQTT_BROKER_PORT,
    MQTT_TOPIC: process.env.MQTT_TOPIC,
    HUB_MQTT_TOPIC: process.env.HUB_MQTT_TOPIC,
    HUB_PORT: process.env.HUB_PORT,
    HUB_HOST: process.env.HUB_HOST,
});
const client = mqtt_1.default.connect(`mqtt://${env.MQTT_BROKER_HOST}:${env.MQTT_BROKER_PORT}`);
client.on("connect", () => {
    console.log("Connected to MQTT broker");
    client.subscribe(env.MQTT_TOPIC, (err) => {
        if (!err) {
            console.log(`MQTT: Subscribed to topic: ${env.MQTT_TOPIC}`);
        }
        else {
            console.error("MQTT: Failed to subscribe to topic", err);
        }
    });
});
client.on("message", (topic, message) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        console.log(`MQTT: Received message on topic ${topic}.`);
        const data = yield JSON.parse(message.toString());
        const processedData = (0, helpers_1.toProcessedData)(data);
        // console.log(JSON.stringify(processedData));
        client.publish(env.HUB_MQTT_TOPIC, JSON.stringify(processedData), (err) => {
            if (!err) {
                console.log(`MQTT: Processed data published to topic: ${env.HUB_MQTT_TOPIC}`);
            }
            else {
                console.error("MQTT: Failed to publish processed data", err);
            }
        });
        // yield (0, helpers_1.sendViaRest)({
        //     data: processedData,
        //     url: `${env.HUB_HOST}:${env.HUB_PORT}`,
        // });
        console.log("MQTT: message processed.");
    }
    catch (err) {
        console.log(err.message);
    }
}));
client.on("error", (err) => {
    console.log(`mqtt://${env.MQTT_BROKER_HOST}:${env.MQTT_BROKER_PORT}`);
    console.error("MQTT: error - ", err);
});
client.on("close", () => {
    console.log("MQTT: connection closed");
});
