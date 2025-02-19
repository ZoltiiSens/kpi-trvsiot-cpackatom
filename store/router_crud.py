from typing import List
from fastapi import APIRouter, HTTPException

from database import SessionLocal, processed_agent_data
from models import ProcessedAgentData, ProcessedAgentDataInDB


# FastAPI router
router = APIRouter(prefix='/processed_agent_data')


# FastAPI CRUDL endpoints
@router.post("/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
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

    db_session = SessionLocal()
    try:
        insert_stmt = processed_agent_data.insert().values(to_insert)
        db_session.execute(insert_stmt)
        db_session.commit()

        created_count = len(to_insert)
        select_stmt = (
            processed_agent_data.select()
            .order_by(processed_agent_data.c.id.desc())
            .limit(created_count)
        )
        rows = db_session.execute(select_stmt).fetchall()
        print(123)
        print(rows)
        # rows = list(reversed(rows))
        # print(456)
        # print(rows)

        return str(rows)
    finally:
        db_session.close()


@router.get("/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int):
    db_session = SessionLocal()
    try:
        select_stmt = processed_agent_data.select().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        row = db_session.execute(select_stmt).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="ProcessedAgentData not found")
        return row
    finally:
        db_session.close()


@router.get("/", response_model=List[ProcessedAgentDataInDB])
def list_processed_agent_data():
    db_session = SessionLocal()
    try:
        select_stmt = processed_agent_data.select()
        rows = db_session.execute(select_stmt).fetchall()
        return rows
    finally:
        db_session.close()


@router.put("/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
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
            raise HTTPException(
                status_code=404, detail="ProcessedAgentData to update not found"
            )

        return updated_row
    finally:
        db_session.close()


@router.delete("/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def delete_processed_agent_data(processed_agent_data_id: int):
    db_session = SessionLocal()
    try:
        select_stmt = processed_agent_data.select().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        row = db_session.execute(select_stmt).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404, detail="ProcessedAgentData to delete not found"
            )

        delete_stmt = processed_agent_data.delete().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        db_session.execute(delete_stmt)
        db_session.commit()

        return row
    finally:
        db_session.close()
