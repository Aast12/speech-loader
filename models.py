from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class Audio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    internet_archive_item_id: str
    internet_archive_file_id: str
    file_path: str
    file_size: int
    processed: bool = Field(default=False)
    duration: int
    rms: float
    dbfs: float
    max_dbfs: float
    source_date: Optional[datetime] = Field(default=None, nullable=False)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
