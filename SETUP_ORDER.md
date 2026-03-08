# Exact Setup Order (What to Install First → Last)

## Phase 1: Environment & Infrastructure (30 min)

### 1.1 Prerequisites
```bash
# Ensure installed:
# - Node.js 18+ (npm 9+)
# - Python 3.11+
# - Git
# - Docker (optional, for backend containerization)
# - UV (Python package manager - faster than pip)

# Install UV:
pip install uv

# Verify:
node --version    # v18.x or higher
python --version  # 3.11+
uv --version
```

### 1.2 GitHub Setup
```bash
# 1. Create GitHub repo: robotics-ai-textbook
# 2. Clone locally:
git clone https://github.com/yourusername/robotics-ai-textbook.git
cd robotics-ai-textbook

# 3. Create main branch structure:
git checkout -b main
git branch -D master (if exists)
```

### 1.3 Cloud Services Setup (CREATE ACCOUNTS)
```
1. Neon Postgres:
   - Create account: https://console.neon.tech
   - Create project: "robotics-textbook"
   - Get connection string: postgresql://[user]:[pass]@[host]/[dbname]
   - Store in secrets

2. Qdrant Cloud:
   - Create account: https://console.qdrant.io
   - Create cluster: "robotics-textbook-prod"
   - Get API key + URL
   - Store in secrets

3. OpenAI API:
   - Create account: https://platform.openai.com
   - Get API key for GPT-4o + embeddings
   - Store in secrets

4. Better Auth:
   - Setup guide: https://www.better-auth.com
   - Register GitHub + Google OAuth apps
   - Get client IDs, secrets

5. GitHub Pages:
   - Enable in repo Settings → Pages
   - Select "Deploy from a branch" → gh-pages branch
```

---

## Phase 2: Frontend Setup (45 min)

### 2.1 Initialize Docusaurus
```bash
cd robotics-ai-textbook

# Create frontend directory
mkdir frontend
cd frontend

# Create Docusaurus project with TypeScript
npx create-docusaurus@latest . --typescript --package-manager pnpm

# Or with npm:
npx create-docusaurus@latest . --typescript
```

### 2.2 Install Additional Dependencies
```bash
cd frontend

# React + UI
npm install react react-dom
npm install -D tailwindcss postcss autoprefixer
npm install @radix-ui/react-dialog @radix-ui/react-tabs

# API client
npm install axios

# Better Auth (client SDK)
npm install @better-auth/core

# Utilities
npm install zustand  # State management for chatbot
npm install marked   # Markdown parser

# Linting & TypeScript
npm install -D typescript eslint prettier
npm install -D @typescript-eslint/eslint-plugin @typescript-eslint/parser

# Dev server
npm install -D @docusaurus/core @docusaurus/preset-classic
```

### 2.3 Configure Docusaurus
```bash
# Edit: frontend/docusaurus.config.js

const config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'Learn ROS 2, Gazebo, Isaac Sim, and Humanoid Control',
  url: 'https://yourusername.github.io',
  baseUrl: '/robotics-ai-textbook/',
  projectName: 'robotics-ai-textbook',
  organizationName: 'yourusername',
  deploymentBranch: 'gh-pages',
  plugins: [
    '@docusaurus/plugin-content-docs',
    '@docusaurus/plugin-content-blog',
  ],
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/yourusername/robotics-ai-textbook/tree/main/frontend/docs',
        },
        blog: {
          showReadingTime: true,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
```

### 2.4 Create Content Structure
```bash
mkdir -p frontend/docs/en frontend/docs/ur frontend/docs/images

# Create sample content files:
# frontend/docs/en/01-introduction.md (will populate in Phase 4)
# frontend/docs/en/02-ros2-basics.md
# etc.

# Create sidebar config:
# frontend/sidebars.js
```

### 2.5 Create React Components for Chatbot
```bash
mkdir -p frontend/src/components frontend/src/services

# Create these files (templates in Phase 4):
# frontend/src/components/ChatbotWidget.tsx
# frontend/src/components/AuthModal.tsx
# frontend/src/components/LanguageToggle.tsx
# frontend/src/services/api.ts
# frontend/src/services/auth.ts
```

### 2.6 Test Frontend Build
```bash
cd frontend
npm run build  # Should complete without errors

# Test locally:
npm run start  # http://localhost:3000
```

---

## Phase 3: Backend Setup (60 min)

### 3.1 Initialize FastAPI Project
```bash
cd robotics-ai-textbook
mkdir backend
cd backend

# Create project structure
mkdir -p app/{api/routes,database/repositories,services,utils}

# Initialize Python project with UV
uv init --python 3.11

# Or if starting from scratch:
uv pip install fastapi uvicorn python-dotenv pydantic
```

### 3.2 Install Backend Dependencies
```bash
cd backend

# Create requirements or use pyproject.toml (UV):
cat > pyproject.toml << 'EOF'
[project]
name = "robotics-textbook-api"
version = "0.1.0"

[tool.uv]
python-version = "3.11"
EOF

# Install all dependencies:
uv pip install \
  fastapi==0.104.1 \
  uvicorn==0.24.0 \
  python-dotenv==1.0.0 \
  pydantic==2.5.0 \
  pydantic-settings==2.1.0 \
  httpx==0.25.2 \
  qdrant-client==2.7.0 \
  openai==1.3.0 \
  sqlalchemy==2.0.23 \
  psycopg[binary]==3.9.18 \
  alembic==1.12.0 \
  better-auth==1.0.0 \
  fastapi-cors==0.1.6 \
  python-jose==3.3.0 \
  passlib==1.7.4 \
  python-multipart==0.0.6

# Dev dependencies:
uv pip install -d \
  pytest==7.4.3 \
  pytest-asyncio==0.21.1 \
  black==23.12.0 \
  mypy==1.7.1
```

### 3.3 Setup Database (Neon Postgres)
```bash
# Create migration system:
cd backend/app/database

# Initialize Alembic:
alembic init migrations

# Create models.py with SQLAlchemy ORM
# Define: User, Session, PersonalizationData, EmbeddingMetadata tables

# Create migration:
# backend/app/database/migrations/versions/001_initial.py

# Run migration:
alembic upgrade head
```

Migrations will be applied to Neon via:
```bash
DATABASE_URL=postgresql://... alembic upgrade head
```

### 3.4 Create FastAPI Main App
```bash
# backend/app/main.py
# Include:
# - CORS middleware
# - Better Auth routes
# - RAG chat routes
# - Health check endpoint
# - Error handlers
```

### 3.5 Initialize Qdrant Collection
```bash
cd backend/scripts

# Create: vectorize_content.py
# This script:
# 1. Reads all markdown files from frontend/docs/en
# 2. Chunks them (512 tokens, 128 overlap)
# 3. Embeds with OpenAI
# 4. Uploads to Qdrant with metadata

# Run (AFTER OpenAI API key setup):
python vectorize_content.py --language en --upload-to-qdrant
```

### 3.6 Test Backend
```bash
cd backend

# Run development server:
uvicorn app.main:app --reload --port 8000

# Test health endpoint:
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# Test auth endpoint:
curl http://localhost:8000/api/auth/session
```

---

## Phase 4: Integration & RAG Setup (90 min)

### 4.1 Vectorization Pipeline
```bash
cd backend/scripts

# Step 1: Extract content from markdown files
python vectorize_content.py \
  --source ../../../frontend/docs/en \
  --chunk-size 512 \
  --overlap 128 \
  --output vectors.jsonl

# Step 2: Embed with OpenAI
python vectorize_content.py \
  --input vectors.jsonl \
  --embed-model text-embedding-3-small \
  --output embedded-vectors.jsonl

# Step 3: Upload to Qdrant
python vectorize_content.py \
  --input embedded-vectors.jsonl \
  --qdrant-url $QDRANT_URL \
  --qdrant-api-key $QDRANT_API_KEY \
  --collection-name robotics_en \
  --upload
```

### 4.2 Create RAG Service
```bash
# backend/app/services/rag.py

# Implements:
# - query_embedding(query: str) → vector
# - search_qdrant(vector, top_k=5) → chunks
# - build_context(chunks) → formatted string
# - call_llm(context, query) → response
# - apply_selected_text_filter(chunks, chapter_id, section_id) → filtered
```

### 4.3 Create Chat Endpoint
```bash
# backend/app/api/routes/chat.py

# POST /api/chat
# Input:
# {
#   "query": "How does ROS 2 work?",
#   "selected_text": "optional highlighted content",
#   "chapter": "02-ros2-basics",
#   "language": "en"
# }
# Output:
# {
#   "answer": "ROS 2 is a distributed middleware...",
#   "sources": [{"chapter": "02", "section": "1.2"}],
#   "tokens_used": 245
# }
```

### 4.4 Connect Frontend to Backend
```bash
cd frontend/src/services

# Edit: api.ts
# Implement:
# - sendQuery(query, selectedText?, chapter?, language?) → Promise<Response>
# - fetchChatHistory(userId) → Promise<Message[]>
# - submitQuiz(chapterId, answers) → Promise<Score>

# Edit: ChatbotWidget.tsx
# - Handle streaming responses
# - Display typing indicator
# - Show sources
# - Error handling
```

### 4.5 Test RAG End-to-End
```bash
# Backend running on :8000
# Frontend running on :3000

# In browser:
# 1. Open http://localhost:3000
# 2. Click "Chatbot" widget
# 3. Type: "What is ROS 2?"
# 4. Should get context-aware answer from textbook

# Check backend logs:
# - Embedding generation time
# - Qdrant query time
# - LLM response time
# - Total latency (should be < 3 sec)
```

---

## Phase 5: Authentication & Personalization (60 min)

### 5.1 Setup Better Auth
```bash
# backend/app/services/auth.py

# Initialize Better Auth:
from better_auth import BetterAuth

auth = BetterAuth(
    database_url=DATABASE_URL,
    github_client_id=GITHUB_CLIENT_ID,
    github_client_secret=GITHUB_CLIENT_SECRET,
    google_client_id=GOOGLE_CLIENT_ID,
    google_client_secret=GOOGLE_CLIENT_SECRET,
)

# Mount routes:
# app.include_router(auth.router, prefix="/api/auth")
```

### 5.2 Create Auth Middleware
```bash
# backend/app/api/middleware/auth.py

# Middleware that:
# 1. Extracts token from Authorization header or cookies
# 2. Validates with Better Auth
# 3. Attaches user_id to request state
# 4. Logs interaction for personalization
```

### 5.3 Implement Personalization DB
```bash
# backend/app/database/models.py

# Add SQLAlchemy model:
class PersonalizationData(Base):
    __tablename__ = "personalization_data"
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("user.id"))
    chapter_id = Column(String)
    progress_percent = Column(Integer, default=0)
    bookmarks = Column(JSON)
    quiz_scores = Column(JSON)
    language_preference = Column(String, default="en")

# Run migration:
alembic revision --autogenerate -m "add personalization"
alembic upgrade head
```

### 5.4 Create Personalization Endpoints
```bash
# backend/app/api/routes/personalization.py

# GET /api/personalization/{user_id}
# POST /api/personalization/{user_id}/{chapter_id} (update progress)
# GET /api/personalization/{user_id}/recommendations (weak areas)
```

### 5.5 Frontend Auth Integration
```bash
# frontend/src/services/auth.ts

# Implement:
# - loginWithGitHub() → opens modal
# - loginWithGoogle() → opens modal
# - logout() → clears session
# - getCurrentUser() → fetches from localStorage + validates with backend
# - refreshToken() → extends session

# frontend/src/components/AuthModal.tsx
# - Display SSO button options
# - Handle callback from Better Auth
```

---

## Phase 6: Multi-language & Deployment (60 min)

### 6.1 Setup Urdu Content
```bash
cd frontend/docs

# Option A: Manual Translation (FAST)
# - Translate 3 key chapters to Urdu manually
# - Use Google Translate for others as placeholder
# - Store in ur/ directory

# Option B: Batch Translation (AUTOMATED)
# Create: backend/scripts/translate_content.py
python translate_content.py \
  --source-dir frontend/docs/en \
  --output-dir frontend/docs/ur \
  --target-language ur \
  --batch-mode
```

### 6.2 Vectorize Urdu Content
```bash
cd backend/scripts

# Create separate Qdrant collection:
python vectorize_content.py \
  --source frontend/docs/ur \
  --collection-name robotics_ur \
  --language ur \
  --upload-to-qdrant
```

### 6.3 Create GitHub Actions Deployment
```bash
mkdir -p .github/workflows

# Create: .github/workflows/deploy-frontend.yml
# Triggers on: push to main branch
# Steps:
# 1. Checkout code
# 2. Setup Node.js
# 3. Run: npm install (frontend)
# 4. Run: npm run build
# 5. Deploy to gh-pages branch

# Create: .github/workflows/deploy-backend.yml
# Triggers on: new release or manual
# Steps:
# 1. Build Docker image
# 2. Push to Docker Hub or GHCR
# 3. Deploy to Render/Railway (via webhook or manual)
```

### 6.4 Configure GitHub Pages
```bash
# In repo settings:
# - Enable GitHub Pages
# - Source: Deploy from branch
# - Branch: gh-pages
# - Folder: root
# 
# After first deploy:
# - Site accessible at: https://yourusername.github.io/robotics-ai-textbook/
```

### 6.5 Deploy Backend to Cloud
```bash
# Option 1: Render.com
# 1. Create new Web Service
# 2. Connect GitHub repo
# 3. Environment variables (from GitHub Secrets)
# 4. Deploy command: uvicorn app.main:app --host 0.0.0.0
# 5. Render provides URL: https://robotics-api-xxxx.onrender.com

# Option 2: Railway.app
# Similar steps with railway CLI or dashboard

# Test production API:
curl https://robotics-api-xxxx.onrender.com/health
```

### 6.6 Update Frontend API URL
```bash
# frontend/.env.production
REACT_APP_API_URL=https://robotics-api-xxxx.onrender.com
REACT_APP_GITHUB_PAGES_URL=https://yourusername.github.io/robotics-ai-textbook

# npm run build uses .env.production for production builds
```

---

## Phase 7: Testing & Optimization (45 min)

### 7.1 End-to-End Tests
```bash
# Test flow:
# 1. Visit https://yourusername.github.io/robotics-ai-textbook/
# 2. Click "Sign In" → authenticate with GitHub/Google
# 3. Open "Chapter 2: ROS 2 Basics"
# 4. Select text → chatbot opens with pre-filled query
# 5. Ask question → get RAG answer
# 6. Switch to Urdu → content + chatbot in Urdu
# 7. Verify chapter progress saved to personalization_data

# All should complete in < 2 seconds per interaction
```

### 7.2 Performance Optimization
```bash
# Frontend:
# - npm run build --analyze (check bundle size)
# - Enable Gzip in GitHub Pages
# - Cache bust CSS/JS with hash

# Backend:
# - Add caching for frequently asked questions
# - Limit Qdrant search to top-5 results
# - Use connection pooling on Neon

# Database:
# - Add indexes on: user_id, chapter_id, created_at
# - Monitor query times with Neon console
```

### 7.3 Error Handling
```bash
# Test scenarios:
# 1. Send invalid query → should return 400
# 2. Exceed rate limit → should return 429
# 3. Qdrant down → should return 503 with message
# 4. OpenAI API down → should return 503 with message
# 5. Session expired → should redirect to login
```

---

## Summary: Total Time

| Phase | Time | Steps |
|-------|------|-------|
| 1. Environment & Infrastructure | 30 min | Cloud accounts, GitHub setup |
| 2. Frontend (Docusaurus) | 45 min | Create, configure, components |
| 3. Backend (FastAPI) | 60 min | API, database, services |
| 4. RAG Integration | 90 min | Vectorization, endpoints, testing |
| 5. Auth & Personalization | 60 min | Better Auth, DB tables, logic |
| 6. Multi-lang & Deploy | 60 min | Urdu, GitHub Actions, cloud deploy |
| 7. Testing & Optimization | 45 min | E2E tests, performance tuning |
| **TOTAL** | **~6-7 hours** | **Full working system** |
| + Content Writing | **40+ hours** | Creating 8 chapters + Urdu translation |

---

## Next: See 7DAY_ROADMAP.md for day-by-day breakdown
