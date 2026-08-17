"use client";

import { useState, useEffect, useRef } from "react";
import confetti from "canvas-confetti";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { ConfigModal } from "@/components/ConfigModal";
import { AgentTimeline } from "@/components/AgentTimeline";
import { ReportDashboard } from "@/components/ReportDashboard";
import { MarketReport } from "@/types/report";
import { MOCK_REPORTS, generateDynamicMockReport } from "@/data/mockReports";
import { Search, ArrowRight, Lightbulb, Sparkles, X } from "lucide-react";

export default function Home() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState("");
  const [currentMessage, setCurrentMessage] = useState("");
  const [report, setReport] = useState<MarketReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // App settings & drawers
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isMockMode, setIsMockMode] = useState(false);
  const [backendUrl, setBackendUrl] = useState("http://localhost:8000");
  const [history, setHistory] = useState<MarketReport[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Load browser-only settings after mount so SSR and hydration stay deterministic.
  useEffect(() => {
    const loadBrowserState = () => {
      try {
        const saved = localStorage.getItem("ama_history");
        if (saved) {
          const parsed: unknown = JSON.parse(saved);
          setHistory(Array.isArray(parsed) ? (parsed as MarketReport[]).slice(0, 20) : Object.values(MOCK_REPORTS));
        } else {
          setHistory(Object.values(MOCK_REPORTS));
        }
        const savedUrl = localStorage.getItem("ama_backend_url");
        if (savedUrl) setBackendUrl(savedUrl);
        const savedMock = localStorage.getItem("ama_mock_mode");
        if (savedMock !== null) setIsMockMode(savedMock === "true");
      } catch (error) {
        console.error("Unable to load browser state", error);
        setHistory(Object.values(MOCK_REPORTS));
      }
    };

    const timer = window.setTimeout(loadBrowserState, 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => () => eventSourceRef.current?.close(), []);

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
    const steps = [
      {
        stage: "planning",
        msg: "🔍 [Xác thực & Định tuyến] Đang đánh giá từ khóa & phạm vi kinh doanh...",
        delay: 1200,
      },
      {
        stage: "scraping",
        msg: "📈 [Thu thập Dữ liệu Thị trường] Đang tổng hợp thông tin xu hướng & đối thủ...",
        delay: 1500,
      },
      {
        stage: "synthesizing",
        msg: "📊 [Xây dựng Báo cáo Chiến lược] Đang trích xuất ngách, giá tối ưu & rủi ro...",
        delay: 1500,
      },
    ];

    for (const step of steps) {
      setCurrentStage(step.stage);
      setCurrentMessage(step.msg);
      await new Promise((r) => setTimeout(r, step.delay));
    }

    const resultReport = generateDynamicMockReport(searchTopic);
    setReport(resultReport);
    saveReportToHistory(resultReport);
    setCurrentStage("completed");
    setCurrentMessage("✅ Đã hoàn tất báo cáo!");
    setLoading(false);

    try {
      confetti({ particleCount: 70, spread: 60, origin: { y: 0.6 } });
    } catch (error) {
      console.error("Unable to show completion animation", error);
    }
  };

  // Live Backend SSE Runner. The server owns the job id; never start a second
  // direct request when the stream is slow because that doubles LLM cost.
  const runLiveAnalysis = async (searchTopic: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    let isCompleted = false;

    try {
      const triggerResponse = await fetch(`${backendUrl}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ topic: searchTopic }),
      });
      if (!triggerResponse.ok) {
        throw new Error(`Backend rejected the job (${triggerResponse.status})`);
      }

      const triggerData: { job_id?: string; stream_token?: string } = await triggerResponse.json();
      if (!triggerData.job_id || !triggerData.stream_token) {
        throw new Error("Backend did not return stream credentials");
      }

      const eventSource = new EventSource(
        `${backendUrl}/api/stream/${triggerData.job_id}?token=${encodeURIComponent(triggerData.stream_token)}`,
      );
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as {
            stage?: string;
            message?: string;
            report?: MarketReport;
          };
          if (data.stage) setCurrentStage(data.stage);
          if (data.message) setCurrentMessage(data.message);
          if (data.report) {
            setReport(data.report);
            saveReportToHistory(data.report);
          }
          if (data.stage === "completed") {
            isCompleted = true;
            eventSource.close();
            setLoading(false);
            try {
              confetti({ particleCount: 70, spread: 60, origin: { y: 0.6 } });
            } catch (error) {
              console.error("Unable to show completion animation", error);
            }
          } else if (data.stage === "error") {
            isCompleted = true;
            eventSource.close();
            setErrorMessage(data.message || "Phân tích thất bại. Vui lòng thử lại.");
            setLoading(false);
          }
        } catch (error) {
          console.error("SSE parse error", error);
        }
      };

      eventSource.onerror = () => {
        if (!isCompleted && eventSource.readyState === EventSource.CLOSED) {
          setErrorMessage("Mất kết nối tới Backend; vui lòng thử lại.");
          setLoading(false);
        }
      };
    } catch (error) {
      console.error("Unable to start analysis", error);
      setErrorMessage("Không thể khởi động phân tích. Kiểm tra Backend URL hoặc thử lại.");
      setLoading(false);
    }
  };

  const handleStartAnalysis = (targetTopic: string) => {
    const q = targetTopic.trim();
    if (!q || loading) return;

    setTopic(q);
    setLoading(true);
    setReport(null);
    setErrorMessage(null);
    setCurrentStage("planning");
    setCurrentMessage("🚀 Đang khởi động hệ thống phân tích...");

    if (isMockMode) {
      runMockSimulation(q);
    } else {
      runLiveAnalysis(q);
    }
  };

  const handleNewAnalysis = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setReport(null);
    setLoading(false);
    setTopic("");
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-100 bg-grid-pattern relative selection:bg-indigo-500 selection:text-white flex flex-col transition-colors duration-200">
      {/* Top Ambient Glow Gradient */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-indigo-500/10 via-indigo-500/5 to-transparent blur-3xl pointer-events-none -z-10" />

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

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Header Hero Section */}
        <section className="text-center space-y-4 pt-4 pb-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 text-xs font-semibold shadow-xs">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Nền Tảng Phân Tích & Nghiên Cứu Thị Trường Doanh Nghiệp</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight max-w-3xl mx-auto leading-tight text-slate-900 dark:text-slate-100">
            Nền Tảng Phân Tích Thị Trường & Xây Dựng Chiến Lược Kinh Doanh
          </h2>

          <p className="text-slate-600 dark:text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
            Nhập sản phẩm hoặc ngách kinh doanh để nhận báo cáo chiến lược toàn diện bao gồm: Thị trường ngách, Chiến lược giá tối ưu, Đánh giá rủi ro và Bộ từ khóa SEO.
          </p>
        </section>

        {/* Search Bar */}
        <section className="max-w-4xl mx-auto space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleStartAnalysis(topic);
            }}
            className="relative group"
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-indigo-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-300" />
            <div className="relative flex items-center bg-white/90 dark:bg-slate-950/90 backdrop-blur-xl border border-slate-200 dark:border-slate-800 rounded-2xl p-2 shadow-xl transition-colors">
              <div className="pl-4 pr-2 text-slate-400">
                <Search className="w-5 h-5 group-focus-within:text-indigo-600 dark:group-focus-within:text-indigo-400 transition-colors" />
              </div>
              <input
                type="text"
                placeholder="Nhập chủ đề hoặc thị trường muốn phân tích (ví dụ: Nước ép đóng chai, Khóa học AI...)"
                className="w-full bg-transparent text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-sm sm:text-base px-2 py-2 focus:outline-none disabled:opacity-50 font-medium"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={loading}
              />
              {topic && !loading && (
                <button
                  type="button"
                  onClick={() => setTopic("")}
                  className="p-1 text-slate-400 hover:text-slate-600 mr-2"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                type="submit"
                disabled={loading || !topic.trim()}
                className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-sm transition-all shadow-md shadow-indigo-500/20 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <span>Phân tích</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Quick Suggestions Chips */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <div className="flex items-center space-x-1 text-xs text-slate-500 dark:text-slate-400 font-medium mr-1">
              <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
              <span>Gợi ý:</span>
            </div>
            {[
              "kinh doanh kindle",
              "thị trường sách giấy việt nam",
              "Thị trường mỹ phẩm thuần chay Việt Nam",
              "Nước ép trái cây tươi đóng chai ngách văn phòng",
              "Khóa học lập trình AI cho sinh viên ngành CNTT",
            ].map((item) => (
              <button
                key={item}
                onClick={() => handleStartAnalysis(item)}
                className="text-xs px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-900/80 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors cursor-pointer text-left shadow-xs"
              >
                {item}
              </button>
            ))}
          </div>
        </section>

        {/* 3 Step Stepper */}
        {loading && (
          <AgentTimeline
            currentStage={currentStage}
            currentMessage={currentMessage}
          />
        )}

        {errorMessage && (
          <div role="alert" className="max-w-4xl mx-auto w-full rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {errorMessage}
          </div>
        )}

        {/* 3 Feature Preview Cards (When Idle) */}
        {!report && !loading && (
          <section className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
            <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-indigo-300 dark:hover:border-slate-700 transition-all shadow-xs">
              <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-bold text-sm">
                01
              </div>
              <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Phân tích Ngách & Thị trường
              </h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Xác định khoảng trống thị trường, cơ hội cạnh tranh và mô tả chi tiết tệp khách hàng mục tiêu.
              </p>
            </div>

            <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-indigo-300 dark:hover:border-slate-700 transition-all shadow-xs">
              <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-500/10 border border-orange-200 dark:border-orange-500/20 flex items-center justify-center text-orange-600 dark:text-orange-400 font-bold text-sm">
                02
              </div>
              <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Định giá & Hạn chế Rủi ro
              </h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Đề xuất khoảng giá kinh doanh tối ưu kèm đánh giá các rủi ro vận hành, tài chính & đối thủ.
              </p>
            </div>

            <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-indigo-300 dark:hover:border-slate-700 transition-all shadow-xs">
              <div className="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-bold text-sm">
                03
              </div>
              <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Tối ưu hóa Thương mại & SEO
              </h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Cung cấp bộ từ khóa tìm kiếm hàng đầu và gợi ý câu lệnh AI marketing hiệu quả cao.
              </p>
            </div>
          </section>
        )}

        {/* Master Report Dashboard */}
        {report && !loading && (
          <section className="space-y-6">
            <ReportDashboard report={report} backendUrl={backendUrl} isMockMode={isMockMode} />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-950/80 py-6 mt-12 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <p>© 2026 AMA Market Intelligence Platform &bull; Multi-Agent System</p>
          <div className="flex items-center space-x-4">
            <span className="hover:text-slate-700 dark:hover:text-slate-400 cursor-pointer">
              Báo cáo Phân tích Kinh doanh
            </span>
            <span>&bull;</span>
            <span className="hover:text-slate-700 dark:hover:text-slate-400 cursor-pointer">
              Bảo mật Enterprise
            </span>
            <span>&bull;</span>
            <span className="hover:text-slate-700 dark:hover:text-slate-400 cursor-pointer">
              Dữ liệu Thời gian thực
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
