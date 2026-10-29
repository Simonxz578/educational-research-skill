"""Shared strict model base avoids schema import cycles."""

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")
