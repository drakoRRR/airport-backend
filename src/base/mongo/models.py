from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime


class PyObjectId(ObjectId):
    """Custom ObjectId field for Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class Review(BaseModel):
    """Model representing reviews for MongoDB."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    tour_id: str  # ID of the tour being reviewed
    user_id: str  # ID of the user who made the review
    rating: int  # Rating out of 5
    comment: Optional[str] = None  # Optional comment
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            ObjectId: str
        }


class Image(BaseModel):
    """Model representing images for MongoDB."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    tour_id: str
    url: str
    description: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            ObjectId: str
        }
