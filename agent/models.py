from dataclasses import dataclass
from enum import Enum

from tools.models import CorpusSource, WebSource


class ToolName(str, Enum):
    CORPUS_SEARCH = "corpus_search"
    WEB_SEARCH = "web_search"
    
class AgentStreamEventType(str, Enum):
    STATUS = "status"
    TOKEN = "token"
    SOURCES = "sources"
    DONE = "done"
    ERROR = "error"

@dataclass
class AgentToolCall:
    tool: ToolName
    query: str


@dataclass
class AgentDecision:
    tool_calls: list[AgentToolCall]
    answer: str | None = None


@dataclass
class AgentResponse:
    answer: str
    corpus_sources: list[CorpusSource]
    web_sources: list[WebSource]
    
@dataclass
class AgentStreamEvent:
    type: AgentStreamEventType
    data: dict