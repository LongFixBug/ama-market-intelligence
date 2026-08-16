"use client";

import React from "react";
import { BrainCircuit, Activity, Settings2, History, PlusCircle, Sparkles } from "lucide-react";

interface NavbarProps {
  onNewAnalysis: () => void;
  onToggleSidebar: () => void;
  onOpenConfig: () => void;
  isMockMode: boolean;
  historyCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  onNewAnalysis,
  onToggleSidebar,
  onOpenConfig,
  isMockMode,
  historyCount,
}) => {
  return (
    <header className="w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-40 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Logo */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={onNewAnalysis}>
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 shadow-md shadow-indigo-500/25">
            <BrainCircuit className="w-5 h-5 text-white" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base sm:text-lg font-bold text-slate-100 tracking-tight">
                AMA Market Intelligence
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase rounded-full bg-indigo-950/70 text-indigo-400 border border-indigo-800">
                Enterprise
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Hệ thống Phân tích Thị trường Tự động &bull; Multi-Agent + GraphRAG
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Status badge */}
          <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs text-slate-300">
            <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span>Chế độ:</span>
            <span className={`font-semibold ${isMockMode ? "text-amber-400" : "text-emerald-400"}`}>
              {isMockMode ? "Demo / Mock Mode" : "Live Backend API"}
            </span>
          </div>

          {/* History Button */}
          <button
            onClick={onToggleSidebar}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 rounded-xl text-xs font-medium transition-all"
            title="Lịch sử phiên phân tích"
          >
            <History className="w-3.5 h-3.5 text-indigo-400" />
            <span className="hidden sm:inline">Lịch sử</span>
            {historyCount > 0 && (
              <span className="px-1.5 py-0.2 bg-indigo-600/30 text-indigo-300 text-[10px] rounded-full font-bold">
                {historyCount}
              </span>
            )}
          </button>

          {/* Settings / Config Button */}
          <button
            onClick={onOpenConfig}
            className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 rounded-xl text-xs transition-all"
            title="Cấu hình Backend & API URL"
          >
            <Settings2 className="w-4 h-4 text-slate-400" />
          </button>

          {/* New Analysis Button */}
          <button
            onClick={onNewAnalysis}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all cursor-pointer"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Phân tích mới</span>
          </button>
        </div>
      </div>
    </header>
  );
};
