from pydantic import BaseModel, Field
from typing import Union, Literal

DateType = Union[str, Literal["p1", "p2", "p3", "r1", "r2", "r3"]]

class Image(BaseModel):
    image_url: str = Field(alias="imageUrl")
    mime_type: str = Field(alias="mimeType")

class AdditionalContext(BaseModel):
    """
    Context extracted from a link.
    """
    content: str = Field(description="The string content from the link.")
    link: str = Field(description="The link from which the content was extracted.")

class RepurposedPost(BaseModel):
    """
    A specific post in a repurposed series.
    """
    content: str = Field(description="The content of the specific post.")
    index: int = Field(description="The index of the post in the series.")
