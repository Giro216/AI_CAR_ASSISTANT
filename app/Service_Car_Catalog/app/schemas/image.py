from typing import Optional

from pydantic import BaseModel, Field


class ImageResponse(BaseModel):
    title: str = Field(..., max_length=127)
    imageUrl: str = Field(..., max_length=2048)
    thumbnailUrl: Optional[str] = None
    imageWidth: int = 0
    imageHeight: int = 0
    source: str = Field(default="", max_length=127)
    domain: str = Field(default="", max_length=127)
    link: str = Field(default="", max_length=2048)
    position: int = 0
    # localFilePath: Optional[str] = Field(default=None, max_length=4096)
