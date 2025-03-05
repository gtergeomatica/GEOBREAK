import os
from datetime import datetime
from typing import Optional
import time
from sqlmodel import SQLModel, Field, create_engine

# Stringa di connessione al database: puoi impostare la variabile d'ambiente DATABASE_URL oppure usare il default
DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@postgres:5432/sensordb")
max_retries = 10
retry_count = 0
while True:
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        print("Connessione al database riuscita")
        break  # Esce dal ciclo se tutto va bene
    except Exception as e:
        retry_count += 1
        print(f"Connessione al database fallita (tentativo {retry_count}/{max_retries}). Riprovo tra 5 secondi...")
        time.sleep(5)
        if retry_count >= max_retries:
            print("Numero massimo di tentativi raggiunto. Uscita.")
            raise e
        
# Definizione del modello per il sensore
class Sensor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Funzione per creare il database e le tabelle con retry
def create_db_and_tables():
    max_retries = 10
    retry_count = 0
    while True:
        try:
            SQLModel.metadata.create_all(engine)
            print("Connessione al database riuscita e tabelle create.")
            break  # Esce dal ciclo se tutto va bene
        except Exception as e:
            retry_count += 1
            print(f"Connessione al database fallita (tentativo {retry_count}/{max_retries}). Riprovo tra 5 secondi...")
            time.sleep(5)
            if retry_count >= max_retries:
                print("Numero massimo di tentativi raggiunto. Uscita.")
                raise e
