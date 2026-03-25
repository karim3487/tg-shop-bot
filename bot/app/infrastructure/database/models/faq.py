from pydantic import BaseModel


class FAQItemModel(BaseModel):
    id: int
    question: str
    answer: str
    is_active: bool = True
