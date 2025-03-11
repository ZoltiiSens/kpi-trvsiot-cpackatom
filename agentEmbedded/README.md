# Agent code for Hackaton

Agent code for BeagleBone Black microcontroller, that demonstrates accelerometer 
and gps data transfer over MQTT protocol. Data is faked, accelerometer comes 
from respective csv file, while gps is faked with gpsfake() with gpsdata file.

Install requirements and run program with commands below. Setup is described in 
tech documentation.

---

## Requirements
- paho.mqtt
- marshmallow
- etc.

```
pip3 install -r requirements.txt
```

---

## Config
**Attention: gpsfake() uses 2948 port by default to ensure conflict-free behaviour.
Also, BBB is meant to be connected via USB cable.**
```
vim config.py
```

---

## Start
```
python3 main.py
```

---

## Credits
Team 14:
- Skorobagatko I.A. IO-13
- Maruzhenko I.S. IO-13