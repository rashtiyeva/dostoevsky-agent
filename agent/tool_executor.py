from agent.models import AgentToolCall, ToolName
from tools.corpus_search import CorpusSearchTool
from tools.models import CorpusSearchResult, WebSearchResult
from tools.web_search import WebSearchTool


class ToolExecutor:
    def __init__(self) -> None:
        self.corpus_search = CorpusSearchTool()
        self.web_search = WebSearchTool()

    async def execute(
        self,
        tool_call: AgentToolCall,
    ) -> CorpusSearchResult | WebSearchResult:
        match tool_call.tool:
            case ToolName.CORPUS_SEARCH:
                return self.corpus_search.search(tool_call.query)

            case ToolName.WEB_SEARCH:
                return await self.web_search.search(tool_call.query)

            case _:
                raise ValueError(f"Unsupported tool: {tool_call.tool}")