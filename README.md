# Physical AI & Humanoid Robotics Textbook

A comprehensive, interactive online textbook for learning robotics and AI with an embedded RAG chatbot, multi-language support, and personalized learning paths.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Git
- Docker (optional)

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/robotics-ai-textbook.git
cd robotics-ai-textbook

# Frontend
cd frontend
npm install
npm run start  # http://localhost:3000

# Backend (in another terminal)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
```

## 📚 Features

- ✅ **Docusaurus-based textbook** with 8 chapters covering ROS 2, Gazebo, NVIDIA Isaac, VLA, Whisper, and humanoid robotics
- ✅ **RAG Chatbot** embedded in every page for contextual Q&A
- ✅ **Multi-language** support (English & Urdu)
- ✅ **Personalized learning** with progress tracking and quiz scores
- ✅ **GitHub Pages deployment** for instant hosting
- ✅ **OpenAI integration** for intelligent answers
- ✅ **Qdrant vector DB** for semantic search
- ✅ **Neon Postgres** for data persistence
- ✅ **Better Auth** for GitHub/Google SSO login
- ✅ **Responsive design** for mobile devices

## 📁 Project Structure

See [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) for detailed layout.

```
robotics-ai-textbook/
├── frontend/              # Docusaurus site
│   ├── docs/             # Course content (EN + UR)
│   └── src/              # React components
├── backend/              # FastAPI server
│   ├── app/              # Main application
│   ├── scripts/          # Vectorization & utilities
│   └── Dockerfile        # Container image
├── .github/workflows/    # CI/CD pipelines
└── docs/                 # Documentation files
```

## 🔧 Setup & Deployment

### 1. Cloud Services Setup

1. **Neon Postgres**: https://console.neon.tech
   - Create project and get connection string
   - Save to `NEON_CONNECTION_URL` in GitHub Secrets

2. **Qdrant Cloud**: https://console.qdrant.io
   - Create cluster
   - Save `QDRANT_URL` and `QDRANT_API_KEY`

3. **OpenAI API**: https://platform.openai.com/api-keys
   - Get API key
   - Save to `OPENAI_API_KEY`

### 2. Frontend Deployment

```bash
cd frontend
npm run build
# Push to GitHub - GitHub Actions auto-deploys to GitHub Pages
```

Visit: `https://yourusername.github.io/robotics-ai-textbook/`

### 3. Backend Deployment

```bash
# Option 1: Render.com
# 1. Connect GitHub repo to Render
# 2. Set environment variables
# 3. Deploy command: uvicorn app.main:app --host 0.0.0.0

# Option 2: Railway
# railway link
# railway up
```

### 4. GitHub Actions Secrets

Add to your repo Settings → Secrets:

```
DATABASE_URL=postgresql://...
QDRANT_URL=https://...
QDRANT_API_KEY=...
OPENAI_API_KEY=sk-...
API_URL=https://your-api.herokuapp.com
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

## 📖 Content Structure

Chapters included:
1. Introduction to Robotics & AI
2. ROS 2 Fundamentals
3. Gazebo Simulation
4. Unity Integration
5. NVIDIA Isaac
6. Vision Language Models (VLA)
7. Whisper Audio Processing
8. Humanoid Robotics Control

Each chapter:
- Detailed explanations
- Code examples
- Interactive diagrams
- End-of-chapter quiz
- Related resources

## 🤖 RAG Chatbot

The embedded chatbot uses:
- **Vectorization**: Content chunks are pre-embedded with OpenAI embeddings
- **Search**: Qdrant performs semantic search on user queries
- **Context**: Retrieved chunks provide context for LLM
- **Generation**: GPT-4 generates contextual answers
- **Filtering**: Selected text can limit answers to specific sections

### Ask Questions
- Select any text → chatbot appears with pre-filled context
- Or type your question directly
- Chatbot returns sources for further reading

## 🌐 Multi-Language Support

### English & Urdu

- **Frontend**: Language toggle in header
- **Content**: Separate markdown files for each language
- **Embeddings**: Separate Qdrant collections (robotics_en, robotics_ur)
- **UI**: RTL support for Urdu

Switch language:
1. Click language selector in navbar
2. Content and chatbot switch to selected language

## 👤 User Authentication

### GitHub & Google Sign-In

1. Click "Sign In" button
2. Choose provider (GitHub or Google)
3. Authorize and get redirected back
4. Session stored in httpOnly cookies
5. Progress saved per user account

### Personalization Features

- Track progress per chapter
- Save bookmarks
- Quiz scores stored
- Recommendations based on weak areas
- Learning preferences (language, pace)

## 📊 Personalization & Analytics

### User Progress Tracking

- Chapter completion percentage
- Bookmark history
- Quiz scores
- Time spent reading
- Preferred language

### Recommendations

- Weak areas identified from quiz scores
- Suggested chapters to review
- Personalized learning path

## 🛠️ Development

### Frontend Setup

```bash
cd frontend

# Install
npm install

# Dev server
npm run start

# Build
npm run build

# Type checking
npm run lint
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Dev server
uvicorn app.main:app --reload

# Vectorize content
python scripts/vectorize_content.py --source ../frontend/docs/en --upload --language en
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests (if added)
cd frontend
npm test
```

## 📚 API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/chat` - Send query to chatbot
- `POST /api/vector-search` - Search knowledge base
- `GET /api/personalization/{user_id}` - Get user progress
- `POST /api/personalization/{user_id}/{chapter_id}` - Update progress
- `POST /api/auth/*` - Authentication endpoints

## 🚀 Performance Tips

- **Frontend**: GitHub Pages CDN serves static content globally
- **Backend**: Async FastAPI with connection pooling
- **Database**: Neon auto-scales, PgBouncer connection pooling
- **Vectors**: Qdrant HNSW index for fast search
- **Caching**: Optional Redis for frequently asked questions

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and fixes.

### Common Problems

| Issue | Solution |
|-------|----------|
| API returns 404 | Verify backend is running, check CORS config |
| Chatbot not responding | Check OpenAI API key, verify Qdrant connection |
| GitHub Pages not deploying | Check baseUrl in docusaurus.config.js |
| Urdu text shows as boxes | Install Noto Sans Urdu font |
| Database connection fails | Verify DATABASE_URL environment variable |

## 📝 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design & data flow
- [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) - Project organization
- [SETUP_ORDER.md](SETUP_ORDER.md) - Installation steps
- [7DAY_ROADMAP.md](7DAY_ROADMAP.md) - Implementation timeline
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues & fixes

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Docusaurus](https://docusaurus.io/) - Documentation framework
- [Qdrant](https://qdrant.tech/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [OpenAI](https://openai.com/) - LLM & embeddings
- [Neon](https://neon.tech/) - Serverless Postgres

## 📞 Support

- GitHub Issues: [Create an issue](https://github.com/yourusername/robotics-ai-textbook/issues)
- Discussions: [Start a discussion](https://github.com/yourusername/robotics-ai-textbook/discussions)
- Email: your-email@example.com

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core textbook & RAG chatbot
- ✅ Multi-language (EN/UR)
- ✅ GitHub Pages deployment

### Phase 2
- [ ] Advanced personalization with ML
- [ ] Claude Code subagents for coding help
- [ ] Community forums
- [ ] Video lectures

### Phase 3
- [ ] Mobile app (React Native)
- [ ] Live coding sessions
- [ ] Certification quizzes
- [ ] Industry partnerships

---

**Built with ❤️ for robotics and AI enthusiasts**
