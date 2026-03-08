# 7-Day Crash Execution Roadmap

## Assumptions
- Pre-written course content available (or use placeholder chapters)
- Cloud accounts ready (Neon, Qdrant, OpenAI, GitHub)
- Developer experience with React, Python, APIs

## Day 1: Environment Setup & Frontend Scaffolding (8 hours)

### Morning (4 hours)

**Task 1.1: Environment Prep** (1 hour)
- [ ] Clone GitHub repo
- [ ] Create GitHub Pages branch (gh-pages)
- [ ] Enable GitHub Pages in repo settings
- [ ] Create `.env.example` files for both frontend and backend
- [ ] Document all cloud credentials in GitHub Secrets (never in code)

**Task 1.2: Frontend Project Init** (1.5 hours)
```bash
cd frontend
npx create-docusaurus@latest . --typescript
npm install react react-dom axios zustand @radix-ui/react-dialog tailwindcss
```

**Task 1.3: Configure Docusaurus** (1.5 hours)
- [ ] Edit `docusaurus.config.js`:
  - Set baseUrl: `/robotics-ai-textbook/`
  - Add GitHub Pages deployment settings
  - Configure i18n (optional, but prepare structure)
- [ ] Create `sidebars.js` with placeholder chapters
- [ ] Add Google Fonts for Urdu (Noto Sans Urdu)
- [ ] Create `static/fonts/` directory

### Afternoon (4 hours)

**Task 1.4: Content Structure** (1 hour)
```bash
mkdir -p frontend/docs/en frontend/docs/ur frontend/docs/images
# Create 8 chapter markdown files (can be minimal stubs):
# 01-introduction.md
# 02-ros2-basics.md
# ... (8 chapters total)
```

**Task 1.5: React Components Skeleton** (2 hours)
- [ ] Create `frontend/src/components/ChatbotWidget.tsx` (basic structure)
- [ ] Create `frontend/src/components/AuthModal.tsx` (stub)
- [ ] Create `frontend/src/components/LanguageToggle.tsx` (stub)
- [ ] Create `frontend/src/services/api.ts` (client setup)
- [ ] Create `frontend/src/services/auth.ts` (auth wrapper)

**Task 1.6: Test Frontend Build** (1 hour)
```bash
npm run build  # Should complete successfully
npm run start  # Test at http://localhost:3000
```

**End of Day 1:** ✅ Frontend scaffold running, chapters placeholder structure in place

---

## Day 2: Backend API Scaffold & Database Setup (8 hours)

### Morning (4 hours)

**Task 2.1: Backend Project Init** (1 hour)
```bash
cd backend
mkdir -p app/{api/{routes,middleware},database/{repositories,migrations},services,utils}
uv init --python 3.11
uv pip install fastapi uvicorn python-dotenv pydantic sqlalchemy psycopg[binary] alembic qdrant-client openai
```

**Task 2.2: FastAPI Main App** (1.5 hours)
- [ ] Create `backend/app/main.py`:
  - Initialize FastAPI app
  - Add CORS middleware
  - Add health check endpoint
  - Add error handlers
- [ ] Create `backend/app/config.py`:
  - Load .env variables
  - Database URL, API keys, etc.

**Task 2.3: Database Setup with Alembic** (1.5 hours)
```bash
cd backend/app/database
alembic init migrations
```
- [ ] Create `backend/app/database/models.py`:
  - Define SQLAlchemy models: User, Session, PersonalizationData
  - Minimal schema for MVP
- [ ] Create initial migration:
```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head  # Apply to Neon
```

### Afternoon (4 hours)

**Task 2.4: API Routes Skeleton** (2 hours)
- [ ] Create `backend/app/api/routes/health.py` → GET /health
- [ ] Create `backend/app/api/routes/chat.py` → POST /api/chat (returns dummy response)
- [ ] Create `backend/app/api/routes/auth.py` → GET /api/auth/session
- [ ] Create `backend/app/api/routes/personalization.py` → GET/POST /api/personalization/*

**Task 2.5: Middleware** (1 hour)
- [ ] Create `backend/app/api/middleware/auth.py` (token verification stub)
- [ ] Create `backend/app/api/middleware/cors.py` (CORS setup)
- [ ] Mount middleware in main.py

**Task 2.6: Test Backend** (1 hour)
```bash
cd backend
uvicorn app.main:app --reload --port 8000
# Test endpoints:
curl http://localhost:8000/health  # → {"status": "ok"}
curl http://localhost:8000/api/auth/session  # → {"user": null}
```

**End of Day 2:** ✅ Backend API running, all endpoints returning dummy data, database connected to Neon

---

## Day 3: Vectorization & Qdrant Integration (8 hours)

### Morning (4 hours)

**Task 3.1: Content Chunking Script** (1.5 hours)
- [ ] Create `backend/scripts/vectorize_content.py`:
  - Read markdown files from `frontend/docs/en`
  - Chunk by 512 tokens (use `tiktoken`)
  - Include metadata: chapter, section, order
  - Output to JSONL

```bash
pip install tiktoken
python backend/scripts/vectorize_content.py --source frontend/docs/en --output vectors.jsonl
```

**Task 3.2: Embedding & Qdrant Upload** (1.5 hours)
```bash
# Extend vectorize_content.py to:
# 1. Embed chunks with OpenAI embedding API
# 2. Upload to Qdrant collection "robotics_en"

python backend/scripts/vectorize_content.py \
  --input vectors.jsonl \
  --embed-api-key $OPENAI_API_KEY \
  --qdrant-url $QDRANT_URL \
  --qdrant-api-key $QDRANT_API_KEY \
  --upload
```

### Afternoon (4 hours)

**Task 3.3: RAG Service Implementation** (2 hours)
- [ ] Create `backend/app/services/rag.py`:
  ```python
  async def embed_query(query: str) → np.ndarray
  async def search_qdrant(vector, top_k=5) → List[Chunk]
  async def build_context(chunks) → str
  async def call_llm(context, query) → str
  async def apply_text_filter(chunks, chapter_id) → List[Chunk]  # For "selected text only"
  ```

**Task 3.4: Chat Endpoint Implementation** (2 hours)
- [ ] Update `backend/app/api/routes/chat.py`:
  - POST /api/chat
  - Input: {query, selected_text?, chapter?, language}
  - Output: {answer, sources, tokens_used}
  - Call RAG pipeline
  - Log to Postgres

**End of Day 3:** ✅ Vectorization pipeline working, Qdrant populated with ~500-1000 chunks, RAG endpoint returning real answers

---

## Day 4: Frontend Chatbot UI & API Integration (8 hours)

### Morning (4 hours)

**Task 4.1: API Client Implementation** (1.5 hours)
- [ ] Implement `frontend/src/services/api.ts`:
  ```typescript
  export async function sendQuery(query, selectedText?, chapter?): Promise<ChatResponse>
  export async function getChatHistory(userId): Promise<Message[]>
  export function subscribeToStream(query): AsyncIterable<string>  // For streaming
  ```

**Task 4.2: ChatbotWidget Component** (2.5 hours)
- [ ] Implement `frontend/src/components/ChatbotWidget.tsx`:
  - Floating button in bottom-right corner
  - Modal dialog with chat history
  - Input field + submit button
  - Display streaming responses
  - Show sources/citations
  - Error handling

### Afternoon (4 hours)

**Task 4.3: Selected Text Feature** (1.5 hours)
- [ ] Add text selection handler to Docusaurus pages
- [ ] On select: extract text + chapter metadata
- [ ] Pass to ChatbotWidget as initial query context
- [ ] Highlight selected text in chatbot

**Task 4.4: End-to-End Test** (2.5 hours)
- [ ] Local testing:
  - Frontend on http://localhost:3000
  - Backend on http://localhost:8000
  - Ask "What is ROS 2?"
  - Should get contextual answer in < 3 seconds
  - Verify streaming works
  - Verify error scenarios (empty query, API down, etc.)

**End of Day 4:** ✅ Chatbot fully functional on localhost, integrated with Qdrant + OpenAI

---

## Day 5: Authentication & Personalization (8 hours)

### Morning (4 hours)

**Task 5.1: Better Auth Integration** (2 hours)
- [ ] Setup Better Auth database tables (Alembic migration)
- [ ] Create `backend/app/services/auth.py`:
  ```python
  class BetterAuthHandler:
      async def verify_token(token) → UserId
      async def create_session(user_info) → SessionToken
      async def get_user(user_id) → UserData
  ```
- [ ] Mount auth routes in main.py

**Task 5.2: Auth Middleware** (1.5 hours)
- [ ] Update middleware/auth.py:
  - Extract token from Authorization header
  - Validate with Better Auth
  - Attach user context to request
- [ ] Protect /api/personalization/* endpoints with auth

**Task 5.3: Frontend Auth** (0.5 hours)
- [ ] Update `frontend/src/components/AuthModal.tsx`:
  - GitHub + Google SSO buttons
  - Callback handler
  - Store token in localStorage/cookies

### Afternoon (4 hours)

**Task 5.4: Personalization DB Schema** (1 hour)
- [ ] Expand Neon schema:
  ```sql
  CREATE TABLE personalization_data (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES user(id),
    chapter_id TEXT,
    progress_percent INT,
    bookmarks JSONB,
    quiz_scores JSONB,
    language_preference VARCHAR(10),
    created_at TIMESTAMP
  );
  ```

**Task 5.5: Personalization Endpoints** (1.5 hours)
- [ ] Implement in `backend/app/api/routes/personalization.py`:
  - GET /api/personalization/{user_id} → fetch user progress
  - POST /api/personalization/{user_id}/{chapter_id} → update progress
  - GET /api/personalization/{user_id}/recommendations → weak areas

**Task 5.6: Personalization UI** (1.5 hours)
- [ ] Create `frontend/src/components/PersonalizationPanel.tsx`:
  - Display: chapters read, quizzes passed, bookmarks
  - Show recommendations based on low scores
  - Allow bookmark/note creation

**End of Day 5:** ✅ GitHub login working, user progress saved to Neon, personalization panel displaying

---

## Day 6: Multi-language & Deployment Setup (8 hours)

### Morning (4 hours)

**Task 6.1: Urdu Content Preparation** (2 hours)
```bash
# Option A: Speed (manual 3 chapters + auto-translate rest)
# Manually translate: intro, ROS2, humanoid
# Auto-translate: others

# Option B: Batch processing
python backend/scripts/translate_content.py \
  --source frontend/docs/en \
  --output frontend/docs/ur \
  --target-lang ur \
  --model gpt-3.5-turbo  # Faster than 4
```

**Task 6.2: Urdu Vectorization** (1.5 hours)
```bash
python backend/scripts/vectorize_content.py \
  --source frontend/docs/ur \
  --collection-name robotics_ur \
  --language ur \
  --qdrant-url $QDRANT_URL \
  --upload
```

**Task 6.3: Language Toggle Frontend** (0.5 hours)
- [ ] Implement `frontend/src/components/LanguageToggle.tsx`:
  - EN/UR button in header
  - Switch docs route + Qdrant collection
  - Persist preference in localStorage

### Afternoon (4 hours)

**Task 6.4: GitHub Actions Workflows** (2 hours)
- [ ] Create `.github/workflows/deploy-frontend.yml`:
  ```yaml
  on: push to main
  jobs:
    build-and-deploy:
      - checkout
      - setup node
      - cd frontend && npm install && npm run build
      - deploy build/ to gh-pages branch
  ```
- [ ] Create `.github/workflows/deploy-backend.yml`:
  ```yaml
  on: manual trigger / release
  jobs:
    deploy:
      - build docker image
      - push to registry
      - deploy to Render/Railway
  ```

**Task 6.5: Backend Cloud Deployment** (1 hour)
- [ ] Deploy to Render.com or Railway.app:
  - Connect GitHub repo
  - Set environment variables
  - Deploy command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - Get public API URL

**Task 6.6: Update Frontend for Production** (1 hour)
- [ ] Create `frontend/.env.production`:
  ```
  REACT_APP_API_URL=https://robotics-api-xxxx.onrender.com
  REACT_APP_GITHUB_PAGES_URL=https://yourusername.github.io/robotics-ai-textbook
  ```
- [ ] First deployment: `git push main` → GitHub Actions triggers

**End of Day 6:** ✅ Frontend deployed to GitHub Pages, backend deployed to cloud, both environments configured

---

## Day 7: Testing, Optimization & Polish (8 hours)

### Morning (4 hours)

**Task 7.1: End-to-End Production Test** (2 hours)
- [ ] Visit: https://yourusername.github.io/robotics-ai-textbook/
- [ ] Sign in with GitHub → verify auth works
- [ ] Read Chapter 2, select text → chatbot appears
- [ ] Ask question → get answer in < 2 seconds
- [ ] Switch to Urdu → content + chatbot in Urdu
- [ ] Check progress saved in personalization panel
- [ ] Test on mobile (responsive design)

**Task 7.2: Performance Optimization** (1.5 hours)
- [ ] Frontend:
  - [ ] Enable gzip compression (GitHub Pages automatic)
  - [ ] Optimize bundle size: `npm run build --analyze`
  - [ ] Lazy load chatbot component
- [ ] Backend:
  - [ ] Set Qdrant search limit to top-5 (faster)
  - [ ] Add response caching for repeated queries (Redis optional)
  - [ ] Monitor Neon query times

**Task 7.3: Error Handling & Logging** (0.5 hours)
- [ ] Test scenarios:
  - [ ] Send empty query → should error gracefully
  - [ ] Backend down → should show "offline" message
  - [ ] Qdrant down → should return 503 with message
  - [ ] Session expired → redirect to login

### Afternoon (4 hours)

**Task 7.4: Documentation & Handoff** (1 hour)
- [ ] Update README.md:
  - Architecture overview
  - Deployment instructions
  - Environment setup
  - Contributing guidelines
- [ ] Add comments to critical code sections
- [ ] Create TROUBLESHOOTING.md

**Task 7.5: Content Quality Check** (1.5 hours)
- [ ] Review all 8 chapters for:
  - Correct metadata (chapter_id, section_id)
  - Image references working
  - Links not broken
  - Urdu translation quality (or mark for manual review)

**Task 7.6: Final Checks & Demo** (1.5 hours)
- [ ] SEO: Add meta tags to Docusaurus config
- [ ] Analytics: (Optional) Add Google Analytics
- [ ] Security: Verify no API keys in code
- [ ] Rate limiting: Add to backend to prevent abuse
- [ ] Record demo video (optional)

**End of Day 7:** ✅ Production-ready system deployed, tested, and documented

---

## Per-Day Time Allocation Summary

| Day | Focus | Hours | Outcome |
|-----|-------|-------|---------|
| 1 | Frontend scaffold | 8 | Docusaurus running, content structure |
| 2 | Backend scaffold | 8 | FastAPI API, Neon database |
| 3 | Vectorization | 8 | Content embedded, Qdrant populated |
| 4 | Chatbot UI | 8 | Working RAG chat on localhost |
| 5 | Auth + personalization | 8 | Login + progress tracking |
| 6 | Multi-lang + deploy | 8 | Urdu support, cloud deployment |
| 7 | Testing + polish | 8 | Production ready, documented |
| **TOTAL** | **Full system** | **56 hours** | **Live textbook + RAG chatbot** |

---

## Shortcuts & Time Savers

1. **Use placeholder content for first 3 days**
   - Spend Day 1-3 on architecture
   - Populate real content on Days 4-7

2. **Skip full Urdu translation**
   - Use Google Translate for placeholder
   - Manual translation post-launch

3. **Minimal personalization MVP**
   - Just track progress % and bookmarks
   - Recommendations logic optional for launch

4. **Simple UI**
   - Use Tailwind CSS templates (free components)
   - Skip custom design until post-MVP

5. **Pre-populate with sample questions**
   - FAQ database for instant answers
   - Reduce RAG latency for common queries

6. **Render-based backend**
   - 1-click deployment from GitHub
   - No Docker/Kubernetes setup needed

---

## Next: Monitor deployment and iterate on content quality
