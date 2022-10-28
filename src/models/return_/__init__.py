from pydantic import BaseModel


class Return(BaseModel):
    item_qid: str = ""
    uploaded_now: bool
