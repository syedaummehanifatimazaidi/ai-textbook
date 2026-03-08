# Troubleshooting & Common Failure Points

## Backend Issues

### 1. FastAPI Won't Start
**Error:** `ModuleNotFoundError: No module named 'fastapi'`
**Fix:**
```bash
cd backend
uv pip install -r requirements.txt
# OR
pip install fastapi uvicorn
```

**Error:** `Address already in use: ('0.0.0.0', 8000)`
**Fix:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows - get PID, then: taskkill /PID xxxx /F
# Or change port:
uvicorn app.main:app --port 8001
```

### 2. Database Connection Fails
**Error:** `psycopg.OperationalError: connection failed`
**Fix:**
- Verify DATABASE_URL in `.env`:
  ```
  postgresql://user:password@ep-xxxxx.neon.tech/dbname?sslmode=require
  ```
- Check Neon console: project active?
- Whitelist IP: Neon dashboard → Connection details → check IP whitelist
- Test connection:
  ```bash
  psql $DATABASE_URL -c "SELECT 1"
  ```

**Error:** `sqlalchemy.exc.ProgrammingError: unknown encoding: utf-8`
**Fix:**
```bash
# This usually means Alembic migration failed
cd backend/app/database
alembic current                    # Check current version
alembic downgrade -1               # Rollback last migration
alembic upgrade head               # Re-apply cleanly
```

### 3. Qdrant Connection Issues
**Error:** `qdrant_client.http_exceptions.UnexpectedResponse: 404`
**Fix:**
- Check QDRANT_URL is correct (with protocol + port):
  ```
  https://xxxxx-xxx-xxx.eu-0.qdrant.io:6333
  ```
- Verify API key: `QDRANT_API_KEY` in Qdrant dashboard
- Check collection exists:
  ```python
  from qdrant_client import QdrantClient
  client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
  client.get_collections()  # Should list robotics_en, robotics_ur
  ```

**Error:** `payload schema mismatch`
**Fix:**
- Ensure metadata in vectorization matches schema:
  ```python
  # All chunks must have:
  # {
  #   "id": int,
  #   "text": str,
  #   "chapter": str,
  #   "section": str,
  #   "language": str,
  #   "order": int
  # }
  ```

### 4. OpenAI API Errors
**Error:** `openai.error.AuthenticationError: Incorrect API key`
**Fix:**
- Verify `OPENAI_API_KEY`:
  - Should start with `sk-`
  - Copied from https://platform.openai.com/account/api-keys
  - Not expired

**Error:** `openai.error.RateLimitError: Rate limit exceeded`
**Fix:**
```python
# Add exponential backoff:
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def call_openai_with_retry(query):
    return await openai.Embedding.create(input=query, model="text-embedding-3-small")
```

**Error:** `openai.error.ContextLengthExceededError: This model's maximum context length is 4096`
**Fix:**
- Check token count before sending to LLM:
  ```python
  import tiktoken
  encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
  tokens = encoding.encode(context)
  if len(tokens) > 3000:  # Leave buffer
      context = " ".join(tokens[:3000])  # Truncate
  ```

---

## Frontend Issues

### 5. Docusaurus Won't Build
**Error:** `Error: Unknown identifier: baseUrl`
**Fix:**
- Verify docusaurus.config.js syntax:
  ```javascript
  const config = {
    title: '...',
    url: 'https://yourusername.github.io',
    baseUrl: '/robotics-ai-textbook/',  // MUST end with /
    projectName: 'robotics-ai-textbook',
    organizationName: 'yourusername',
  };
  ```

**Error:** `Cannot find module '@docusaurus/core'`
**Fix:**
```bash
cd frontend
npm install       # Install all dependencies
npm install -D @docusaurus/core @docusaurus/preset-classic
npm run build
```

### 6. Chatbot Widget Not Appearing
**Error:** Component renders but not visible
**Fix:**
- Check z-index in CSS:
  ```css
  .chatbot-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;  /* Above GitHub Pages header */
  }
  ```
- Verify React component mounted:
  ```bash
  # In browser DevTools:
  # Elements tab → search for "chatbot-widget"
  # Verify it's in DOM
  ```

### 7. API Calls Return 404
**Error:** `fetch('http://localhost:8000/api/chat')` → 404
**Fix:**
- Verify backend running:
  ```bash
  curl http://localhost:8000/health  # Should return OK
  ```
- Check CORS headers:
  ```python
  # In backend/app/main.py:
  from fastapi.middleware.cors import CORSMiddleware
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],  # Add frontend URL
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

### 8. Authorization Token Not Working
**Error:** `401 Unauthorized` on personalization endpoints
**Fix:**
- Verify token being sent:
  ```typescript
  // frontend/src/services/api.ts
  const token = localStorage.getItem('authToken');
  const response = await fetch('/api/personalization/me', {
    headers: {
      'Authorization': `Bearer ${token}`  // Correct format
    }
  });
  ```
- Check token validity in backend:
  ```python
  # backend/app/api/middleware/auth.py
  token = request.headers.get('Authorization', '').replace('Bearer ', '')
  user_id = verify_token(token)  # Should not throw
  ```

### 9. Urdu Text Renders as Boxes
**Error:** Urdu characters show as ☐☐☐
**Fix:**
- Add Urdu font to Docusaurus:
  ```javascript
  // docusaurus.config.js
  themeConfig: {
    navbar: {
      // ...
    },
  },
  // Add to <head>:
  scripts: [
    {
      src: 'https://fonts.googleapis.com/css2?family=Noto+Sans+Urdu:wght@400;700&display=swap',
      async: true,
    },
  ],
  ```
- Update CSS:
  ```css
  body, html {
    font-family: 'Noto Sans Urdu', serif;
  }
  ```

### 10. GitHub Pages Deploy Fails
**Error:** `fatal: no changes added to commit`
**Fix:**
```bash
# Ensure .gitignore doesn't exclude /build:
cat frontend/.gitignore
# Should NOT have:
# /build
# dist
# build/

# If it does, remove these lines

# Then:
git add frontend/build
git commit -m "Build output"
git push origin main
```

**Error:** GitHub Actions job keeps failing
**Fix:**
- Check workflow file: `.github/workflows/deploy-frontend.yml`
  ```yaml
  - name: Deploy
    uses: peaceiris/actions-gh-pages@v3
    with:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      publish_dir: ./frontend/build
  ```
- Verify `publish_dir` matches actual build output path
- Check GitHub Actions logs for detailed errors

---

## Deployment Issues

### 11. Frontend Not Loading from GitHub Pages
**Error:** https://yourusername.github.io/robotics-ai-textbook/ → 404
**Fix:**
- Verify repo settings:
  - Settings → Pages → Source: Deploy from a branch
  - Branch: gh-pages
  - Folder: root
- Check baseUrl matches:
  ```javascript
  // docusaurus.config.js
  baseUrl: '/robotics-ai-textbook/',  // Must match repo name
  ```
- Force refresh (Ctrl+Shift+R on Windows/Linux, Cmd+Shift+R on macOS)

### 12. Backend Deployment to Render Fails
**Error:** `Command failed: npm install` in Render logs
**Fix:**
- Render expects Node.js for frontend or Python for backend, not both
- If deploying Flask/FastAPI to Render:
  - Set Build Command: (blank if no build needed)
  - Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Ensure Python version specified in `backend/runtime.txt`:
  ```
  python-3.11.0
  ```

**Error:** `Module not found: better_auth`
**Fix:**
```bash
# Verify backend/requirements.txt or pyproject.toml has:
better-auth==1.0.0
# Then rebuild Render deployment
```

### 13. Environment Variables Not Loading
**Error:** `OPENAI_API_KEY` is None
**Fix:**
- Check .env file location (should be in backend/ directory)
- Verify file is not in .gitignore:
  ```bash
  cat .gitignore | grep ".env"
  # If .env is listed, it won't be pushed to repo
  ```
- For production, set via platform:
  - Render: Dashboard → Environment
  - Railway: Variables tab
  - GitHub Actions: Settings → Secrets
  ```bash
  git push --all
  # Wait for automatic redeploy
  ```

---

## Vector Database Issues

### 14. Qdrant Search Returns No Results
**Error:** Top-k search returns empty even after upload
**Fix:**
```python
# Verify collection populated:
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
collection_info = client.get_collection("robotics_en")
print(collection_info.points_count)  # Should be > 0

# If 0, re-run vectorization:
python backend/scripts/vectorize_content.py --upload --force
```

### 15. Vectorization Takes Too Long
**Error:** 1000+ chunks ≈ 5-10 minutes
**Fix:**
- Use batch embedding:
  ```python
  # Instead of embedding one-by-one, batch:
  queries = [chunk.text for chunk in chunks]
  # Embed 20 at a time:
  for i in range(0, len(queries), 20):
      batch = queries[i:i+20]
      embeddings = openai.Embedding.create(
          input=batch,
          model="text-embedding-3-small"
      )
  ```
- Or pre-compute and cache for re-deployments

### 16. Similarity Search Returns Too-generic Results
**Error:** Query "ROS 2" returns chapters about Gazebo
**Fix:**
- Increase top-k:
  ```python
  search_result = client.search(
      collection_name="robotics_en",
      query_vector=query_embedding,
      limit=10,  # Increase from 5
      score_threshold=0.7,  # Add threshold
  )
  ```
- Check chunk metadata filtering:
  ```python
  # Apply chapter/section filter before scoring:
  if selected_text:
      search_result = [r for r in search_result if r.payload['chapter'] == chapter_id]
  ```

---

## Authentication Issues

### 17. Better Auth Session Not Persisting
**Error:** Login works, but session lost on page refresh
**Fix:**
- Check localStorage/cookies:
  ```javascript
  // browser console:
  localStorage.getItem('authToken')   // Should be non-empty
  document.cookie              // Should have session cookie
  ```
- Verify Better Auth middleware:
  ```python
  # backend/app/api/middleware/auth.py
  @app.middleware("http")
  async def auth_middleware(request: Request, call_next):
      token = request.cookies.get("session") or \
              request.headers.get("Authorization", "").replace("Bearer ", "")
      # ... verify token
  ```

### 18. GitHub OAuth Redirect Not Working
**Error:** After GitHub login, redirected to wrong URL
**Fix:**
- Verify GitHub App settings:
  - Settings → Developer settings → OAuth Apps
  - Callback URL: `https://yourdomain.com/api/auth/callback/github`
  - Must match exactly (including protocol + path)
- Check Better Auth config:
  ```python
  BetterAuth(
      github_client_id=GITHUB_CLIENT_ID,
      github_client_secret=GITHUB_CLIENT_SECRET,
      # Redirect must match GitHub App settings
  )
  ```

---

## Performance Issues

### 19. Chat Latency Too High (> 5 seconds)
**Fix (in order of priority):**
1. Check network: DevTools → Network tab
   - Embedding generation: should be < 1 sec
   - Qdrant search: should be < 500 ms
   - OpenAI LLM call: 2-3 secs
   - Total: < 5 secs

2. Optimize Qdrant:
   ```python
   search_result = client.search(
       collection_name="robotics_en",
       query_vector=query_embedding,
       limit=3,  # Reduce from 10
       exact=False,  # Use approximate search (faster)
   )
   ```

3. Cache frequent queries:
   ```python
   import redis
   cache = redis.Redis(host='localhost', port=6379)
   
   cache_key = f"rag:{query}"
   if cache.exists(cache_key):
       return json.loads(cache.get(cache_key))
   ```

4. Stream response instead of waiting for full LLM completion:
   ```python
   # Use streaming tokens rather than waiting for full response
   for chunk in openai.ChatCompletion.create(..., stream=True):
       yield chunk.choices[0].delta.content
   ```

### 20. Frontend Bundle Size Too Large
**Error:** Initial load slow on 4G
**Fix:**
```bash
cd frontend
npm run build --analyze

# Output should show bundle size
# Target: < 200KB for JS files

# Lazy load chatbot:
const ChatbotWidget = React.lazy(() => import('./components/ChatbotWidget'));
```

---

## Quick Reference: Common Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000       # Dev server
python scripts/vectorize_content.py --upload     # Populate Qdrant
alembic upgrade head                             # Run DB migrations
pytest tests/                                     # Run tests

# Frontend
cd frontend
npm run start                                     # Dev server
npm run build                                     # Build for production
npm run build --analyze                          # Analyze bundle

# Git
git status
git add .
git commit -m "message"
git push origin main                             # Triggers GH Actions
git pull origin main                             # Sync latest

# Database
psql $DATABASE_URL -c "SELECT count(*) FROM users;"  # Query Neon
psql $DATABASE_URL < backup.sql                  # Restore from backup

# Monitoring
curl http://localhost:8000/health                # Check backend health
curl http://localhost:3000                       # Check frontend
curl $QDRANT_URL/collections                     # Check Qdrant collections
```

---

## Still Stuck?

1. **Check logs:**
   - Frontend: Browser DevTools → Console
   - Backend: Terminal where uvicorn is running
   - Cloud: Render/Railway dashboard → Logs

2. **Enable debug mode:**
   ```python
   # backend/app/config.py
   DEBUG = True
   LOG_LEVEL = "DEBUG"
   ```

3. **Test endpoints individually:**
   ```bash
   # Test RAG without auth:
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is ROS 2?"}'
   ```

4. **Check GitHub Issues** on project repos for similar problems

5. **Post on Discord/Reddit with:**
   - Error message
   - Stack trace (full error)
   - Steps to reproduce
   - Environment (OS, Node/Python version)
