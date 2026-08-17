# AMA-System (Automated Market Analysis System)
> **Hệ thống Nghiên cứu Thị trường Tự động ứng dụng Multi-Agent + GraphRAG**  
> *Rút ngắn quy trình từ 8 giờ nghiên cứu thủ công xuống còn 2–3 phút.*

> **Trạng thái hiện tại:** đây là MVP chạy được, chưa phải production-ready. Luồng đang hoạt động là Next.js → FastAPI → pipeline LLM/Tavily → MarketReport → bounded agentic content campaign. Campaign đã có SQLite WAL snapshot/event/idempotency/duplicate reservation, cooperative lease cùng host và khôi phục scheduler sau restart; job queue, rate limiter phân tán, pub/sub SSE, tenant authentication và worker production vẫn chưa nối vào đường chạy chính.

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
├── backend/              # 2. BACKEND GATEWAY (BE) - FastAPI, SSE, validation, local guardrails
│   ├── app/
│   │   ├── main.py       # API Router & EventSource SSE Endpoint
│   │   └── services/     # Campaign store, bounded coordinator, publishers
│   │   └── schemas.py    # Pydantic Data Contracts
│   ├── requirements.txt
│   └── .env.example
│
├── ml/                   # 3. AI PIPELINE (ML) - planner/synthesis LLM + Tavily crawler
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

Backend mặc định chỉ cho phép frontend local `localhost:3000` và `127.0.0.1:3000`; khi triển khai cần đặt `APP_ENV=production`, `CORS_ORIGINS` là danh sách origin cụ thể, và đưa secret vào secret manager của nền tảng. API bất đồng bộ dùng `POST /api/analyze` rồi `GET /api/stream/{job_id}`. Sau khi có báo cáo, `POST /api/content-campaigns` tạo chiến dịch agentic; campaign token được dùng qua `Authorization: Bearer`, còn SSE lấy stream ticket ngắn hạn từ `/stream-ticket` để không đưa campaign token vào URL/log. `GET /api/content-campaigns/{id}/stream` phát tiến trình có replay event id và polling fallback khi request đi vào worker khác, rồi approval mới cho phép `POST /api/content-campaigns/{id}/publish`. Publish các biến thể chạy song song trong giới hạn, có idempotency, lease cùng host, lịch tối đa 31 ngày, duplicate-content guard và retry thủ công sau `needs_review`; không retry mù vì có thể tạo bài trùng khi provider timeout. `PUBLISH_MODE=mock` chỉ dùng để test local; live publish cần credentials cho WordPress, X, LinkedIn và/hoặc Facebook Page. `CAMPAIGN_STORE_PATH` mặc định là `backend/.data/content_campaigns.sqlite3` với WAL để giữ campaign sau restart trên cùng host. Muốn chạy nhiều instance trên nhiều host cần adapter Postgres/Redis cho state/lease, event pub/sub, queue và rate limiter; SQLite không phù hợp cho distributed scale.

TikTok chưa được bật trong connector này vì luồng chính thức cần video asset, quyền creator và quy trình consent riêng; hệ thống không giả lập hoặc né kiểm duyệt nền tảng.
