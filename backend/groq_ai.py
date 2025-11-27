"""Groq AI integration for fast, free explanations."""

import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    _GROQ_AVAILABLE = True
except ImportError:
    _GROQ_AVAILABLE = False


class GroqAIUnavailable(RuntimeError):
    """Raised when Groq API is not available."""


def _get_groq_client() -> Optional[Groq]:
    """Get Groq client if API key is configured."""
    if not _GROQ_AVAILABLE:
        raise GroqAIUnavailable("Groq SDK not installed. Run: pip install groq")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise GroqAIUnavailable("GROQ_API_KEY not set in .env")
    
    return Groq(api_key=api_key)


def _format_options(options: List[str]) -> str:
    """Format options with labels."""
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    formatted = []
    for idx, option in enumerate(options):
        label = labels[idx] if idx < len(labels) else f"Option {idx+1}"
        formatted.append(f"{label}) {option}")
    return "\n".join(formatted)


def generate_explanation(question: str, options: List[str], correct_index: Optional[int]) -> str:
    """Generate explanation using Groq API."""
    try:
        client = _get_groq_client()
        correct_option = (
            options[correct_index]
            if correct_index is not None and 0 <= correct_index < len(options)
            else "Unknown"
        )

        prompt = (
            "You are an expert tutor. Explain why the correct MCQ option is right in 2-3 sentences.\n"
            f"Question: {question}\n"
            f"Options:\n{_format_options(options)}\n"
            f"Correct option: {correct_option}\n"
            "Explain clearly and concisely."
        )

        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=200,
            temperature=0.7,
        )

        return message.choices[0].message.content.strip()
    except Exception as exc:
        logger.error(f"Groq explanation failed: {exc}")
        raise


def generate_hint(question: str, options: List[str]) -> str:
    """Generate hint using Groq API."""
    try:
        client = _get_groq_client()
        prompt = (
            "Provide a helpful hint (2 sentences) for this multiple-choice question without revealing the answer. "
            "Focus on key concepts the student should think about.\n"
            f"Question: {question}\n"
            f"Options:\n{_format_options(options)}\n"
        )

        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=120,
            temperature=0.7,
        )

        return message.choices[0].message.content.strip()
    except Exception as exc:
        logger.error(f"Groq hint failed: {exc}")
        raise


def generate_feedback(
    question: str,
    options: List[str],
    student_index: int,
    correct_index: Optional[int],
) -> str:
    """Generate feedback using Groq API."""
    try:
        client = _get_groq_client()
        student_option = (
            options[student_index]
            if 0 <= student_index < len(options)
            else "Unknown"
        )
        correct_option = (
            options[correct_index]
            if correct_index is not None and 0 <= correct_index < len(options)
            else "Unknown"
        )

        prompt = (
            "Provide constructive feedback (2-3 sentences) for a student's MCQ answer. "
            "Mention if they are correct or not and why.\n"
            f"Question: {question}\n"
            f"Options:\n{_format_options(options)}\n"
            f"Student answer: {student_option}\n"
            f"Correct answer: {correct_option}\n"
        )

        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=160,
            temperature=0.7,
        )

        return message.choices[0].message.content.strip()
    except Exception as exc:
        logger.error(f"Groq feedback failed: {exc}")
        raise
