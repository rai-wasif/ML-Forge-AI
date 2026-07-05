from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    message: str
    dataset_id: int | None = None
    project_id: int | None = None


class AgentChatResponse(BaseModel):
    message: str
    plan: list[str]
    dataset_id: int
    project_id: int
    stages: dict
    artifacts: dict
