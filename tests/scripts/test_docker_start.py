import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.error import URLError

import pytest
from qdrant_client.models import Distance

from scripts import docker_start
from vector_store.qdrant_store import COLLECTION_NAME, VECTOR_SIZE


def indexed_client(ids=("a", "b")):
    client = Mock()
    client.collection_exists.return_value = True
    client.get_collection.return_value = SimpleNamespace(
        config=SimpleNamespace(params=SimpleNamespace(
            vectors=SimpleNamespace(size=VECTOR_SIZE, distance=Distance.COSINE),
        )),
    )
    client.count.return_value.count = len(ids)
    client.retrieve.side_effect = lambda *args, ids, **kwargs: [
        SimpleNamespace(id=value) for value in ids
    ]
    return client


def test_complete_corpus_is_reused():
    client = indexed_client()
    assert docker_start.corpus_is_complete(client, ["a", "b"])
    client.count.assert_called_once_with(COLLECTION_NAME, exact=True)
    client.retrieve.assert_called_once_with(
        COLLECTION_NAME, ids=["a", "b"], with_payload=False, with_vectors=False,
    )


@pytest.mark.parametrize("count", [0, 1, 3])
def test_empty_partial_or_extra_points_require_indexing(count):
    client = indexed_client()
    client.count.return_value.count = count
    assert not docker_start.corpus_is_complete(client, ["a", "b"])


def test_missing_collection_requires_indexing():
    client = indexed_client()
    client.collection_exists.return_value = False
    assert not docker_start.corpus_is_complete(client, ["a", "b"])
    client.count.assert_not_called()


def test_same_count_but_wrong_ids_is_not_accepted():
    client = indexed_client()
    client.retrieve.side_effect = None
    client.retrieve.return_value = [SimpleNamespace(id="unrelated"), SimpleNamespace(id="b")]
    assert not docker_start.corpus_is_complete(client, ["a", "b"])


def test_incompatible_vector_schema_is_not_accepted():
    client = indexed_client()
    client.get_collection.return_value.config.params.vectors.size = 3
    assert not docker_start.corpus_is_complete(client, ["a", "b"])


def test_ids_are_verified_in_bounded_batches():
    ids = [str(index) for index in range(600)]
    client = indexed_client(ids)
    assert docker_start.corpus_is_complete(client, ids)
    assert [len(call.kwargs["ids"]) for call in client.retrieve.call_args_list] == [256, 256, 88]


@pytest.fixture
def corpus():
    with patch.object(docker_start, "load_corpus_chunks", return_value=["a", "b"]),          patch.object(docker_start, "build_point_id", side_effect=lambda chunk: chunk):
        yield


def test_restart_never_invokes_indexer_when_complete(corpus):
    with patch.object(docker_start.subprocess, "run") as run:
        docker_start.ensure_corpus(indexed_client())
    run.assert_not_called()


def test_first_start_reuses_existing_indexing_command(corpus):
    with patch.object(docker_start, "corpus_is_complete", side_effect=[False, True]),          patch.object(docker_start.subprocess, "run") as run:
        docker_start.ensure_corpus(indexed_client())
    run.assert_called_once_with(
        [docker_start.sys.executable, "-m", "scripts.index_corpus"], check=True,
    )


def test_failed_indexing_stops_startup(corpus):
    with patch.object(docker_start, "corpus_is_complete", return_value=False),          patch.object(docker_start.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "index")):
        with pytest.raises(subprocess.CalledProcessError):
            docker_start.ensure_corpus(indexed_client())


def test_successful_exit_with_incomplete_index_stops_startup(corpus):
    with patch.object(docker_start, "corpus_is_complete", return_value=False),          patch.object(docker_start.subprocess, "run"):
        with pytest.raises(RuntimeError, match="complete expected corpus"):
            docker_start.ensure_corpus(indexed_client())


def test_empty_bundled_corpus_fails_before_indexing():
    with patch.object(docker_start, "load_corpus_chunks", return_value=[]),          patch.object(docker_start.subprocess, "run") as run:
        with pytest.raises(RuntimeError, match="no indexable chunks"):
            docker_start.ensure_corpus(indexed_client())
    run.assert_not_called()


def test_readiness_wait_is_bounded():
    with patch.object(docker_start, "urlopen", side_effect=URLError("not ready")) as request,          patch.object(docker_start.time, "sleep") as sleep:
        with pytest.raises(RuntimeError, match="startup timeout"):
            docker_start.wait_for_qdrant("http://qdrant:6333", attempts=3, delay=0)
    assert request.call_count == 3
    assert sleep.call_count == 2


def test_readiness_recovers_and_checks_http_endpoint():
    from unittest.mock import MagicMock

    ready = MagicMock()
    ready.__enter__.return_value.status = 200
    with patch.object(docker_start, "urlopen", side_effect=[URLError("not ready"), ready]) as request,          patch.object(docker_start.time, "sleep"):
        docker_start.wait_for_qdrant("http://qdrant:6333/", attempts=3, delay=0)
    request.assert_called_with("http://qdrant:6333/readyz", timeout=3)
    assert request.call_count == 2


def test_missing_key_fails_before_initializing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with patch.object(docker_start, "wait_for_qdrant") as wait:
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            docker_start.main()
    wait.assert_not_called()


def test_server_is_not_started_after_initialization_failure(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    with patch.object(docker_start, "wait_for_qdrant"),          patch.object(docker_start, "QdrantStore") as store,          patch.object(docker_start, "ensure_corpus", side_effect=RuntimeError("failed")),          patch.object(docker_start.os, "execvp") as execute:
        with pytest.raises(RuntimeError, match="failed"):
            docker_start.main()
    store.return_value.client.close.assert_called_once()
    execute.assert_not_called()
