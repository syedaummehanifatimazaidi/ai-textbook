# Physical AI & Humanoid Robotics Textbook - Architecture

## System Overview (Text Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER BROWSER                                │
├─────────────────────────────────────────────────────────────────┤
│  Docusaurus Frontend (React)                                    │
│  ├─ Content Pages (Markdown + MDX)                              │
│  ├─ RAG Chatbot Widget (Embedded)                               │
│  ├─ Auth UI (Better Auth)                                       │
│  ├─ Urdu Toggle / Language Switch                               │
│  └─ Chapter Personalization UI                                  │
└────────┬────────────────────────────────────────────────────────┘
         │ HTTPS
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   GITHUB PAGES (Static)                         │
│  - Deployed via GH Actions from /frontend/build                 │
└─────────────────────────────────────────────────────────────────┘

     [Chatbot calls] ↓ API Requests

┌─────────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (UV-hosted/Render)                 │
├─────────────────────────────────────────────────────────────────┤
│  RAG Pipeline:                                                  │
│  ├─ /api/chat (POST) - Process user query                       │
│  ├─ /api/vector-search (POST) - Semantic search                 │
│  ├─ /api/auth/* (GET/POST) - Better Auth handlers               │
│  ├─ /api/personalization/* - User preferences                   │
│  └─ /api/health (GET)                                           │
│                                                                 │
│  Internals:                                                     │
│  ├─ Query Embedding (OpenAI embeddings API)                     │
│  ├─ Vector Search (Qdrant)                                      │
│  ├─ Context Window Management                                   │
│  ├─ RAG Retrieval (selected text filter)                        │
│  └─ LLM Call (OpenAI Agents / GPT-4)                            │
└────────┬──────────────────┬──────────────────┬──────────────────┘
         │                  │                  │
         ↓                  ↓                  ↓
┌────────────────────┐ ┌─────────────────┐ ┌──────────────────┐
│  QDRANT CLOUD      │ │  NEON POSTGRES  │ │  OPENAI API      │
│                    │ │                 │ │                  │
│  Vector DB:        │ │  Stores:        │ │  Models:         │
│  ├─ Embeddings     │ │  ├─ Users       │ │  ├─ Embeddings   │
│  ├─ Metadata       │ │  ├─ Sessions    │ │  ├─ Chat GPT-4o  │
│  ├─ Chunks         │ │  ├─ Accounts    │ │  └─ Whisper      │
│  └─ Chapter maps   │ │  └─ Personalize │ │                  │
└────────────────────┘ └─────────────────┘ └──────────────────┘
```

## Component Breakdown

### Frontend (Docusaurus)
- **Tech**: React 18 + TypeScript
- **Build**: Static site to /build, deployed to GitHub Pages
- **Key Features**:
  - Content in /docs (Markdown + MDX)
  - Chatbot embedded as Floating Widget
  - Auth state from localStorage/SessionStorage
  - Urdu toggle switches content language
  - Chapter personalization (bookmark history, progress)

### Backend (FastAPI)
- **Endpoint Base**: `https://api.yourdomain.com` or cloud-hosted
- **Auth Flow**: Better Auth SDK validates tokens, creates sessions in Postgres
- **RAG Flow**:
  1. User sends query + optional selected text
  2. Backend filters documents by selected text (if provided)
  3. Embed query with OpenAI embedding API
  4. Search Qdrant for top-k similar chunks
  5. Build context from retrieved chunks + metadata
  6. Call OpenAI Agents/ChatGPT with context
  7. Stream/return response

### Database (Neon Postgres)
- Connection pooling for FastAPI workers
- Schema: users, sessions, personalization_data, embedding_metadata
- Backup: Neon handles automated backups

### Vector DB (Qdrant Cloud)
- Pre-populated with textbook chapter chunks
- Chunk size: 512 tokens + metadata (chapter, section, language)
- Distance: Cosine similarity
- Filtering: Support language/chapter filters

### Storage (GitHub)
- Frontend code & deployment via GitHub Actions
- Content markdown files versioned here

## Data Flow

### Vectorization Flow (Pre-deployment)
1. Extract all course content into chunks (512 tokens, 128 overlap)
2. For each chunk: embed with OpenAI API
3. Store in Qdrant with metadata: {chapter, section, language, timestamp}
4. Also store English → Urdu pairs with separate embeddings

### Query → Answer Flow
1. User types query or selects text
2. Frontend sends POST to `/api/chat`
3. Backend logs to Postgres (personalization)
4. Query embedded with OpenAI embedding API
5. Qdrant searched with cosine similarity (top 5-10 chunks)
6. If selected text provided, filter chunks by section/chapter
7. Build context: "\n\n".join(retrieved_chunks)
8. Call OpenAI Agents SDK or ChatGPT-4 with system prompt
9. Stream response back to frontend
10. Frontend displays in chatbot widget
11. Log interaction (for personalization)

### "Answer from Selected Text Only"
1. User highlights text in content → chatbot opens with selection
2. Frontend extracts: text content + chapter metadata + offset
3. POST to `/api/chat` with payload:
   ```json
   {
     "query": "user question",
     "selected_text": "highlighted content",
     "chapter": "chapter_id",
     "section": "section_id"
   }
   ```
4. Backend filters Qdrant search to ONLY return chunks within same chapter/section
5. Only retrieved chunks = highlighted text content (approximately)
6. Context window builder ensures response uses only selected context

## Authentication (Better Auth)

### Flow
1. User clicks "Sign In" → Modal opens
2. Better Auth SSO options: GitHub, Google, Email/Password
3. Token created, stored in httpOnly cookie (Postgres session)
4. Frontend stores user ID in localStorage for personalization
5. Each API request includes Authorization header with token
6. Backend verifies with Better Auth middleware

### Database Tables (Neon)
- `accounts`: OAuth provider data
- `users`: Profile + metadata
- `sessions`: Active sessions + expiry
- `verification_tokens`: Email verification

## Personalization Architecture

### Data Storage (Neon Postgres)
```sql
CREATE TABLE personalization_data (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  chapter_id TEXT,
  progress_percent INT,
  bookmarks TEXT[],
  quiz_scores JSON,
  notes TEXT,
  language_preference VARCHAR(10),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Logic
1. After user answers quiz or reads chapter, log to personalization_data
2. On page load, check Postgres for user's progress + preferences
3. Personalization widget shows: chapters read, quizzes passed, saved notes
4. Recommendations based on quiz performance (weak areas)

## Urdu Translation Implementation

### Approach
1. **Content Layer**: Store English + Urdu separately in /docs
   ```
   /docs/en/chapter-1.md
   /docs/ur/chapter-1.md
   ```
2. **Embeddings**: Create separate Qdrant collections:
   - `robotics_en` - English chunks
   - `robotics_ur` - Urdu chunks
3. **Toggle**: Language selector switches docs route + Qdrant collection
4. **Backend**: `/api/chat?language=ur` triggers Urdu embedding + search
5. **Translation**: Use OpenAI GPT-4 to translate on first load (batch job)

### Shortcut: Skip full translation initially
- English content + manual Urdu translation for 3-4 chapters
- Auto-translate remaining chapters via OpenAI batch API (night job)
- Store translations in Postgres, serve from cache

## Deployment Architecture

### GitHub Actions Workflow
1. **Trigger**: Push to main branch
2. **Frontend Job**:
   - Check out code
   - `cd frontend && npm install && npm run build`
   - Deploy /build to GitHub Pages
3. **Backend Job** (if using cloud platform):
   - Build Docker image
   - Push to Docker registry (Docker Hub / GitHub Container Registry)
   - Deploy to Render / Fly.io / Railway
4. **Secrets**: Store API keys in GitHub Secrets

### Environments
- **Dev**: localhost:3000 (frontend) + localhost:8000 (backend)
- **Staging**: GitHub branch + staging backend URL
- **Production**: GitHub main → Pages + production API URL

## Common Failure Points & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Chatbot returns irrelevant answers | Embedding model mismatch (mixing models) | Always use OpenAI text-embedding-3-small consistently |
| Slow Qdrant queries | Too many chunks/high latency | Limit search results to top-5, use async queries |
| Out of LLM context window | Retrieved too many chunks (>3000 tokens) | Dynamic token counting, compress/truncate context |
| Auth token expires mid-chat | Session TTL too short | Set to 7 days, implement refresh token rotation |
| Urdu text renders as boxes | Font missing in Docusaurus | Add Google Fonts: Noto Sans Urdu in _docusaurus.js |
| Vector quantization errors | Qdrant payload mismatch | Ensure metadata schema matches insertion schema |
| GitHub Pages deployment fails | Build output not in /build | Verify docusaurus.config.js has correct baseUrl |
| FastAPI CORS issues | Frontend origin not allowed | Add wildcard or specific GitHub Pages origin to CORS middleware |
| Neon connection pool exhausted | Too many concurrent requests | Reduce FastAPI worker count, increase Neon connection pool |

## Scalability Notes
- **Vectorization**: Pre-compute all embeddings once, cache in Qdrant
- **Search**: Qdrant automatically optimizes with HNSW index
- **Frontend**: GitHub Pages serves static assets via CDN
- **Backend**: Use async FastAPI + uvicorn workers
- **Database**: Neon auto-scales, connection pooling via PgBouncer
- **LLM calls**: Implement token budgeting + response caching

---

## Next: See FOLDER_STRUCTURE.md and SETUP_ORDER.md
