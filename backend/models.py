from sqlalchemy import Column, Integer, String, JSON, Text, DateTime, LargeBinary
from sqlalchemy.orm import validates
from datetime import datetime
from typing import List, Dict, Any, Optional

from db import Base


class Question(Base):
    """ORM model representing a parsed MCQ."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_option = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    source_file = Column(String(255), nullable=True)
    page_no = Column(Integer, nullable=True)
    image_data = Column(LargeBinary, nullable=True)  # Store image as base64 or binary
    image_type = Column(String(50), nullable=True)  # e.g., 'png', 'jpg'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @validates("question")
    def validate_question(self, key: str, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("Question text cannot be empty")
        return value

    @validates("options")
    def validate_options(self, key: str, value: List[str]) -> List[str]:
        if not isinstance(value, list) or len(value) < 2:
            raise ValueError("Each MCQ must provide at least two options")
        cleaned = [str(opt).strip() for opt in value if str(opt).strip()]
        if len(cleaned) < 2:
            raise ValueError("Options cannot all be blank")
        return cleaned

    @validates("correct_option")
    def validate_correct_option(self, key: str, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 0:
            raise ValueError("Correct option index cannot be negative")
        return value

    def to_dict(self) -> Dict[str, Any]:
        import base64
        image_url = None
        if self.image_data and self.image_type:
            # Convert binary image to base64 data URL
            image_b64 = base64.b64encode(self.image_data).decode('utf-8')
            image_url = f"data:image/{self.image_type};base64,{image_b64}"
        
        return {
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "correct_option": self.correct_option,
            "explanation": self.explanation,
            "source_file": self.source_file,
            "page_no": self.page_no,
            "image_url": image_url,  # Include image as data URL
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
