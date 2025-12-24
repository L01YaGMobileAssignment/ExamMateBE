# Backend for Mobile Development course
This is the backend for the Mobile Development course.

# Get API Key and setup environment variables
1. Go to [Google aistudio](https://aistudio.google.com/api-keys) to get your API key.
2. Create a file named `.env` in the root directory of the project and follow example in `.env.example`.

# Prerequisites
1. Install uv package manager [uv](https://docs.astral.sh/uv/)
2. Run 
```bash
uv sync
```

# Initialize database
```bash
python -m app.db.init_db
```

# Run
```bash
.venv\Scripts\activate

uvicorn main:app --host 0.0.0.0 --port 8000
```

Go to http://127.0.0.1:8000/docs for testing.
