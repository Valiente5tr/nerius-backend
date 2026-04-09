"""Gem bank schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GemCategoryRead(BaseModel):
    id: str
    name: str
    description: str | None = None
    icon: str | None = None
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class GemTagRead(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class GemCreatorRead(BaseModel):
    id: str
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class AreaRead(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class GemCardRead(BaseModel):
    """Gem summary for card display."""
    id: str
    title: str
    description: str | None = None
    icon_url: str | None = None
    gemini_url: str | None = None
    visibility: str
    is_featured: bool
    status: str
    saves_count: int = 0
    created_at: datetime
    category: GemCategoryRead | None = None
    area: AreaRead | None = None
    created_by_user: GemCreatorRead
    tags: list[GemTagRead] = []
    is_saved: bool = False

    model_config = ConfigDict(from_attributes=True)


class GemDetailRead(BaseModel):
    """Full gem detail."""
    id: str
    title: str
    description: str | None = None
    instructions: str
    icon_url: str | None = None
    gemini_url: str | None = None
    conversation_starters: list[str] | None = None
    visibility: str
    is_featured: bool
    status: str
    saves_count: int = 0
    created_at: datetime
    updated_at: datetime
    category: GemCategoryRead | None = None
    area: AreaRead | None = None
    areas: list[AreaRead] = []
    created_by_user: GemCreatorRead
    tags: list[GemTagRead] = []
    is_saved: bool = False

    model_config = ConfigDict(from_attributes=True)


class GemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=180)
    description: str | None = None
    instructions: str = Field(..., min_length=1)
    icon_url: str | None = None
    gemini_url: str | None = None
    conversation_starters: list[str] | None = None
    category_id: str | None = None
    area_id: str | None = None
    additional_area_ids: list[str] = []
    tag_names: list[str] = []
    visibility: str = "public"
    is_featured: bool = False
    status: str = "draft"


class GemUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=180)
    description: str | None = None
    instructions: str | None = Field(None, min_length=1)
    icon_url: str | None = None
    gemini_url: str | None = None
    conversation_starters: list[str] | None = None
    category_id: str | None = None
    area_id: str | None = None
    additional_area_ids: list[str] | None = None
    tag_names: list[str] | None = None
    visibility: str | None = None
    is_featured: bool | None = None
    status: str | None = None


class UserGemCollectionRead(BaseModel):
    """Saved gem in user's collection."""
    id: str
    gem: GemCardRead
    saved_at: datetime
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class GemSaveRequest(BaseModel):
    notes: str | None = None
