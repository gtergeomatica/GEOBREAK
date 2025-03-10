import requests
import random
import time
from datetime import datetime
import os

# Modifica questa variabile in base all'URL in cui l'API è in esecuzione
BASE_URL = os.getenv("BASE_BACKEND_URL","http://localhost:8000")

while True:
    sensor_data = {
        "name": f"Sensor-{random.randint(1, 5)}",
        "value": round(random.uniform(0, 100), 2),
        "timestamp": datetime.now().isoformat()
    }
    try:
        response = requests.post(f"{BASE_URL}/sensors", json=sensor_data)
        if response.status_code == 201:
            print("Sensor creato:", response.json())
        else:
            print("Errore nella creazione del sensor:", response.status_code, response.text)
    except Exception as e:
        print("Eccezione durante la richiesta:", e)
    
    time.sleep(1)  # Attende 1 secondo prima della prossima iterazione
