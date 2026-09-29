from openai import OpenAI

from app.config import OPENAI_API_KEY
from tools.models import WebSearchResult, WebSource


class WebSearchTool:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def search(
        self,
        query: str,
    ) -> WebSearchResult:
        response = self.client.responses.create(
            model="gpt-5.6",
            tools=[
                {"type": "web_search"}
            ],
            input=query,
        )

        sources = []
        seen_urls = set()

        for output in response.output:
            if output.type != "message":
                continue

            for content in output.content:
                if content.type != "output_text":
                    continue

                for annotation in content.annotations:
                    if annotation.type != "url_citation":
                        continue

                    if annotation.url in seen_urls:
                        continue

                    seen_urls.add(annotation.url)

                    sources.append(
                        WebSource(
                            number=len(sources) + 1,
                            title=annotation.title,
                            url=annotation.url,
                        )
                    )

        return WebSearchResult(
            answer=response.output_text,
            sources=sources,
        )