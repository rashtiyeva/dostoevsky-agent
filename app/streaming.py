from collections.abc import AsyncIterator

from fastapi.sse import ServerSentEvent

from agent.models import AgentStreamEvent


async def to_sse_events(
    events: AsyncIterator[AgentStreamEvent],
) -> AsyncIterator[ServerSentEvent]:
    async for event in events:
        yield ServerSentEvent(
            event=event.type.value,
            data=event.data,
        )