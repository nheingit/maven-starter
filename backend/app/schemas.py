from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PageMetadata(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    # Allow any additional metadata fields
    additional_fields: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        # Extract known fields
        known_fields = {'url', 'title'}
        # Store all unknown fields in additional_fields
        additional_fields = {k: v for k, v in data.items() if k not in known_fields}
        # Update data with additional_fields
        data.update({'additional_fields': additional_fields})
        super().__init__(**data)

class PageData(BaseModel):
    html: Optional[str] = None
    markdown: Optional[str] = None
    metadata: PageMetadata

class CrawlRequest(BaseModel):
    url: HttpUrl

class CrawlResponse(BaseModel):
    success: bool
    status: str
    completed: int
    total: int
    credits_used: int = Field(alias="creditsUsed")
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    data: List[PageData]

    class Config:
        populate_by_name = True
