from pydantic import BaseModel, field_validator

class RunCreationResponse(BaseModel):
    thread_id: str
    run_id: str