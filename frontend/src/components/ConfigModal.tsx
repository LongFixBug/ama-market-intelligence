"use client";

import React, { useState } from "react";
import { X, Server, Check, AlertCircle, RefreshCw } from "lucide-react";

interface ConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  backendUrl: string;
  onSaveBackendUrl: (url: string) => void;
  isMockMode: boolean;
  onToggleMockMode: (val: boolean) => void;
}

export const ConfigModal: React.FC<ConfigModalProps> = ({
  isOpen,
  onClose,
  backendUrl,
  onSaveBackendUrl,
  isMockMode,
  onToggleMockMode,
}) => {
  const [url, setUrl] = useState(backendUrl);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<"success" | "error" | null>(null);

  if (!isOpen) return null;

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch(`${url}/docs`, { method: "GET", mode: "no-cors" });
      setTestResult("success");
    } catch (e) {
      setTestResult("error");
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    onSaveBackendUrl(url.trim().replace(/\/$/, ""));
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/70 backdrop-blur-xs" onClick={onClose} />

      {/* Modal Box */}
      <div className="relative bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-md p-6 shadow-2xl space-y-6 z-10 text-white">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Server className="w-5 h-5 text-indigo-400" />
            <h3 className="font-bold text-base text-slate-100">Cấu Hình Kết Nối Backend</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Mode Toggle Switch */}
        <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-200">Chế độ Demo / Mock Mode</span>
              <p className="text-[11px] text-slate-400">
                Cho phép test giao diện ngay mà không cần chạy server backend.
              </p>
            </div>
            <button
              onClick={() => onToggleMockMode(!isMockMode)}
              className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors cursor-pointer ${
                isMockMode ? "bg-indigo-600 justify-end" : "bg-slate-800 justify-start"
              }`}
            >
              <span className="bg-white w-4 h-4 rounded-full shadow-md transform transition-transform" />
            </button>
          </div>
        </div>

        {/* Backend API Endpoint Input */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-300">
            FastAPI Backend Endpoint URL
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="http://localhost:8000"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
            />
            <button
              onClick={handleTestConnection}
              disabled={testing}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center space-x-1 flex-shrink-0 transition-colors"
            >
              {testing ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <span>Test</span>
              )}
            </button>
          </div>

          {testResult === "success" && (
            <p className="text-[11px] text-emerald-400 flex items-center gap-1">
              <Check className="w-3 h-3" /> Kết nối tới Backend thành công!
            </p>
          )}
          {testResult === "error" && (
            <p className="text-[11px] text-rose-400 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" /> Không thể kết nối tới Backend URL này.
            </p>
          )}
        </div>

        {/* Modal Actions */}
        <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-colors"
          >
            Đóng
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors shadow-md shadow-indigo-600/30"
          >
            Lưu cài đặt
          </button>
        </div>
      </div>
    </div>
  );
};
