from dataclasses import field
import bleach.sanitizer
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator

import bleach

class Entry(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the entry (UUID)."
    )
    work: str = Field(
        ...,
        max_length=256,
        description="What did you work on today?"
    )
    struggle: str = Field(
        ...,
        max_length=256,
        description="What’s one thing you struggled with today?"
    )
    intention: str = Field(
        ...,
        max_length=256,
        description="What will you study/work on tomorrow?"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entry was created."
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entry was last updated."
    )
    schema_version: int = Field(
        default=1,
        description="Version of the schema used to represent the entry."
    )

    
    @field_validator("work", "struggle", "intention")
    @classmethod
    def no_empty_strings(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace.")
        return v


    @field_validator("work", "struggle", "intention", mode="before")
    def sanitize_html(cls, value: str) -> str:
         return bleach.clean(value, tags=[], attributes={}, strip=True)


    # @field_validator("created_at", "updated_at")
    # def validate_datetime(cls, value):
    #     if not isinstance(value, datetime):
    #         raise ValueError("Timestamp must be a datetime object.")
    #     return value


    # Optional: add a partition key if your Cosmos DB collection requires it
    # partition_key: str = Field(..., description="Partition key for the entry.")

    class Config:
        # This can help with how the model serializes field names if needed by Cosmos DB.
        # For example, if Cosmos DB requires a specific field naming convention.
        # allow_population_by_field_name = True
        pass
