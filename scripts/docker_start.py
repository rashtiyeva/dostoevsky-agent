"""Wait for Qdrant, initialize a missing/incomplete corpus, then exec the server."""

import logging
import os
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

from qdrant_client.models import Distance

from retrieval.corpus_loader import load_corpus_chunks
from vector_store.point_mapper import build_point_id
from vector_store.qdrant_store import COLLECTION_NAME, VECTOR_SIZE, QdrantStore

logger = logging.getLogger(__name__)


def wait_for_qdrant(url: str, attempts: int = 30, delay: float = 2) -> None:
    """Bound the wait; do not mistake a listening socket for database readiness."""
    for attempt in range(attempts):
        try:
            with urlopen(url.rstrip("/") + "/readyz", timeout=3) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError):
            pass
        if attempt + 1 < attempts:
            time.sleep(delay)
    raise RuntimeError("Qdrant did not become ready within the startup timeout")


def corpus_is_complete(client, expected_ids: list[str]) -> bool:
    if not client.collection_exists(COLLECTION_NAME):
        return False
    vectors = client.get_collection(COLLECTION_NAME).config.params.vectors
    if (isinstance(vectors, dict) or vectors is None
            or vectors.size != VECTOR_SIZE or vectors.distance != Distance.COSINE):
        return False
    if client.count(COLLECTION_NAME, exact=True).count != len(expected_ids):
        return False
    # Count alone could accept an unrelated or partially replaced corpus.
    # Reuse existing deterministic IDs; do not embed anything during this check.
    for start in range(0, len(expected_ids), 256):
        batch = expected_ids[start:start + 256]
        points = client.retrieve(
            COLLECTION_NAME, ids=batch, with_payload=False, with_vectors=False,
        )
        if {str(point.id) for point in points} != set(batch):
            return False
    return True


def ensure_corpus(client) -> None:
    # Reuse the same corpus loader used by hybrid/BM25 retrieval.
    expected_ids = sorted({build_point_id(chunk) for chunk in load_corpus_chunks()})
    if not expected_ids:
        raise RuntimeError("The bundled corpus contains no indexable chunks")
    if corpus_is_complete(client, expected_ids):
        logger.info("Existing corpus verified (%s chunks); skipping indexing.", len(expected_ids))
        return
    logger.info("Corpus missing or incomplete; running python -m scripts.index_corpus.")
    # A child process releases embedding-model memory before Uvicorn loads models.
    subprocess.run([sys.executable, "-m", "scripts.index_corpus"], check=True)
    if not corpus_is_complete(client, expected_ids):
        raise RuntimeError("Indexing finished without producing the complete expected corpus")
    logger.info("Corpus initialization complete (%s chunks).", len(expected_ids))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY must be set")
    url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    logger.info("Waiting for Qdrant readiness.")
    wait_for_qdrant(url)
    client = QdrantStore(url=url).client
    try:
        ensure_corpus(client)
    finally:
        client.close()
    command = sys.argv[1:] or [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0", "--port", "8000",
    ]
    logger.info("Starting FastAPI.")
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
