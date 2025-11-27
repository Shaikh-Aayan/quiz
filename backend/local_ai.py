"""AI utilities with local transformer fallback and Groq API support."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import List, Optional

logger = logging.getLogger(__name__)

# Try to import Groq for fast API-based generation
try:
    from groq_ai import (
        GroqAIUnavailable,
        generate_explanation as groq_generate_explanation,
        generate_feedback as groq_generate_feedback,
        generate_hint as groq_generate_hint,
    )
    _GROQ_AVAILABLE = True
except ImportError:
    _GROQ_AVAILABLE = False

try:  # pragma: no cover - import side effects checked at runtime
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    _TRANSFORMERS_AVAILABLE = True
except ImportError:  # pragma: no cover - handled gracefully
    _TRANSFORMERS_AVAILABLE = False

MODEL_NAME = os.getenv("LOCAL_AI_MODEL", "google/flan-t5-base")
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("LOCAL_AI_MAX_TOKENS", "256"))


class LocalAIUnavailable(RuntimeError):
    """Raised when the local AI model is not available."""


@lru_cache(maxsize=1)
def _load_model():
    if not _TRANSFORMERS_AVAILABLE:
        raise LocalAIUnavailable(
            "Local AI model requires 'transformers', 'torch', and 'sentencepiece'. "
            "Install them with: pip install transformers sentencepiece accelerate torch"
        )

    logger.info("Loading local AI model: %s", MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def _ensure_model_ready():
    try:
        return _load_model()
    except LocalAIUnavailable:
        raise
    except Exception as exc:  # pragma: no cover - defensive programming
        logger.exception("Failed to load local AI model")
        raise LocalAIUnavailable(str(exc)) from exc


def _generate_response(prompt: str, max_new_tokens: Optional[int] = None) -> str:
    tokenizer, model = _ensure_model_ready()
    tokens = tokenizer(prompt, return_tensors="pt")

    kwargs = {
        "max_new_tokens": min(max_new_tokens or DEFAULT_MAX_NEW_TOKENS, 512),
        "num_beams": 4,
        "early_stopping": True,
        "no_repeat_ngram_size": 2,
    }

    with torch.no_grad():
        outputs = model.generate(**tokens, **kwargs)

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text.strip()


def _format_options(options: List[str]) -> str:
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    formatted = []
    for idx, option in enumerate(options):
        label = labels[idx] if idx < len(labels) else f"Option {idx+1}"
        formatted.append(f"{label}) {option}")
    return "\n".join(formatted)


def generate_explanation(question: str, options: List[str], correct_index: Optional[int]) -> str:
    """Generate a short explanation for the correct option (Groq first, then local)."""
    # Try Groq first if available
    if _GROQ_AVAILABLE:
        try:
            return groq_generate_explanation(question, options, correct_index)
        except Exception as exc:
            logger.debug("Groq explanation failed, falling back to local: %s", exc)
    
    # Fall back to local model
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

    return _generate_response(prompt, max_new_tokens=180)


def generate_hint(question: str, options: List[str]) -> str:
    """Generate a hint without revealing the answer (Groq first, then local)."""
    # Try Groq first if available
    if _GROQ_AVAILABLE:
        try:
            return groq_generate_hint(question, options)
        except Exception as exc:
            logger.debug("Groq hint failed, falling back to local: %s", exc)
    
    # Fall back to local model
    prompt = (
        "Provide a helpful hint (2 sentences) for this multiple-choice question without revealing the answer."
        " Focus on key concepts the student should think about.\n"
        f"Question: {question}\n"
        f"Options:\n{_format_options(options)}\n"
    )
    return _generate_response(prompt, max_new_tokens=120)


def generate_feedback(
    question: str,
    options: List[str],
    student_index: int,
    correct_index: Optional[int],
) -> str:
    """Generate targeted feedback comparing student's choice with the correct one (Groq first, then local)."""
    # Try Groq first if available
    if _GROQ_AVAILABLE:
        try:
            return groq_generate_feedback(question, options, student_index, correct_index)
        except Exception as exc:
            logger.debug("Groq feedback failed, falling back to local: %s", exc)
    
    # Fall back to local model
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
        "Provide constructive feedback (2-3 sentences) for a student's MCQ answer."
        " Mention if they are correct or not and why."
        f"\nQuestion: {question}\n"
        f"Options:\n{_format_options(options)}\n"
        f"Student answer: {student_option}\n"
        f"Correct answer: {correct_option}\n"
    )

    return _generate_response(prompt, max_new_tokens=160)
