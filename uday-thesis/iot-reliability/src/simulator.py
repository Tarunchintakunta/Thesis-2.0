import time
import random

def simulate_mqtt_transmission(qos_level):
    duration = 5
    messages_sent = 1000
    print(f"Starting simulation: QoS {qos_level}")
    # Simulation placeholder
    time.sleep(1)
    delivered = messages_sent if qos_level == 1 else messages_sent - random.randint(0, 50)
    print(f"Simulation ended. Delivered: {delivered}/{messages_sent}")

if __name__ == "__main__":
    simulate_mqtt_transmission(0)
    simulate_mqtt_transmission(1)
