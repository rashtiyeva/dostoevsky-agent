from chunking.chunker import count_tokens


def test_count_tokens_returns_token_count():
    text = "Hello world"

    result = count_tokens(text)

    assert result == 2


def test_count_tokens_empty_text():
    result = count_tokens("")

    assert result == 0



    