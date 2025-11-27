# ACCA MCQ Backend

A FastAPI-based backend for managing ACCA multiple-choice questions, with PDF processing and OCR capabilities.

## Features

- PDF upload and question extraction
- OCR support for scanned documents
- SQLite database storage
- RESTful API endpoints
- CORS support
- Environment-based configuration
- Logging
- Input validation

## Prerequisites

- Python 3.9+
- Tesseract OCR (for PDF text extraction)
- Poppler (for PDF to image conversion)

### Installation on Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

### Installation on macOS

```bash
brew install tesseract poppler
```

### Installation on Windows

1. Install Tesseract OCR from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Add Tesseract to your system PATH
3. Install Poppler from [here](https://github.com/oschwartz10612/poppler-windows/releases/) and add to PATH

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and update the values:
   ```bash
   cp .env.example .env
   ```
5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

## Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./questions.db` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:3000` |
| `HF_API_KEY` | Hugging Face API key (optional) | - |
| `HF_MODEL_ENDPOINT` | Hugging Face model endpoint | `https://api-inference.huggingface.co/models/google/flan-t5-small` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `WORKERS` | Number of worker processes | `4` |

## API Endpoints

### Upload PDF

```http
POST /upload/
Content-Type: multipart/form-data

file: <pdf_file>
```

### List Questions

```http
GET /questions/
```

### Get Question by ID

```http
GET /questions/{question_id}
```

### Health Check

```http
GET /health
```

## Development

### Code Formatting

```bash
black .
isort .
flake8
mypy .
```

### Running Tests

```bash
pytest
```

### Database Migrations

1. Create a new migration:
   ```bash
   alembic revision --autogenerate -m "description of changes"
   ```
2. Apply migrations:
   ```bash
   alembic upgrade head
   ```

## License

MIT
