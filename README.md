# xbee-sensor-lab

The Digi XBee Sensor Lab is a demonstration of cellular IoT using a variety of different environmental sensors and industrial actuators. It was created as a booth demo for trade shows, and creates a hands-on experience for interacting with wireless sensors while watching the real-time data change on a cloud-attached dashboard display. Current devices measure air quality, distance, location, accelerations, heartrate, compass heading, RFID tags, keypad entry, light, loudness, soil moisture, weight, SMS display, relay actuation, performing Bluetooth beaconing and reading Bluetooth sensors.

Each sensor is from Sparkfun Electronics. They connect directly to Digi XBee 3 Global Cellular modems via I2C. These XBee modules use MicroPython onboard to accept the raw data, transform it to readings, manage timings, upload to Remote Manager, configure the XBee and provide resiliency. Data posted to Remote Manager data streams is presented via a secure API, and we seperately implemented a custom dashboard to display the data as it happens.


XBee Sensor Lab at Embedded World 2023: https://youtu.be/zfkEAhnPG1s

XBee Sensor Lab at CES 2024: https://youtu.be/LSKDwjhVuL0
