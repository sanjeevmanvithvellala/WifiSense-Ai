# Deployment & Operations Guide

## 1. Quick Local Development Setup

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Node.js 18+ and npm
- Git

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-org/wifisense-ai.git
cd wifisense-ai

# Install Python dependencies
pip install -r requirements.txt

# Run database migration & seed default environments/models
python -m backend.app.services.seed

# Start the FastAPI development server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend

# Install npm packages
npm install

# Start Vite hot-reloading dev server
npm run dev
# App will be accessible at http://localhost:5173
```

---

## 2. Docker & Containerized Deployment

To deploy both frontend and backend services in production using Docker Compose:

```bash
# Build and launch all services in background
docker compose up --build -d

# Check service health
docker compose ps

# View real-time logs
docker compose logs -f
```

- **Frontend Application**: `http://localhost:3000`
- **Backend REST API**: `http://localhost:8000/api`
- **WebSocket Streaming**: `ws://localhost:8000/ws/replay`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`

---

## 3. Environment Variables Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| `APP_ENV` | Application environment (`development` / `production`) | `development` |
| `HOST` | Backend host binding IP | `0.0.0.0` |
| `PORT` | Backend listening port | `8000` |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///backend/data/wifisense.db` |
| `ARTIFACTS_DIR` | Directory for serialized ML models and datasets | `backend/artifacts` |
| `CORS_ORIGINS` | Allowed CORS origins JSON list | `["http://localhost:5173","http://localhost:3000"]` |
