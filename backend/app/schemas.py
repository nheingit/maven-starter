from pydantic import BaseModel
from typing import Optional, List

class Parameter(BaseModel):
    id: int
    name: str
    type: Optional[str]
    default_value: Optional[str]
    description: Optional[str]

class Example(BaseModel):
    id: int
    code: str
    description: Optional[str]

class Function(BaseModel):
    id: int
    name: str
    arity: int
    return_type: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    parameters: List[Parameter] = []
    examples: List[Example] = []

class Module(BaseModel):
    id: int
    name: str
    description: Optional[str]
    functions: List[Function] = []

class Application(BaseModel):
    id: int
    name: str
    version: str
    description: Optional[str]
    modules: List[Module] = []

class ScrapeRequest(BaseModel):
    url: str
