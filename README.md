# AMA-System (Automated Market Analysis System)
> **Hệ thống Nghiên cứu Thị trường Tự động ứng dụng Multi-Agent + GraphRAG**  
> *Rút ngắn quy trình từ 8 giờ nghiên cứu thủ công xuống còn 2–3 phút.*

---

## 🏗️ Cấu trúc Hệ thống

- **Frontend (`/frontend`)**: Next.js 14/15, TypeScript, TailwindCSS, Recharts, Lucide Icons, Canvas Confetti.
  - Hỗ trợ cả **Live SSE Stream** từ Backend lẫn chế độ **Demo / Mock Simulation** độc lập để test UI ngay lập tức.
  - Đầy đủ 7 Tab: Tổng quan & Persona, Đối thủ & SWOT, Định giá (Recharts), Rủi ro, Từ khóa SEO, Đồ thị Tri thức (GraphRAG SVG Viewer), Lộ trình GTM.
  - Xuất báo cáo Markdown, JSON, In/PDF, Quản lý lịch sử phiên (LocalStorage).
- **Backend (`/backend`)**: FastAPI, LlamaIndex Property Graph, ChromaDB, Gemini 2.0 Flash API, Tavily Search, Playwright.

---

## 🚀 Hướng dẫn Chạy Nhanh

### 1. Khởi động Frontend (Chạy ngay lập tức)

```bash
cd frontend
npm run dev
```

Truy cập: [http://localhost:3000](http://localhost:3000)  
*(Mặc định bật sẵn **Demo / Mock Mode** để bạn bấm phân tích các chủ đề mẫu và trải nghiệm toàn bộ UI/UX ngay lập tức!)*

---

### 2. Khởi động Backend (Khi bạn phát triển Backend & AI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
pip install -r requirements.txt

# Cấu hình API Keys trong file backend/.env
cp .env.example .env

# Chạy server FastAPI
uvicorn app.main:app --reload --port 8000
```

Trong giao diện Frontend, bấm nút ⚙️ (Cài đặt) ở góc trên bên phải, tắt **Chế độ Demo / Mock Mode** để chuyển sang kết nối trực tiếp với FastAPI Backend qua Server-Sent Events (SSE).
