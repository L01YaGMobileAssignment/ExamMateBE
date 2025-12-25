from pydantic import BaseModel




class Schedule(BaseModel):
    title: str
    description: str
    start_date: int | None = None
    end_date: int | None = None

class ScheduleInDB(Schedule):
    id: str
    created_at: int
    updated_at: int