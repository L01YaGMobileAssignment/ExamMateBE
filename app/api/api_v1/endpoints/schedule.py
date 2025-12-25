from fastapi import APIRouter, HTTPException
from app.api.deps import CurrentUser
from app.schemas.schedule import Schedule, ScheduleInDB
import app.crud.schedule as schedule_crud

router = APIRouter()

@router.get("/schedule", response_model=list[ScheduleInDB])
async def get_schedule(current_user: CurrentUser):
    return schedule_crud.get_schedule(current_user)

@router.get("/schedule/{schedule_id}", response_model=ScheduleInDB)
async def get_schedule_by_id(current_user: CurrentUser, schedule_id: str):
    schedule = schedule_crud.get_schedule_by_id(current_user, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.post("/schedule", response_model=ScheduleInDB)
async def create_schedule(current_user: CurrentUser, request: Schedule):
    return schedule_crud.create_schedule(current_user, request)

@router.put("/schedule/{schedule_id}", response_model=ScheduleInDB)
async def update_schedule(current_user: CurrentUser, schedule_id: str, request: Schedule):
    if schedule_crud.get_schedule_by_id(current_user, schedule_id) is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule_crud.update_schedule(current_user, schedule_id, request)

@router.delete("/schedule/{schedule_id}")
async def delete_schedule(current_user: CurrentUser, schedule_id: str):
    if schedule_crud.get_schedule_by_id(current_user, schedule_id) is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule_crud.delete_schedule(current_user, schedule_id)
    return  {"message": "Document deleted successfully."}