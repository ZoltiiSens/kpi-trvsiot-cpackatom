from typing import List
from fastapi import APIRouter, HTTPException
from scipy.signal import find_peaks
from google_sheets_operate import google_read_values, google_insert_values

from database import SessionLocal, processed_agent_data
from models import ProcessedAgentData, ProcessedAgentDataInDB
from router_ws import send_data_to_subscribers

# FastAPI router
router = APIRouter(prefix='/processed_agent_data')


# FastAPI CRUDL endpoints
@router.post("/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    z_values = [d.agent_data.accelerometer.z for d in data]

    peak_distance = 10
    peak_height = 16670
    peak_prominence = 100

    peaks_max, _ = find_peaks(
        z_values,
        distance=peak_distance,
        height=peak_height,
        prominence=peak_prominence
    )

    inverted_z = [-1 * z for z in z_values]
    pit_height = -16660
    pits_min, _ = find_peaks(
        inverted_z,
        distance=peak_distance,
        height=(-1) * pit_height,
        prominence=peak_prominence
    )

    to_insert_excel = []
    for i, item in enumerate(data):
        to_insert_excel.append([
            item.road_state,
            item.agent_data.accelerometer.x,
            item.agent_data.accelerometer.y,
            item.agent_data.accelerometer.z,
            item.agent_data.gps.latitude,
            item.agent_data.gps.longitude,
            str(item.agent_data.timestamp),
            i in peaks_max,
            i in pits_min
        ])
    google_insert_values(list(reversed(to_insert_excel)), len(google_read_values()) + 1)

    to_insert = []
    for i, item in enumerate(data):
        to_insert.append({
            "road_state": item.road_state,
            "x": item.agent_data.accelerometer.x,
            "y": item.agent_data.accelerometer.y,
            "z": item.agent_data.accelerometer.z,
            "latitude": item.agent_data.gps.latitude,
            "longitude": item.agent_data.gps.longitude,
            "timestamp": str(item.agent_data.timestamp),
            "peak": i in peaks_max,
            "pit": i in pits_min
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
        # print(type(rows), ';;;;;;;')
        await send_data_to_subscribers(to_insert)
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
