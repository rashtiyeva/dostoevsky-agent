CORPUS_SEARCH_TOOL = {
    "type": "function",
    "name": "corpus_search",
    "description": (
        "Search the local corpus of Dostoevsky's works. "
        "Use this for questions about the content, characters, events, "
        "themes, ideas, or passages in Dostoevsky's books."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to use for corpus retrieval.",
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


WEB_SEARCH_TOOL = {
    "type": "function",
    "name": "web_search",
    "description": (
        "Search the web for information outside the local Dostoevsky corpus. "
        "Use this for current information, scholarship, criticism, historical "
        "context, or other external information."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search for on the web.",
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


AGENT_TOOLS = [
    CORPUS_SEARCH_TOOL,
    WEB_SEARCH_TOOL,
]