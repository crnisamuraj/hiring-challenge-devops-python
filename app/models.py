from enum import Enum
from datetime import datetime
from ipaddress import IPv4Address
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ServerState(str, Enum):
    active = "active"
    offline = "offline"
    retired = "retired"

class ServerBase(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: IPv4Address
    state: ServerState

class ServerCreate(ServerBase):
    pass

class ServerUpdate(BaseModel):
    hostname: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[IPv4Address] = None
    state: Optional[ServerState] = None

class Server(ServerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
