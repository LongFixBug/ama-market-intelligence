"use client";

import React from "react";
import { Check, Search, TrendingUp, BarChart3, Loader2 } from "lucide-react";

interface AgentTimelineProps {
  currentStage: string;
  currentMessage: string;
}

const STAGES = [
  {
    id: "planning",
    title: "Xác thực & Định tuyến",
    desc: "Đánh giá từ khóa & phạm vi kinh doanh",
    icon: Search,
  },
  {
    id: "scraping",
    title: "Thu thập Dữ liệu Thị trường",
    desc: "Tổng hợp thông tin xu hướng & đối thủ",
    icon: TrendingUp,
  },
  {
    id: "synthesizing",
    title: "Xây dựng Báo cáo Chiến lược",
    desc: "Trích xuất ngách, giá tối ưu & rủi ro",
    icon: BarChart3,
  },
];

export const AgentTimeline: React.FC<AgentTimelineProps> = ({ currentStage }) => {
  const getStageIndex = (stage: string) => {
    if (stage === "planning") return 0;
    if (stage === "scraping" || stage === "graph_rag" || stage === "analyzing") return 1;
    if (stage === "synthesizing") return 2;
    if (stage === "completed") return 3;
    return 0;
  };

  const activeIdx = getStageIndex(currentStage);

  return (
    <div className="w-full max-w-4xl mx-auto bg-slate-900/60 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-ping" />
          <span className="font-semibold text-slate-300">Tiến trình tổng hợp báo cáo</span>
        </div>
        <span className="text-slate-400 font-mono">
          {currentStage === "completed" ? "Đã hoàn tất báo cáo!" : "Đang xử lý đa tác tử..."}
        </span>
      </div>

      {/* 3 Stepper Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {STAGES.map((s, idx) => {
          const isDone = activeIdx > idx;
          const isRunning = activeIdx === idx && currentStage !== "completed";
          const Icon = s.icon;

          return (
            <div
              key={s.id}
              className={`p-4 rounded-2xl border transition-all flex items-start space-x-3 ${
                isDone
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : isRunning
                  ? "bg-indigo-950/40 border-indigo-500/60 ring-1 ring-indigo-500/40 text-indigo-200 shadow-md"
                  : "bg-slate-900/40 border-slate-800 text-slate-500"
              }`}
            >
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                  isDone
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                    : isRunning
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-800 text-slate-600"
                }`}
              >
                {isDone ? (
                  <Check className="w-4 h-4 text-emerald-400 stroke-3" />
                ) : isRunning ? (
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                ) : (
                  <Icon className="w-3.5 h-3.5" />
                )}
              </div>

              <div className="space-y-0.5 min-w-0">
                <div className="flex items-center space-x-1.5">
                  <Icon className="w-3.5 h-3.5" />
                  <h4 className="text-xs font-bold truncate">{s.title}</h4>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-1 leading-tight">{s.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
