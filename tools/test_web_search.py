from tools.web_search import WebSearchTool


def main() -> None:
    tool = WebSearchTool()

    result = tool.search(
        "What are the latest major news developments about OpenAI today?"
    )

    print("\nANSWER:")
    print(result.answer)

    print("\nSOURCES:")
    for source in result.sources:
        print(f"[{source.number}] {source.title}")
        print(source.url)


if __name__ == "__main__":
    main()