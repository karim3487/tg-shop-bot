from datetime import datetime

from pydantic import BaseModel, Field


class ClientModel(BaseModel):
    id: int
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime

    @property
    def display_name(self) -> str:
        parts = [p for p in [self.first_name, self.last_name] if p]
        return " ".join(parts) or str(self.telegram_id)

    @property
    def is_admin(self) -> bool:
        return self.role in ("admin", "owner")

    class Config:
        from_attributes = True
