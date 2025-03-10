from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from models import Sensor, create_db_and_tables, engine

app = FastAPI(title="API per Pseudo Sensori")

# Schema per aggiornamenti parziali (PATCH)
class SensorUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[float] = None
    timestamp: Optional[datetime] = None

# All'avvio dell'applicazione, creiamo le tabelle se non esistono
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- CREATE --- 
@app.post("/sensors", response_model=Sensor, status_code=status.HTTP_201_CREATED)
def create_sensor(sensor: Sensor):
    with Session(engine) as session:
        session.add(sensor)
        session.commit()
        session.refresh(sensor)
        return sensor

# --- READ: tutti i sensori ---
@app.get("/sensors", response_model=List[Sensor])
def read_sensors():
    with Session(engine) as session:
        sensors = session.exec(select(Sensor)).all()
        return sensors

# --- READ: singolo sensore ---
@app.get("/sensors/{sensor_id}", response_model=Sensor)
def get_sensor(sensor_id: int):
    with Session(engine) as session:
        sensor = session.get(Sensor, sensor_id)
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensore non trovato")
        return sensor
    
@app.get("/sensors/by_name/{sensor_name}", response_model=List[Sensor])
def get_sensor_by_name(sensor_name: str):
    with Session(engine) as session:
        statement = select(Sensor).where(Sensor.name == sensor_name)
        sensors = session.exec(statement).all()
        if not sensors:
            raise HTTPException(status_code=404, detail="Sensore non trovato")
        return sensors

# --- UPDATE: aggiornamento completo (PUT) ---
@app.put("/sensors/{sensor_id}", response_model=Sensor)
def update_sensor(sensor_id: int, sensor_data: Sensor):
    with Session(engine) as session:
        sensor = session.get(Sensor, sensor_id)
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensore non trovato")
        sensor.name = sensor_data.name
        sensor.value = sensor_data.value
        sensor.timestamp = sensor_data.timestamp
        session.add(sensor)
        session.commit()
        session.refresh(sensor)
        return sensor

# --- PATCH: aggiornamento parziale ---
@app.patch("/sensors/{sensor_id}", response_model=Sensor)
def patch_sensor(sensor_id: int, sensor_update: SensorUpdate):
    with Session(engine) as session:
        sensor = session.get(Sensor, sensor_id)
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensore non trovato")
        update_data = sensor_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(sensor, key, value)
        session.add(sensor)
        session.commit()
        session.refresh(sensor)
        return sensor

# --- DELETE: cancellazione del sensore ---
@app.delete("/sensors/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor(sensor_id: int):
    with Session(engine) as session:
        sensor = session.get(Sensor, sensor_id)
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensore non trovato")
        session.delete(sensor)
        session.commit()
        return None