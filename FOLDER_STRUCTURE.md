# Monorepo Folder Structure

```
robotics-ai-textbook/
│
├── .github/
│   └── workflows/
│       ├── deploy-frontend.yml       # Deploy Docusaurus to GitHub Pages
│       └── deploy-backend.yml        # Deploy FastAPI to cloud (Render/Railway)
│
├── frontend/                          # Docusaurus + Spec-Kit
│   ├── docs/
│   │   ├── en/
│   │   │   ├── 01-introduction.md
│   │   │   ├── 02-ros2-basics.md
│   │   │   ├── 03-gazebo.md
│   │   │   ├── 04-unity-ai.md
│   │   │   ├── 05-nvidia-isaac.md
│   │   │   ├── 06-vla.md
│   │   │   ├── 07-whisper.md
│   │   │   └── 08-humanoid-robotics.md
│   │   ├── ur/                       # Urdu translations
│   │   │   ├── 01-introduction.md
│   │   │   ├── 02-ros2-basics.md
│   │   │   └── ... (other chapters)
│   │   └── images/
│   │       └── (ROS 2, Gazebo, Isaac diagrams)
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatbotWidget.tsx      # RAG chatbot widget
│   │   │   ├── AuthModal.tsx          # Better Auth login
│   │   │   ├── PersonalizationPanel.tsx
│   │   │   ├── LanguageToggle.tsx     # EN/UR switcher
│   │   │   └── SelectedTextChat.tsx   # Highlight → chat
│   │   ├── services/
│   │   │   ├── api.ts                 # API client
│   │   │   ├── auth.ts                # Better Auth wrapper
│   │   │   └── storage.ts             # localStorage utilities
│   │   ├── styles/
│   │   │   ├── global.css
│   │   │   └── chatbot.module.css
│   │   └── App.tsx
│   │
│   ├── static/
│   │   ├── img/
│   │   ├── css/
│   │   └── fonts/                     # Noto Sans Urdu
│   │
│   ├── docusaurus.config.js           # Main config
│   ├── sidebars.js                    # Content navigation
│   ├── .env.example
│   ├── package.json
│   ├── tsconfig.json
│   └── babel.config.js
│
├── backend/                            # FastAPI + RAG
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py                  # Environment config
│   │   ├── models.py                  # Pydantic models
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py            # /api/chat
│   │   │   │   ├── vector_search.py   # /api/vector-search
│   │   │   │   ├── auth.py            # /api/auth/*
│   │   │   │   └── personalization.py # /api/personalization/*
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py            # Token verification
│   │   │       └── cors.py            # CORS middleware
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── rag.py                 # RAG pipeline
│   │   │   ├── vectorization.py       # Embedding logic
│   │   │   ├── llm.py                 # OpenAI Agents/Chat
│   │   │   └── auth.py                # Better Auth helper
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py          # Neon connection pool
│   │   │   ├── models.py              # SQLAlchemy ORM
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── user.py
│   │   │       ├── personalization.py
│   │   │       └── session.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── token_counter.py       # For context window
│   │       └── cache.py               # Redis cache (optional)
│   │
│   ├── scripts/
│   │   ├── vectorize_content.py       # Pre-populate Qdrant
│   │   ├── migrate_db.py              # Run DB migrations
│   │   └── seed_data.py               # Sample questions/answers
│   │
│   ├── tests/
│   │   ├── test_chat.py
│   │   ├── test_rag.py
│   │   └── conftest.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   ├── pyproject.toml                 # UV config
│   ├── Dockerfile                     # Container image
│   └── main.py                        # Entry point (uvicorn)
│
├── shared/                             # Shared utils (optional)
│   ├── types.ts                       # Shared TypeScript types
│   ├── constants.py
│   └── README.md
│
├── scripts/
│   ├── setup.sh / setup.ps1           # OS-specific setup
│   ├── deploy-all.sh                  # Deploy both frontend + backend
│   └── seed-vectors.sh                # Populate Qdrant
│
├── .gitignore
├── README.md                          # Project overview
├── ARCHITECTURE.md                    # (This file)
├── SETUP_ORDER.md                     # Detailed setup steps
├── 7DAY_ROADMAP.md                    # Crash execution plan
├── .env.example                       # Template for env vars
└── TROUBLESHOOTING.md                 # Common issues & fixes
```

## Key Files Explained

| File | Purpose |
|------|---------|
| `frontend/docs/` | Course markdown content (EN + UR) + images |
| `frontend/src/components/ChatbotWidget.tsx` | Embedded RAG chat UI |
| `frontend/docusaurus.config.js` | Base URL, plugins, theme config |
| `backend/app/services/rag.py` | Query → embeddings → search → LLM |
| `backend/app/database/models.py` | SQLAlchemy ORM for Neon Postgres |
| `.github/workflows/deploy-*.yml` | CI/CD automation |
| `scripts/vectorize_content.py` | Pre-compute embeddings for entire textbook |

## Environment Files

### `.env.example` (copy to `.env` in both frontend and backend)

#### Frontend `.env.local`
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_BETTER_AUTH_URL=http://localhost:8000/api/auth
REACT_APP_GITHUB_PAGES_URL=https://yourusername.github.io/robotics-ai-textbook
```

#### Backend `.env`
```
DATABASE_URL=postgresql://user:pass@ep-xxxxx.neon.tech/roboticstextbook
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_URL=https://xxxxx-xxx-xxxxxxx.eu-0.qdrant.io:6333
OPENAI_API_KEY=sk-xxxxx
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

BETTER_AUTH_SECRET=your-secret-key
GITHUB_CLIENT_ID=xxxxx
GITHUB_CLIENT_SECRET=xxxxx
GOOGLE_CLIENT_ID=xxxxx
GOOGLE_CLIENT_SECRET=xxxxx

CORS_ORIGINS=http://localhost:3000,https://yourusername.github.io/robotics-ai-textbook
LOG_LEVEL=INFO

# Optional
REDIS_URL=redis://localhost:6379
SENTRY_DSN=
```

## Notes
- **Monorepo Strategy**: Nx or Turborepo optional; simple npm workspaces sufficient for this project size
- **Shared Code**: Use `shared/types.ts` for API request/response types shared between frontend and backend
- **API Deployment**: Backend can run on Render, Railway, Fly.io, or AWS Lambda (via FastAPI with serverless adapters)
- **Static Content**: GitHub Pages serves frontend from root of gh-pages branch /robotics-ai-textbook
