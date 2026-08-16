# AMA-System (Automated Market Analysis System)
> **Hệ thống Nghiên cứu Thị trường Tự động ứng dụng Multi-Agent + GraphRAG**  
> *Rút ngắn quy trình từ 8 giờ nghiên cứu thủ công xuống còn 2–3 phút.*

---

## 🏛️ Kiến Trúc Hệ Thống (3 Tầng Độc Lập: FE &bull; BE &bull; ML)

Dự án được phân chia độc lập thành 3 module rõ ràng:

```text
agentic-ai/
├── frontend/             # 1. FRONTEND (FE) - Next.js 15+ App Router, TailwindCSS, Recharts
│   ├── src/
│   │   ├── app/          # Giao diện chính & Metadata
│   │   ├── components/   # Multi-tab Dashboard, Timeline SSE Stepper, Graph Viewer
│   │   ├── data/         # Mock datasets & Generator
│   │   └── types/        # TypeScript interfaces khớp 100% với ML Schemas
│   └── package.json
│
├── backend/              # 2. BACKEND GATEWAY (BE) - FastAPI, SSE Stream, Session Management
│   ├── app/
│   │   ├── main.py       # API Router & EventSource SSE Endpoint
│   │   └── schemas.py    # Pydantic Data Contracts
│   ├── requirements.txt
│   └── .env.example
│
├── ml/                   # 3. MACHINE LEARNING & AI (ML) - Multi-Agent, GraphRAG, Crawlers
│   ├── agents/           # 7 Autonomous Agents (Planner, Crawler, Analyst, etc.)
│   ├── graphrag/         # LlamaIndex Property Graph, ChromaDB Embeddings, Triples
│   ├── crawlers/         # Tavily Search API, Playwright Scraper, HTML Sanitizer
│   ├── pipelines/        # End-to-End Orchestrator Pipeline
│   ├── schemas/          # Pydantic Schemas & Graph Nodes
│   └── requirements.txt
│
├── ARCHITECTURE.md       # Bản thiết kế kiến trúc toàn diện
└── README.md
```

---

## 🚀 Hướng dẫn Chạy Nhanh

### 1. Khởi động Frontend (`/frontend`)

```bash
cd frontend
npm run dev
```
Truy cập: **[http://localhost:3000](http://localhost:3000)**  
*(Có sẵn chế độ **Demo / Mock Simulation** độc lập để bạn bấm trải nghiệm toàn bộ UI/UX ngay lập tức).*

---

### 2. Khởi động Backend & AI Service (`/backend` + `/ml`)

```bash
# 1. Tạo môi trường ảo Python
python3 -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate

# 2. Cài đặt thư viện Backend & ML
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
playwright install chromium

# 3. Cấu hình API Keys trong backend/.env
cp backend/.env.example backend/.env

# 4. Chạy FastAPI Server Gateway
uvicorn backend.app.main:app --reload --port 8000
```
