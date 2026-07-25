from pydantic import BaseModel


class VideoJobSubmitResponse(BaseModel):
    job_id: str
    status: str
    detail: str


class VideoJobStatusResponse(BaseModel):
    job_id: str
    status: str
    output_path: str | None = None
    error: str | None = None
