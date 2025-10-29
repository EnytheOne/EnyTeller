import hashlib
import json
import logging
import os
import time

import google.generativeai as genai
import numpy as np

from config import Config

genai.configure(api_key=Config.GEMMA_API_KEY)
MEMORY_PATH = "memory/memory_store.json"
_QUOTA_BACKOFF_SECONDS = 60
_quota_block_until = 0.0
_FALLBACK_VECTOR_SIZE = 128


def _should_backoff() -> bool:
    return time.time() < _quota_block_until


def _start_backoff(message: str) -> None:
    global _quota_block_until
    _quota_block_until = time.time() + _QUOTA_BACKOFF_SECONDS
    logging.warning(
        "Embedding quota exceeded; backing off for %s seconds: %s",
        _QUOTA_BACKOFF_SECONDS,
        message,
    )


def reset_backoff():
    """Reset quota backoff (primarily for tests)."""
    global _quota_block_until
    _quota_block_until = 0.0


def get_embedding(text):
    """Generate embedding vector for given text with quota-aware backoff."""
    if _should_backoff():
        logging.debug("Skipping embedding request due to active quota backoff.")
        return _local_embedding(text)

    try:
        result = genai.embed_content(model="models/embedding-001", content=text)
    except Exception as exc:  # pragma: no cover - network errors hit except
        if "429" in str(exc):
            _start_backoff(str(exc))
            return _local_embedding(text)
        logging.warning("Embedding API error, using local fallback: %s", exc)
        return _local_embedding(text)

    # Successful call; clear backoff if previously set
    reset_backoff()
    return result["embedding"]


def _local_embedding(text: str):
    """Deterministic embedding fallback using seeded Gaussian values."""
    seed_bytes = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(seed_bytes[:8], "big", signed=False)
    rng = np.random.default_rng(seed)
    vector = rng.normal(size=_FALLBACK_VECTOR_SIZE).astype(float)
    logging.debug("Using local embedding fallback (seed=%s)", seed)
    return vector.tolist()

def cosine_similarity(a, b):
    """Measure semantic similarity between two vectors."""
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return []
    with open(MEMORY_PATH, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)
