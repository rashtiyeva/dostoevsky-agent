from collections.abc import Iterator

from fastapi.sse import ServerSentEvent

from agent.models import AgentStreamEvent


def to_sse_events(
    events: Iterator[AgentStreamEvent],
) -> Iterator[ServerSentEvent]:
    for event in events:
        yield ServerSentEvent(
            event=event.type.value,
            data=event.data,
        )