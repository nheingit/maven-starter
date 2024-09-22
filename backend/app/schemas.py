from pydantic import BaseModel
class BlogPost(BaseModel):
    id: int
    title: str
    content: str