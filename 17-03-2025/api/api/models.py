import os
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine

# Stringa di connessione al database: puoi impostare la variabile d'ambiente DATABASE_URL oppure usare il default
DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@postgres:5432/sensordb")
engine = create_engine(DATABASE_URL, echo=True)

# Definizione del modello per il sensore
class Sensor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Funzione per creare il database e le tabelle
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
