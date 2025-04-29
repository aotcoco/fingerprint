import time
import serial
import board
import adafruit_fingerprint
import RPi.GPIO as GPIO  # GPIO library

# Setup GPIO
RELAY_PIN = 17  # Use GPIO17 (pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

# Setup UART communication
uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)


def unlock_door():
    """Activate relay (unlock door) for 3 seconds"""
    print("🔓 Door unlocked!")
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("🔒 Door locked again.")


def get_fingerprint():
    """Scans and identifies fingerprint"""
    print("Waiting for finger...")

    while finger.get_image() != adafruit_fingerprint.OK:
        pass

    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("Failed to convert image")
        return False

    if finger.finger_search() != adafruit_fingerprint.OK:
        print("No match found.")
        return False

    print("✅ Match found!")
    print("Fingerprint ID:", finger.finger_id)
    print("Confidence:", finger.confidence)

    unlock_door()
    return True


def enroll_fingerprint(location):
    print("Enrolling fingerprint at ID", location)

    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...")
        else:
            print("Remove finger, then place same finger again...")

        while True:
            if finger.get_image() == adafruit_fingerprint.OK:
                break

        if finger.image_2_tz(fingerimg) != adafruit_fingerprint.OK:
            print("Error processing fingerprint.")
            return False

        while finger.get_image() != adafruit_fingerprint.NOFINGER:
            pass
        time.sleep(1)

    if finger.create_model() != adafruit_fingerprint.OK:
        print("Failed to create fingerprint model.")
        return False

    if finger.store_model(location) != adafruit_fingerprint.OK:
        print("Failed to store fingerprint.")
        return False

    print("✅ Fingerprint enrolled successfully!")
    return True


def delete_fingerprint(location):
    if finger.delete_model(location) == adafruit_fingerprint.OK:
        print(f"🗑️ Fingerprint ID {location} deleted.")
    else:
        print("❌ Deletion failed.")


def list_templates():
    template_count = finger.read_templates()
    print("Stored fingerprint IDs:", finger.templates)


# Main Menu
if __name__ == "__main__":
    try:
        while True:
            print("\n--- Fingerprint Sensor Menu ---")
            print("1. Scan Finger")
            print("2. Enroll New Fingerprint")
            print("3. Delete Fingerprint")
            print("4. List Stored Fingerprints")
            print("5. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                get_fingerprint()
            elif choice == "2":
                location = int(input("Enter ID (1-127): "))
                enroll_fingerprint(location)
            elif choice == "3":
                location = int(input("Enter ID to delete: "))
                delete_fingerprint(location)
            elif choice == "4":
                list_templates()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

    except KeyboardInterrupt:
        print("\n[CTRL+C] Exiting...")
    finally:
        GPIO.cleanup()
