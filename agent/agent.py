import json

from agent.models import AgentDecision, AgentResponse, AgentToolCall, ToolName
from agent.prompts import AGENT_INSTRUCTIONS, FINAL_ANSWER_PROMPT
from agent.tool_definitions import AGENT_TOOLS
from agent.tool_executor import ToolExecutor
from app.llm.openai_client import client
from tools.models import CorpusSearchResult, WebSearchResult


class DostoevskyAgent:
    def __init__(self) -> None:
        self.executor = ToolExecutor()

    def decide_tools(
        self,
        query: str,
    ) -> AgentDecision:
        response = client.responses.create(
            model="gpt-5.6",
            instructions=AGENT_INSTRUCTIONS,
            input=query,
            tools=AGENT_TOOLS,
            tool_choice="auto",
        )

        tool_calls = []

        for output in response.output:
            if output.type != "function_call":
                continue

            arguments = json.loads(output.arguments)

            tool_calls.append(
                AgentToolCall(
                    tool=ToolName(output.name),
                    query=arguments["query"],
                )
            )

        return AgentDecision(
            tool_calls=tool_calls,
            answer=response.output_text if not tool_calls else None,
        )

    def run(self, query: str) -> AgentResponse:
        decision = self.decide_tools(query)

        if not decision.tool_calls:
            return AgentResponse(
                answer=decision.answer
                or "I can only help with questions related to Dostoevsky.",
                corpus_sources=[],
                web_sources=[],
            )

        results = []

        for tool_call in decision.tool_calls:
            result = self.executor.execute(tool_call)
            results.append((tool_call, result))

        answer = self._generate_final_answer(
            query=query,
            results=results,
        )

        corpus_sources = []
        web_sources = []

        for _, result in results:
            if isinstance(result, CorpusSearchResult):
                corpus_sources.extend(result.sources)

            elif isinstance(result, WebSearchResult):
                web_sources.extend(result.sources)

        return AgentResponse(
            answer=answer,
            corpus_sources=corpus_sources,
            web_sources=web_sources,
        )

    def _generate_final_answer(
        self,
        query: str,
        results: list[
            tuple[AgentToolCall, CorpusSearchResult | WebSearchResult]
        ],
    ) -> str:
        context_parts = []

        for tool_call, result in results:
            if isinstance(result, CorpusSearchResult):
                sources = "\n\n".join(
                    (
                        f"[{source.number}] "
                        f"Book: {source.book_id}\n"
                        f"Chapter: {source.chapter or '-'}\n"
                        f"Section: {source.section or '-'}\n"
                        f"Text: {source.text}"
                    )
                    for source in result.sources
                )

                context_parts.append(
                    f"CORPUS SEARCH\n"
                    f"Query: {tool_call.query}\n\n"
                    f"{sources}"
                )

            elif isinstance(result, WebSearchResult):
                sources = "\n".join(
                    f"[{source.number}] {source.title}: {source.url}"
                    for source in result.sources
                )

                context_parts.append(
                    f"WEB SEARCH\n"
                    f"Query: {tool_call.query}\n\n"
                    f"Answer:\n{result.answer}\n\n"
                    f"Sources:\n{sources}"
                )

        context = "\n\n---\n\n".join(context_parts)

        prompt = FINAL_ANSWER_PROMPT.format(
            query=query,
            context=context,
        )

        response = client.responses.create(
            model="gpt-5.6",
            input=prompt,
        )

        return response.output_text