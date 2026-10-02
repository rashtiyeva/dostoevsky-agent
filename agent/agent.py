import json
from collections.abc import AsyncIterator

from agent.models import (
    AgentDecision,
    AgentResponse,
    AgentStreamEvent,
    AgentStreamEventType,
    AgentToolCall,
    ToolName,
)
from agent.prompts import AGENT_INSTRUCTIONS, FINAL_ANSWER_PROMPT
from agent.tool_definitions import AGENT_TOOLS
from agent.tool_executor import ToolExecutor
from app.llm.openai_client import client
from tools.models import CorpusSearchResult, WebSearchResult


class DostoevskyAgent:
    def __init__(self) -> None:
        self.executor = ToolExecutor()

    async def decide_tools(
        self,
        query: str,
    ) -> AgentDecision:
        response = await client.responses.create(
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

    async def run(self, query: str) -> AgentResponse:
        decision = await self.decide_tools(query)

        if not decision.tool_calls:
            return AgentResponse(
                answer=decision.answer
                or "I can only help with questions related to Dostoevsky.",
                corpus_sources=[],
                web_sources=[],
            )

        results = []

        for tool_call in decision.tool_calls:
            result = await self.executor.execute(tool_call)
            results.append((tool_call, result))

        answer = await self._generate_final_answer(
            query=query,
            results=results,
        )

        corpus_sources, web_sources = self._collect_sources(results)

        return AgentResponse(
            answer=answer,
            corpus_sources=corpus_sources,
            web_sources=web_sources,
        )

    async def stream(
        self,
        query: str,
    ) -> AsyncIterator[AgentStreamEvent]:
        try:
            yield AgentStreamEvent(
                type=AgentStreamEventType.STATUS,
                data={"message": "Analyzing your question..."},
            )

            decision = await self.decide_tools(query)

            if not decision.tool_calls:
                answer = decision.answer or (
                    "I can only help with questions related to Dostoevsky."
                )

                yield AgentStreamEvent(
                    type=AgentStreamEventType.TOKEN,
                    data={"text": answer},
                )

                yield AgentStreamEvent(
                    type=AgentStreamEventType.SOURCES,
                    data={
                        "corpus_sources": [],
                        "web_sources": [],
                    },
                )

                yield AgentStreamEvent(
                    type=AgentStreamEventType.DONE,
                    data={},
                )
                return

            results = []

            for tool_call in decision.tool_calls:
                if tool_call.tool == ToolName.CORPUS_SEARCH:
                    message = "Searching Dostoevsky corpus..."
                else:
                    message = "Searching external sources..."

                yield AgentStreamEvent(
                    type=AgentStreamEventType.STATUS,
                    data={"message": message},
                )

                result = await self.executor.execute(tool_call)
                results.append((tool_call, result))

            yield AgentStreamEvent(
                type=AgentStreamEventType.STATUS,
                data={"message": "Generating answer..."},
            )

            async for text_delta in self._stream_final_answer(
                query=query,
                results=results,
            ):
                yield AgentStreamEvent(
                    type=AgentStreamEventType.TOKEN,
                    data={"text": text_delta},
                )

            corpus_sources, web_sources = self._collect_sources(results)

            yield AgentStreamEvent(
                type=AgentStreamEventType.SOURCES,
                data={
                    "corpus_sources": [
                        {
                            "number": source.number,
                            "book_id": source.book_id,
                            "chapter": source.chapter,
                            "section": source.section,
                            "chunk_index": source.chunk_index,
                            "text": source.text,
                        }
                        for source in corpus_sources
                    ],
                    "web_sources": [
                        {
                            "number": source.number,
                            "title": source.title,
                            "url": source.url,
                        }
                        for source in web_sources
                    ],
                },
            )

            yield AgentStreamEvent(
                type=AgentStreamEventType.DONE,
                data={},
            )

        except Exception as exc:
            yield AgentStreamEvent(
                type=AgentStreamEventType.ERROR,
                data={
                    "message": "Failed to process the request.",
                    "detail": str(exc),
                },
            )

    async def _generate_final_answer(
        self,
        query: str,
        results: list[
            tuple[AgentToolCall, CorpusSearchResult | WebSearchResult]
        ],
    ) -> str:
        prompt = self._build_final_prompt(
            query=query,
            results=results,
        )

        response = await client.responses.create(
            model="gpt-5.6",
            input=prompt,
        )

        return response.output_text

    async def _stream_final_answer(
        self,
        query: str,
        results: list[
            tuple[AgentToolCall, CorpusSearchResult | WebSearchResult]
        ],
    ) -> AsyncIterator[str]:
        prompt = self._build_final_prompt(
            query=query,
            results=results,
        )

        stream = await client.responses.create(
            model="gpt-5.6",
            input=prompt,
            stream=True,
        )

        async for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta

    def _build_final_prompt(
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

        return FINAL_ANSWER_PROMPT.format(
            query=query,
            context=context,
        )

    @staticmethod
    def _collect_sources(
        results: list[
            tuple[AgentToolCall, CorpusSearchResult | WebSearchResult]
        ],
    ) -> tuple[list, list]:
        corpus_sources = []
        web_sources = []

        for _, result in results:
            if isinstance(result, CorpusSearchResult):
                corpus_sources.extend(result.sources)

            elif isinstance(result, WebSearchResult):
                web_sources.extend(result.sources)

        return corpus_sources, web_sources