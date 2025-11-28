"""FastAPI application exposing PDF upload, question listing, and quiz endpoints."""

import json
import logging
import os
import re
from datetime import datetime
from typing import List, Optional

import requests
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from db import Base, SessionLocal, engine, get_db
from extractor import PDFExtractionError, extract_questions_from_pdf, extract_answer_key_from_pdf
from groq_ai import (
    generate_explanation as groq_generate_explanation,
    generate_feedback as groq_generate_feedback,
    generate_hint as groq_generate_hint,
    GroqAIUnavailable,
)
from models import Question


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="ACCA MCQ API",
    description="API for uploading, storing, and quizzing ACCA MCQs",
    version="1.0.0",
)

raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for file:// protocol support
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Backend is running"}


class QuestionDTO(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_option: Optional[int]
    explanation: Optional[str]
    source_file: Optional[str]
    page_no: Optional[int]
    image_url: Optional[str] = None  # Base64 encoded image data URL

    class Config:
        orm_mode = True


class UploadResponse(BaseModel):
    status: str
    message: str
    saved_count: int
    total_parsed: int


class QuizResponse(BaseModel):
    total: int
    questions: List[QuestionDTO]


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")


@app.exception_handler(ValueError)
async def handle_value_error(_, exc: ValueError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def handle_uncaught(_, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file containing MCQs"),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    logger.info(f"Starting PDF extraction for {file.filename} ({len(contents)} bytes)")
    
    try:
        parsed_questions = extract_questions_from_pdf(contents)
        logger.info(f"Extracted {len(parsed_questions)} questions from {file.filename}")
    except PDFExtractionError as exc:
        logger.error(f"PDF extraction error: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected extraction error: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PDF extraction failed") from exc

    if not parsed_questions:
        logger.warning(f"No questions extracted from {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No MCQs could be extracted from the PDF. Please ensure the PDF contains properly formatted MCQs.",
        )

    saved = 0
    for record in parsed_questions:
        try:
            # Store all question data INCLUDING image data if available
            question = Question(
                question=record.get("question"),
                options=record.get("options", []),
                correct_option=record.get("correct_option"),  # IMPORTANT: Store the answer!
                explanation=record.get("explanation", ""),
                source_file=file.filename,
                page_no=record.get("page_no"),
                image_data=record.get("image_data"),  # Store image if available
                image_type=record.get("image_type"),  # Store image type if available
            )
            db.add(question)
            saved += 1
            has_image = "✓" if record.get("image_data") else "✗"
            logger.debug(f"Saved Q: {record.get('question')[:40]}... Answer: {record.get('correct_option')} Image: {has_image}")
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Failed to persist question: {str(exc)}", exc_info=exc)

    db.commit()
    logger.info(f"Saved {saved} questions to database")
    background_tasks.add_task(generate_explanations, file.filename)

    return UploadResponse(
        status="success",
        message=f"Successfully processed {saved} questions from {file.filename}",
        saved_count=saved,
        total_parsed=len(parsed_questions),
    )


@app.post("/upload-answer-key")
async def upload_answer_key(
    file: UploadFile = File(..., description="PDF file containing answer key"),
):
    """Upload and validate an answer key PDF using AI"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    logger.info(f"Processing answer key PDF: {file.filename} ({len(contents)} bytes)")
    
    try:
        result = extract_answer_key_from_pdf(contents)
        
        if result.get("status") == "success":
            logger.info(f"✅ Answer key validated: {result.get('message')}")
            return {
                "status": "success",
                "message": result.get("message"),
                "answer_key": result.get("answer_key"),
                "file_name": file.filename
            }
        else:
            logger.warning(f"⚠️ Answer key validation failed: {result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.get("message", "Failed to validate answer key")
            )
            
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error processing answer key: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process answer key PDF"
        ) from exc


@app.get("/questions", response_model=List[QuestionDTO])
def list_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        limit = max(1, min(limit, 200))
        records = db.query(Question).offset(skip).limit(limit).all()
        return records
    except Exception as e:
        logger.error(f"Error fetching questions: {str(e)}")
        # If columns don't exist, try to migrate
        if "no such column" in str(e) or "column" in str(e).lower():
            logger.info("Attempting database migration...")
            try:
                from db import run_migrations
                run_migrations()
                # Try again after migration
                records = db.query(Question).offset(skip).limit(limit).all()
                return records
            except Exception as migrate_err:
                logger.error(f"Migration failed: {str(migrate_err)}")
                raise HTTPException(status_code=500, detail="Database schema error. Please try again.")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/questions/all")
def delete_all_questions(db: Session = Depends(get_db)):
    """Delete all extracted questions from database"""
    try:
        count = db.query(Question).count()
        if count == 0:
            return {"status": "success", "deleted_count": 0}
        
        db.query(Question).delete(synchronize_session=False)
        db.commit()
        logger.info(f"✅ Deleted {count} questions")
        return {"status": "success", "deleted_count": count}
    except Exception as e:
        try:
            db.rollback()
        except:
            pass
        logger.error(f"❌ Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/questions/{question_id}", response_model=QuestionDTO)
def get_question(question_id: int, db: Session = Depends(get_db)):
    record = db.query(Question).filter(Question.id == question_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return record


@app.get("/quiz", response_model=QuizResponse)
def get_quiz(limit: int = 20, topic: Optional[str] = None, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 50))
    query = db.query(Question)

    if topic:
        query = query.filter(Question.question.ilike(f"%{topic}%"))

    results = query.order_by(func.random()).limit(limit).all()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No questions available for quiz")

    return QuizResponse(total=len(results), questions=results)


@app.post("/assistant/validate-raw-text")
def validate_raw_extraction(raw_text: str):
    """AI-FIRST: Validate raw extracted text before parsing into MCQs"""
    try:
        if not raw_text or len(raw_text) < 50:
            return {"status": "error", "message": "Text too short"}
        
        logger.info(f"🤖 AI-validating raw text ({len(raw_text)} chars)")
        
        # Ask Groq to validate and structure the text
        validation_prompt = f"""You are an expert MCQ validator. Analyze this raw extracted text and:

1. Identify if it contains valid MCQ questions
2. Validate the structure (question + options + answer)
3. Fix any formatting issues
4. Return ONLY valid, well-structured MCQs in this JSON format:

[{{"question": "...", "options": ["A", "B", "C", "D"], "correct_option": 0}}]

Raw text:
{raw_text[:2000]}

Return ONLY the JSON array, no other text."""
        
        try:
            response = groq_generate_explanation(validation_prompt)
            logger.info(f"✅ AI validation response received")
            
            # Try to parse JSON from response
            try:
                import json
                # Extract JSON from response
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    questions = json.loads(json_match.group())
                    logger.info(f"✅ Parsed {len(questions)} questions from AI validation")
                    return {
                        "status": "success",
                        "questions": questions,
                        "message": f"AI validated and structured {len(questions)} questions"
                    }
            except:
                pass
            
            return {
                "status": "success",
                "validation": response,
                "message": "AI validation complete"
            }
        except GroqAIUnavailable:
            logger.warning("⚠️ Groq AI unavailable")
            return {"status": "error", "message": "AI unavailable"}
    except Exception as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assistant/validate")
def validate_extraction(
    questions: List[dict],
):
    """Validate extracted questions using Groq AI"""
    try:
        if not questions:
            return {"status": "error", "message": "No questions to validate"}
        
        logger.info(f"Validating {len(questions)} questions with Groq AI")
        
        # Format questions for validation
        validation_prompt = f"""Analyze these extracted MCQ questions and validate them:

{json.dumps(questions[:5], indent=2)}

For each question, check:
1. Is the question clear and complete?
2. Are all options present and distinct?
3. Is there a correct answer marked?
4. Are there any extraction errors?

Respond with JSON: {{"valid": true/false, "issues": [], "confidence": 0-100}}"""
        
        try:
            response = groq_generate_explanation(validation_prompt)
            logger.info(f"Validation response: {response}")
            
            return {
                "status": "success",
                "validation": response,
                "total_questions": len(questions),
                "message": "Extraction validated with AI"
            }
        except GroqAIUnavailable:
            logger.warning("Groq AI unavailable for validation")
            return {
                "status": "success",
                "validation": "AI validation unavailable",
                "total_questions": len(questions),
                "message": "Questions extracted but AI validation failed"
            }
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/assistant/explain")
def explain_question(
    question_id: int,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Get AI explanation for a specific question using Groq API."""
    logger.info(f"Explain request for question {question_id}")
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    if question.explanation:
        return {"explanation": question.explanation, "source": "cached"}

    try:
        explanation = groq_generate_explanation(
            question.question,
            question.options,
            question.correct_option,
        )
        question.explanation = explanation
        db.add(question)
        db.commit()
        return {"explanation": explanation, "source": "generated"}
    except GroqAIUnavailable as exc:
        logger.warning("Groq AI unavailable: %s", exc)
        return {
            "explanation": "AI explanations unavailable. Check GROQ_API_KEY in .env.",
            "source": "unavailable",
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to generate explanation", exc_info=exc)
        return {"explanation": "Could not generate explanation. Please try again.", "source": "error"}


@app.post("/assistant/feedback")
def answer_feedback(
    question_id: int,
    student_answer: int,
    db: Session = Depends(get_db),
):
    """Provide feedback on student's answer choice using Groq API."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    is_correct = student_answer == question.correct_option

    try:
        feedback = groq_generate_feedback(
            question.question,
            question.options,
            student_answer,
            question.correct_option,
        )
        return {"feedback": feedback, "is_correct": is_correct}
    except GroqAIUnavailable as exc:
        logger.warning("Groq AI unavailable: %s", exc)
        return {
            "feedback": "AI feedback unavailable. Check GROQ_API_KEY in .env.",
            "is_correct": None,
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to generate feedback", exc_info=exc)
        return {"feedback": "Could not generate feedback. Please try again.", "is_correct": None}


@app.post("/assistant/hint")
def get_hint(
    question_id: int,
    db: Session = Depends(get_db),
):
    """Get a hint for a question without revealing the answer using Groq API."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    try:
        hint = groq_generate_hint(question.question, question.options)
        return {"hint": hint}
    except GroqAIUnavailable as exc:
        logger.warning("Groq AI unavailable: %s", exc)
        return {"hint": "AI hints unavailable. Check GROQ_API_KEY in .env."}
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to generate hint", exc_info=exc)
        return {"hint": "Could not generate a hint. Please try again."}


def generate_explanations(filename: str) -> None:
    """Background task to populate explanations using Groq API."""
    try:
        db = SessionLocal()
        pending = (
            db.query(Question)
            .filter(Question.source_file == filename, Question.explanation.is_(None))
            .limit(25)
            .all()
        )

        if not pending:
            logger.debug("No pending explanations for %s", filename)
            return

        success_count = 0
        for question in pending:
            try:
                explanation = groq_generate_explanation(
                    question.question,
                    question.options,
                    question.correct_option,
                )
                question.explanation = explanation
                db.add(question)
                success_count += 1
            except GroqAIUnavailable as exc:
                logger.warning("Groq AI unavailable in background task: %s", exc)
                break
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Failed to generate explanation for question %s", question.id, exc_info=exc
                )

        db.commit()
        logger.info("Generated %s/%s explanations for %s", success_count, len(pending), filename)
    except GroqAIUnavailable:
        logger.warning("Groq API unavailable. Check GROQ_API_KEY in .env.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Explanation generation crashed", exc_info=exc)
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
