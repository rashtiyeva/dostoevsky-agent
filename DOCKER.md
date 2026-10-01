# Docker

## Quickstart

Clone the repository:

```bash
git clone https://github.com/rashtiyeva/dostoevsky-agent.git
cd dostoevsky-agent
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key
```

Start the application:

```bash
docker compose up -d --build
```

Open the UI at `http://localhost:8000/`.

The first startup may take longer while the BGE models are downloaded and the Dostoevsky corpus is indexed. You can follow the startup progress with:

```bash
docker compose logs -f app
```

## Persistence

Docker Compose runs two services:

- `app` — FastAPI application and frontend
- `qdrant` — vector database

The Qdrant index and Hugging Face model cache are stored in Docker volumes, so they are preserved across normal restarts.

Stop the application:

```bash
docker compose down
```

Stop the application and remove the persisted index and model cache:

```bash
docker compose down -v
```

After removing the volumes, the models will be downloaded and the corpus indexed again on the next startup.