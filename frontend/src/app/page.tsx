"use client";

import { useState, useEffect } from "react";
import confetti from "canvas-confetti";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { ConfigModal } from "@/components/ConfigModal";
import { AgentTimeline } from "@/components/AgentTimeline";
import { ReportDashboard } from "@/components/ReportDashboard";
import { MarketReport } from "@/types/report";
import { MOCK_REPORTS, generateDynamicMockReport } from "@/data/mockReports";
import {
  Sparkles,
  ArrowRight,
  Search,
  Lightbulb,
  Zap,
  TrendingUp,
  ShieldCheck,
  Globe2,
  PieChart,
  Bot,
} from "lucide-react";

export default function Home() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState("");
  const [currentMessage, setCurrentMessage] = useState("");
  const [logs, setLogs] = useState<string[]>([]);
  const [report, setReport] = useState<MarketReport | null>(null);

  // App settings & drawers
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isMockMode, setIsMockMode] = useState(true);
  const [backendUrl, setBackendUrl] = useState("http://localhost:8000");
  const [history, setHistory] = useState<MarketReport[]>([]);

  // Load history from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("ama_history");
      if (saved) {
        setHistory(JSON.parse(saved));
      } else {
        // Pre-populate with mock samples
        setHistory(Object.values(MOCK_REPORTS));
      }
      const savedUrl = localStorage.getItem("ama_backend_url");
      if (savedUrl) setBackendUrl(savedUrl);
      const savedMock = localStorage.getItem("ama_mock_mode");
      if (savedMock !== null) setIsMockMode(savedMock === "true");
    } catch (e) {
      console.error(e);
    }
  }, []);

  const saveReportToHistory = (newReport: MarketReport) => {
    const updated = [newReport, ...history.filter((h) => h.id !== newReport.id)].slice(0, 20);
    setHistory(updated);
    try {
      localStorage.setItem("ama_history", JSON.stringify(updated));
    } catch (e) {
      console.error(e);
    }
  };

  const clearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem("ama_history");
    } catch (e) {
      console.error(e);
    }
  };

  // Mock Multi-Agent Simulator
  const runMockSimulation = async (searchTopic: string) => {
    const mockSteps = [
      {
        stage: "planning",
        msg: `[Planner Agent] Đang phân rã đề tài '${searchTopic}' thành 4 giả thuyết & 8 truy vấn tìm kiếm...`,
        logs: [
          "Xác định bài toán nghiên cứu thị trường mục tiêu...",
          "Tạo bộ truy vấn SERP: competitor benchmark, pricing breakdown, market painpoints, risk factors.",
          "Phân công nhiệm vụ cho Web Crawler Agent...",
        ],
        delay: 2000,
      },
      {
        stage: "scraping",
        msg: "[Web Crawler] Đang cào dữ liệu từ 15+ website đối thủ, bài đánh giá & sàn TMĐT...",
        logs: [
          "Truy vấn Google Search API qua Tavily/Serper...",
          "Cào dữ liệu chi tiết landing page đối thủ bằng Playwright...",
          "Lọc bỏ HTML rác, làm sạch 18,500 từ văn bản nội dung...",
        ],
        delay: 2500,
      },
      {
        stage: "graph_rag",
        msg: "[Knowledge Graph Engine] Đang trích xuất thực thể (Entities) và liên kết đồ thị LlamaIndex...",
        logs: [
          "Bóc tách thực thể: Competitor, Product, PricePoint, TargetAudience, Risk.",
          "Thiết lập mối quan hệ: COMPETES_WITH, PRICED_AT, TARGETS, HAS_RISK.",
          "Đồng bộ Embeddings vào ChromaDB Vector Store...",
        ],
        delay: 2500,
      },
      {
        stage: "competitor_analysis",
        msg: "[Competitor Analyst] Đang bóc tách ma trận SWOT, khoảng trống thị trường (Gaps)...",
        logs: [
          "So sánh điểm mạnh & điểm yếu của các thương hiệu hàng đầu...",
          "Phát hiện 3 khoảng trống thị trường lớn chưa có bên nào khai thác triệt để...",
        ],
        delay: 2000,
      },
      {
        stage: "pricing_risk",
        msg: "[Pricing & Risk Strategist] Đang mô phỏng độ co giãn giá & ma trận giảm thiểu rủi ro...",
        logs: [
          "Tính toán phân vị giá tối thiểu, trung vị và sweet spot...",
          "Xây dựng 3 gói định giá phân tầng (3-Tier Pricing Model)...",
          "Đánh giá rủi ro chuỗi cung ứng, pháp lý và chiến lược phòng thủ...",
        ],
        delay: 2000,
      },
      {
        stage: "seo_gtm",
        msg: "[SEO & GTM Specialist] Đang phân tích bộ từ khóa tìm kiếm thương mại & lộ trình GTM...",
        logs: [
          "Phân loại từ khóa theo Commercial Intent và Search Volume...",
          "Gợi ý góc tiếp cận nội dung (Content Angles) cho chiến dịch ra mắt...",
        ],
        delay: 1800,
      },
      {
        stage: "synthesizing",
        msg: "[Chief Editor] Đang tổng hợp báo cáo chiến lược doanh nghiệp hoàn chỉnh...",
        logs: [
          "Kiểm định tính nhất quán dữ liệu qua Schema Pydantic...",
          "Định dạng bảng biểu, ma trận và biểu đồ thị trường...",
        ],
        delay: 1500,
      },
    ];

    for (const step of mockSteps) {
      setCurrentStage(step.stage);
      setCurrentMessage(step.msg);
      for (const l of step.logs) {
        setLogs((prev) => [...prev, l]);
      }
      await new Promise((r) => setTimeout(r, step.delay));
    }

    // Generate result
    const resultReport = generateDynamicMockReport(searchTopic);
    setReport(resultReport);
    saveReportToHistory(resultReport);
    setCurrentStage("completed");
    setCurrentMessage("✅ Đã hoàn tất báo cáo thị trường!");
    setLoading(false);

    try {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 },
      });
    } catch (e) {}
  };

  // Live Backend SSE Runner
  const runLiveAnalysis = async (searchTopic: string) => {
    const jobId = "job_" + Math.random().toString(36).substring(2, 9);
    const eventSource = new EventSource(`${backendUrl}/api/stream/${jobId}`);

    eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.stage) setCurrentStage(data.stage);
        if (data.message) {
          setCurrentMessage(data.message);
          setLogs((prev) => [...prev, data.message]);
        }
        if (data.report) {
          setReport(data.report);
          saveReportToHistory(data.report);
        }
        if (data.stage === "completed" || data.stage === "error") {
          eventSource.close();
          setLoading(false);
          if (data.stage === "completed") {
            try {
              confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
            } catch (e) {}
          }
        }
      } catch (err) {
        console.error("SSE parse error", err);
      }
    };

    eventSource.onerror = () => {
      setLogs((prev) => [
        ...prev,
        "⚠️ Không thể kết nối tới Backend SSE. Chuyển hướng sang chế độ Mock Simulation...",
      ]);
      eventSource.close();
      runMockSimulation(searchTopic);
    };

    // Trigger backend job
    try {
      await fetch(`${backendUrl}/api/analyze/${jobId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: searchTopic }),
      });
    } catch (err) {
      console.warn("Backend not available, fallback to mock", err);
      eventSource.close();
      runMockSimulation(searchTopic);
    }
  };

  const handleStartAnalysis = (targetTopic: string) => {
    const q = targetTopic.trim();
    if (!q || loading) return;

    setTopic(q);
    setLoading(true);
    setReport(null);
    setLogs([]);
    setCurrentStage("planning");
    setCurrentMessage("🚀 Đang khởi động hệ thống Multi-Agent...");

    if (isMockMode) {
      runMockSimulation(q);
    } else {
      runLiveAnalysis(q);
    }
  };

  const handleNewAnalysis = () => {
    setReport(null);
    setLoading(false);
    setTopic("");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 bg-grid-pattern relative selection:bg-indigo-500 selection:text-white flex flex-col">
      {/* Top Ambient Glow Gradient */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-indigo-500/15 via-purple-500/5 to-transparent blur-3xl pointer-events-none -z-10" />

      {/* Navbar */}
      <Navbar
        onNewAnalysis={handleNewAnalysis}
        onToggleSidebar={() => setIsSidebarOpen(true)}
        onOpenConfig={() => setIsConfigOpen(true)}
        isMockMode={isMockMode}
        historyCount={history.length}
      />

      {/* Sidebar Drawer */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        history={history}
        onSelectReport={(selected) => {
          setReport(selected);
          setTopic(selected.topic);
          setLoading(false);
        }}
        onClearHistory={clearHistory}
        activeReportId={report?.id}
      />

      {/* Config Modal */}
      <ConfigModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        backendUrl={backendUrl}
        onSaveBackendUrl={(url) => {
          setBackendUrl(url);
          localStorage.setItem("ama_backend_url", url);
        }}
        isMockMode={isMockMode}
        onToggleMockMode={(val) => {
          setIsMockMode(val);
          localStorage.setItem("ama_mock_mode", String(val));
        }}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
        {/* Search Hero Section (Shown when no report or when creating new) */}
        {!report && !loading && (
          <section className="text-center space-y-5 pt-8 pb-4">
            <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold shadow-sm">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Nền Tảng Nghiên Cứu Thị Trường & Chiến Lược Kinh Doanh Tự Động</span>
            </div>

            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight max-w-4xl mx-auto leading-tight text-slate-100">
              Nghiên Cứu Thị Trường &bull; Multi-Agent + GraphRAG
            </h1>

            <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
              Nhập bất kỳ sản phẩm hoặc ngách kinh doanh nào để nhận ngay bản báo cáo toàn diện:
              Phân tích khoảng trống thị trường, Chiến lược định giá, Đánh giá rủi ro và Bộ từ khóa SEO.
            </p>
          </section>
        )}

        {/* Search Bar */}
        {(!report || loading) && (
          <section className="max-w-3xl mx-auto space-y-4">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleStartAnalysis(topic);
              }}
              className="relative group"
            >
              <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 rounded-3xl blur opacity-30 group-hover:opacity-60 transition duration-300" />
              <div className="relative flex items-center bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-2xl p-2 shadow-2xl transition-colors">
                <div className="pl-4 pr-2 text-slate-500">
                  <Search className="w-5 h-5 group-focus-within:text-indigo-400 transition-colors" />
                </div>
                <input
                  type="text"
                  placeholder="Nhập chủ đề hoặc thị trường muốn phân tích (ví dụ: Nước ép đóng chai, Khóa học AI...)"
                  className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm sm:text-base px-2 py-2.5 focus:outline-none disabled:opacity-50 font-medium"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !topic.trim()}
                  className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-sm transition-all shadow-md shadow-indigo-600/30 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex-shrink-0"
                >
                  <span>Phân tích</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </form>

            {/* Quick Suggestions Chips */}
            {!loading && (
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <div className="flex items-center space-x-1 text-xs text-slate-500 font-medium mr-1">
                  <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
                  <span>Gợi ý mẫu:</span>
                </div>
                {[
                  "Thị trường mỹ phẩm thuần chay Việt Nam",
                  "Nước ép trái cây tươi đóng chai ngách văn phòng",
                  "Khóa học lập trình AI cho sinh viên ngành CNTT",
                  "Dịch vụ thiết kế website AI cho doanh nghiệp nhỏ",
                ].map((item) => (
                  <button
                    key={item}
                    onClick={() => handleStartAnalysis(item)}
                    className="text-xs px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-indigo-300 transition-all cursor-pointer text-left shadow-xs"
                  >
                    {item}
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Feature Highlights Grid (When Idle) */}
        {!report && !loading && (
          <section className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6">
            <div className="bg-slate-900/50 border border-slate-800/80 rounded-3xl p-6 space-y-3 hover:border-indigo-500/30 transition-all shadow-lg">
              <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-extrabold text-sm">
                01
              </div>
              <h4 className="text-sm font-bold text-slate-100">Phân tích Ngách & Đối thủ</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Tự động cào dữ liệu, xác định khoảng trống thị trường (Market Gaps) và bóc tách ma trận SWOT của các đối thủ dẫn đầu.
              </p>
            </div>

            <div className="bg-slate-900/50 border border-slate-800/80 rounded-3xl p-6 space-y-3 hover:border-indigo-500/30 transition-all shadow-lg">
              <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-extrabold text-sm">
                02
              </div>
              <h4 className="text-sm font-bold text-slate-100">Chiến lược Giá & Rủi ro</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Khám phá khoảng giá tối ưu (Sweet Spot) kèm cơ cấu đóng gói 3 gói sản phẩm và các biện pháp phòng ngừa rủi ro vận hành.
              </p>
            </div>

            <div className="bg-slate-900/50 border border-slate-800/80 rounded-3xl p-6 space-y-3 hover:border-indigo-500/30 transition-all shadow-lg">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-extrabold text-sm">
                03
              </div>
              <h4 className="text-sm font-bold text-slate-100">SEO & Đồ thị Tri thức</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Bóc tách bộ từ khóa có ý định mua hàng cao và trực quan hóa toàn bộ mối quan hệ mạng lưới qua GraphRAG.
              </p>
            </div>
          </section>
        )}

        {/* Live Execution Multi-Agent Stepper */}
        {loading && (
          <AgentTimeline
            currentStage={currentStage}
            currentMessage={currentMessage}
            logs={logs}
          />
        )}

        {/* Completed Report Dashboard */}
        {report && !loading && (
          <div className="space-y-6">
            <ReportDashboard report={report} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 bg-slate-950 py-6 mt-16 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <p>© 2026 AMA Market Intelligence Platform &bull; Multi-Agent + GraphRAG System</p>
          <div className="flex items-center space-x-4">
            <span className="hover:text-slate-400 transition-colors cursor-pointer">
              Báo cáo Doanh nghiệp
            </span>
            <span>&bull;</span>
            <span className="hover:text-slate-400 transition-colors cursor-pointer">
              LlamaIndex + ChromaDB
            </span>
            <span>&bull;</span>
            <span className="hover:text-slate-400 transition-colors cursor-pointer">
              Gemini 2.0 Flash
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
