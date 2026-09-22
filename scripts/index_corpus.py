from indexing.indexer import CorpusIndexer


def main() -> None:
    indexer = CorpusIndexer()
    indexer.index()


if __name__ == "__main__":
    main()