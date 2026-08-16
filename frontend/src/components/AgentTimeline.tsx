"use client";

import React, { useState, useEffect } from "react";
import {
  CheckCircle2,
  CircleDashed,
  Loader2,
  Terminal,
  Cpu,
  Globe,
  Network,
  Users,
  DollarSign,
  Search,
  FileCheck2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface AgentTimelineProps {
  currentStage: string;
  currentMessage: string;
  logs: string[];
}

const AGENT_PIPELINE = [
  {
    id: "planning",
    title: "1. Planner Strategist Agent",
    desc: "Phân rã bài toán, tạo bộ search queries & chiến lược cào dữ liệu",
    icon: Cpu,
  },
  {
    id: "scraping",
    title: "2. Web Crawler & Scraping Agent",
    desc: "Cào nội dung trang web đối thủ, sàn TMĐT & diễn đàn thời gian thực",
    icon: Globe,
  },
  {
    id: "graph_rag",
    title: "3. Knowledge Graph Engine (LlamaIndex + ChromaDB)",
    desc: "Trích xuất thực thể, bóc tách Property Graph & lưu vector",
    icon: Network,
  },
  {
    id: "competitor_analysis",
    title: "4. Competitor & Niche Analyst",
    desc: "Phân tích SWOT, định vị thương hiệu & khoảng trống thị trường (Gaps)",
    icon: Users,
  },
  {
    id: "pricing_risk",
    title: "5. Pricing & Risk Strategist",
    desc: "Tính toán phân khúc giá, biên lợi nhuận & ma trận quản trị rủi ro",
    icon: DollarSign,
  },
  {
    id: "seo_gtm",
    title: "6. SEO & Commercial Intent Specialist",
    desc: "Bóc tách từ khóa tìm kiếm cao, content angle & lộ trình Go-To-Market",
    icon: Search,
  },
  {
    id: "synthesizing",
    title: "7. Chief Editor & Synthesis Agent",
    desc: "Tổng hợp toàn bộ tri thức thành Báo cáo Chiến lược hoàn chỉnh",
    icon: FileCheck2,
  },
];

export const AgentTimeline: React.FC<AgentTimelineProps> = ({
  currentStage,
  currentMessage,
  logs,
}) => {
  const [seconds, setSeconds] = useState(0);
  const [showLogs, setShowLogs] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const remainingSecs = sec % 60;
    return `${mins.toString().padStart(2, "0")}:${remainingSecs.toString().padStart(2, "0")}s`;
  };

  const getStageIndex = (stageId: string) => {
    if (stageId === "completed") return AGENT_PIPELINE.length;
    const idx = AGENT_PIPELINE.findIndex((a) => a.id === stageId);
    return idx >= 0 ? idx : 0;
  };

  const activeIdx = getStageIndex(currentStage);
  const progressPercent = Math.min(100, Math.round(((activeIdx + 0.5) / AGENT_PIPELINE.length) * 100));

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Main Execution Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl space-y-6 relative overflow-hidden">
        {/* Glowing Ambient Top Light */}
        <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-32 bg-indigo-500/20 blur-3xl pointer-events-none" />

        {/* Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <Loader2 className="w-5 h-5 animate-spin" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-bold text-slate-100">
                Multi-Agent Workflow Đang Thực Thi
              </h3>
              <p className="text-xs text-slate-400">
                Tự động thu thập dữ liệu & suy luận tri thức với Gemini 2.0 Flash
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <div className="px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700 font-mono text-indigo-300">
              Thời gian: <span className="font-bold text-slate-100">{formatTime(seconds)}</span>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-indigo-950/60 border border-indigo-800 font-mono text-indigo-300">
              Tiến độ: <span className="font-bold">{progressPercent}%</span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
          <div
            className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Current Activity Banner */}
        <div className="bg-indigo-950/40 border border-indigo-500/30 p-3.5 rounded-2xl flex items-center space-x-3">
          <span className="relative flex h-3 w-3 flex-shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
          </span>
          <p className="text-xs sm:text-sm font-medium text-indigo-200 truncate">
            {currentMessage || "Đang khởi tạo các Agent tác vụ..."}
          </p>
        </div>

        {/* 7 Agents Stepper */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
          {AGENT_PIPELINE.map((agent, idx) => {
            const isCompleted = activeIdx > idx || currentStage === "completed";
            const isCurrent = activeIdx === idx && currentStage !== "completed";
            const Icon = agent.icon;

            return (
              <div
                key={agent.id}
                className={`p-3.5 rounded-2xl border transition-all flex items-start space-x-3 ${
                  isCurrent
                    ? "bg-indigo-950/40 border-indigo-500/60 shadow-lg shadow-indigo-950/50 ring-1 ring-indigo-500/40"
                    : isCompleted
                    ? "bg-slate-800/40 border-slate-700/60 text-slate-300"
                    : "bg-slate-900/40 border-slate-800/60 text-slate-500 opacity-60"
                }`}
              >
                <div
                  className={`p-2 rounded-xl flex-shrink-0 mt-0.5 ${
                    isCurrent
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : isCompleted
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                      : "bg-slate-800 text-slate-600"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                <div className="flex-1 min-w-0 space-y-0.5">
                  <div className="flex items-center justify-between">
                    <h4
                      className={`text-xs font-bold truncate ${
                        isCurrent
                          ? "text-indigo-300"
                          : isCompleted
                          ? "text-slate-200"
                          : "text-slate-500"
                      }`}
                    >
                      {agent.title}
                    </h4>
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 ml-1" />
                    ) : isCurrent ? (
                      <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin flex-shrink-0 ml-1" />
                    ) : (
                      <CircleDashed className="w-3.5 h-3.5 text-slate-700 flex-shrink-0 ml-1" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-tight">
                    {agent.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Terminal / Logs Output */}
        <div className="border border-slate-800 rounded-2xl overflow-hidden bg-slate-950">
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="w-full px-4 py-2.5 bg-slate-900 flex items-center justify-between text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <div className="flex items-center space-x-2">
              <Terminal className="w-3.5 h-3.5 text-indigo-400" />
              <span className="font-mono font-semibold">Nhật ký thực thi (Agent Activity Stream)</span>
            </div>
            {showLogs ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showLogs && (
            <div className="p-4 font-mono text-[11px] space-y-1.5 max-h-44 overflow-y-auto custom-scrollbar text-slate-300">
              {logs.length === 0 ? (
                <p className="text-slate-600 italic">&gt; Đang chờ tín hiệu từ Agent Server...</p>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <span className="text-indigo-400 font-bold select-none">&gt;</span>
                    <span className="text-slate-300">{log}</span>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
