# SQLAlchemy setup
import json
from typing import Set, List

from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocketDisconnect, WebSocket

from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
from datetime import datetime

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

# Define the ProcessedAgentData table
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)


# FastAPI models
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float


class GpsData(BaseModel):
    latitude: float
    longitude: float


class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator('timestamp', mode='before')
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError("Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData


# Database model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime


# FastAPI app setup
app = FastAPI()

# WebSocket subscriptions
subscriptions: Set[WebSocket] = set()


# FastAPI WebSocket endpoint
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions.remove(websocket)


# Function to send data to subscribed users
async def send_data_to_subscribers(data):
    for websocket in subscriptions:
        await websocket.send_json(json.dumps(data))


# FastAPI CRUDL endpoints

@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    """
    Створити один або кілька записів ProcessedAgentData
    у таблиці processed_agent_data.
    Повертає створені записи.
    """

    # Створимо список значень, підготовлених для вставки
    to_insert = []
    for item in data:
        to_insert.append({
            "road_state": item.road_state,
            "x": item.agent_data.accelerometer.x,
            "y": item.agent_data.accelerometer.y,
            "z": item.agent_data.accelerometer.z,
            "latitude": item.agent_data.gps.latitude,
            "longitude": item.agent_data.gps.longitude,
            "timestamp": item.agent_data.timestamp,
        })

    # Працюємо із сесією
    db_session = SessionLocal()
    try:
        # Виконуємо вставку
        insert_stmt = processed_agent_data.insert().values(to_insert)
        result = db_session.execute(insert_stmt)
        db_session.commit()

        new_ids = []
        if result.inserted_primary_key is not None:
            new_ids.append(result.inserted_primary_key)
        else:
            pass

        created_count = len(to_insert)
        select_stmt = (
            processed_agent_data.select()
            .order_by(processed_agent_data.c.id.desc())
            .limit(created_count)
        )
        rows = db_session.execute(select_stmt).fetchall()

        rows = list(reversed(rows))

        return str(rows)
    finally:
        db_session.close()


@app.get("/processed_agent_data/{processed_agent_data_id}")
def read_processed_agent_data(processed_agent_data_id: int):
    """
    Отримати запис ProcessedAgentData за його ідентифікатором.
    """
    db_session = SessionLocal()
    try:
        select_stmt = processed_agent_data.select().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        row = db_session.execute(select_stmt).fetchone()
        if row is None:
            # Можна викликати HTTPException(404)
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="ProcessedAgentData not found")
        return ProcessedAgentDataInDB(**dict(row))
    finally:
        db_session.close()


@app.get("/processed_agent_data/")
def list_processed_agent_data():
    """
    Отримати список усіх ProcessedAgentData.
    """
    db_session = SessionLocal()
    try:
        select_stmt = processed_agent_data.select()
        rows = db_session.execute(select_stmt).fetchall()
        return [ProcessedAgentDataInDB(**dict(row)) for row in rows]
    finally:
        db_session.close()


@app.put("/processed_agent_data/{processed_agent_data_id}")
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    """
    Оновити запис ProcessedAgentData за ідентифікатором.
    """
    db_session = SessionLocal()
    try:
        update_stmt = (
            processed_agent_data.update()
            .where(processed_agent_data.c.id == processed_agent_data_id)
            .values(
                road_state=data.road_state,
                x=data.agent_data.accelerometer.x,
                y=data.agent_data.accelerometer.y,
                z=data.agent_data.accelerometer.z,
                latitude=data.agent_data.gps.latitude,
                longitude=data.agent_data.gps.longitude,
                timestamp=data.agent_data.timestamp,
            )
            .returning(processed_agent_data)
        )

        updated_row = db_session.execute(update_stmt).fetchone()
        db_session.commit()

        if updated_row is None:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404, detail="ProcessedAgentData to update not found"
            )

        return ProcessedAgentDataInDB(**dict(updated_row))
    finally:
        db_session.close()


@app.delete("/processed_agent_data/{processed_agent_data_id}")
def delete_processed_agent_data(processed_agent_data_id: int):
    """
    Видалити запис ProcessedAgentData за ідентифікатором.
    Повертає видалений запис.
    """
    db_session = SessionLocal()
    try:
        # Спочатку отримаємо те, що видаляємо (щоб повернути користувачеві)
        select_stmt = processed_agent_data.select().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        row = db_session.execute(select_stmt).fetchone()

        if row is None:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404, detail="ProcessedAgentData to delete not found"
            )

        delete_stmt = processed_agent_data.delete().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        db_session.execute(delete_stmt)
        db_session.commit()

        return ProcessedAgentDataInDB(**dict(row))
    finally:
        db_session.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
