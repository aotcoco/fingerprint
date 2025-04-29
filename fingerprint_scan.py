import serial
import adafruit_fingerprint

# Connect to serial port
uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

print("✅ Fingerprint sensor initialized")

# Try basic communication
if finger.read_templates() != adafruit_fingerprint.OK:
    print("❌ Failed to communicate with fingerprint sensor")
else:
    print("✅ Sensor is ready. Stored templates:", finger.templates)
