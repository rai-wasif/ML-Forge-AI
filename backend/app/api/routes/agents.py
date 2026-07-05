from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.agents import AgentChatRequest, AgentChatResponse
from app.services import agent_service


router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/chat", response_model=AgentChatResponse)
def chat_with_agents(request: AgentChatRequest, db: Session = Depends(get_db)):
    return agent_service.chat(db, request)
