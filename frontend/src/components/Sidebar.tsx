"use client";

import React from "react";
import { MarketReport } from "@/types/report";
import { X, Clock, Trash2, ChevronRight, Layers, Cpu, Database, Network } from "lucide-react";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  history: MarketReport[];
  onSelectReport: (report: MarketReport) => void;
  onClearHistory: () => void;
  activeReportId?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  history,
  onSelectReport,
  onClearHistory,
  activeReportId,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/60 backdrop-blur-xs" onClick={onClose} />

      {/* Slide-out Drawer */}
      <aside className="relative w-80 sm:w-96 bg-slate-950 border-r border-slate-800 h-full flex flex-col z-10 shadow-2xl">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-slate-100">Lịch sử phiên phân tích</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {history.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-xs space-y-2">
              <Clock className="w-8 h-8 mx-auto text-slate-700 stroke-1" />
              <p>Chưa có phiên phân tích nào được lưu.</p>
              <p className="text-[11px] text-slate-600">
                Hãy thực hiện phân tích một chủ đề để lưu lại kết quả.
              </p>
            </div>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  onSelectReport(item);
                  onClose();
                }}
                className={`p-3 rounded-xl border transition-all cursor-pointer text-left group ${
                  activeReportId === item.id
                    ? "bg-indigo-950/40 border-indigo-500/50 text-indigo-200"
                    : "bg-slate-900/60 border-slate-800/80 hover:border-slate-700 text-slate-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <h4 className="text-xs font-semibold line-clamp-2 group-hover:text-indigo-400 transition-colors">
                    {item.topic}
                  </h4>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 transition-colors flex-shrink-0 ml-1 mt-0.5" />
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2">
                  <span>{item.createdAt}</span>
                  <span className="text-indigo-400/80 font-mono">{item.pricing?.recommended_price ? `${item.pricing.recommended_price.toLocaleString()}đ` : ""}</span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Tech Stack Info Box */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-900/40 space-y-2">
          <p className="text-[10px] uppercase tracking-wider font-bold text-slate-500">
            Hạ Tầng AI & Multi-Agent
          </p>
          <div className="grid grid-cols-2 gap-1.5 text-[10px] text-slate-400">
            <span className="flex items-center space-x-1 bg-slate-900 px-2 py-1 rounded border border-slate-800">
              <Cpu className="w-3 h-3 text-indigo-400" />
              <span>Gemini 2.0 Flash</span>
            </span>
            <span className="flex items-center space-x-1 bg-slate-900 px-2 py-1 rounded border border-slate-800">
              <Layers className="w-3 h-3 text-purple-400" />
              <span>CrewAI Framework</span>
            </span>
            <span className="flex items-center space-x-1 bg-slate-900 px-2 py-1 rounded border border-slate-800">
              <Network className="w-3 h-3 text-emerald-400" />
              <span>LlamaIndex Graph</span>
            </span>
            <span className="flex items-center space-x-1 bg-slate-900 px-2 py-1 rounded border border-slate-800">
              <Database className="w-3 h-3 text-amber-400" />
              <span>ChromaDB Vector</span>
            </span>
          </div>
        </div>

        {/* Footer Actions */}
        {history.length > 0 && (
          <div className="p-3 border-t border-slate-800 bg-slate-950">
            <button
              onClick={onClearHistory}
              className="w-full flex items-center justify-center space-x-2 py-2 px-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 rounded-xl text-xs font-semibold transition-all cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Xóa toàn bộ lịch sử</span>
            </button>
          </div>
        )}
      </aside>
    </div>
  );
};
