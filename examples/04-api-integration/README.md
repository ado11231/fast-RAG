# API Integration

Shows how to embed fastrag into an existing FastAPI application.

## Run

```bash
pip install fastrag "fastapi[standard]"
python api_app.py
# Open http://localhost:8000/docs
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /ask | Query ingested documents |
| GET | /health | Server status |
