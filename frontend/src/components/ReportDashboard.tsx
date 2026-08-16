"use client";

import React, { useState } from "react";
import { MarketReport } from "@/types/report";
import {
  BarChart3,
  Share2,
  Copy,
  Download,
  Check,
  Target,
  TrendingUp,
  DollarSign,
  Info,
  ShieldCheck,
  AlertTriangle,
  Search,
  Bot,
} from "lucide-react";

interface ReportDashboardProps {
  report: MarketReport;
}

export const ReportDashboard: React.FC<ReportDashboardProps> = ({ report }) => {
  const [copiedMd, setCopiedMd] = useState(false);
  const [copiedKeywords, setCopiedKeywords] = useState(false);
  const [copiedPromptIndex, setCopiedPromptIndex] = useState<number | null>(null);

  const handleCopyMarkdown = () => {
    const md = `
# BÁO CÁO PHÂN TÍCH CHIẾN LƯỢC: ${report.topic}

## 1. PHÂN TÍCH NGÁCH THỊ TRƯỜNG
${report.niche_analysis.summary}
*Tiềm năng tăng trưởng: ${report.niche_analysis.growth_potential}*

## 2. CHIẾN LƯỢC ĐỊNH GIÁ
- Khoảng giá tối ưu: ${report.pricing.price_range}
- Cơ sở & Cơ chế định giá: ${report.pricing.rationale}
- Luận điểm: ${report.pricing.tagline}

## 3. RỦI RO & THÁCH THỨC KINH DOANH
${report.risks.map((r, i) => `${i + 1}. ${r.title}`).join("\n")}

## 4. TỪ KHÓA SEO & QUẢNG CÁO
${report.seo_keywords.map((k) => `# ${k}`).join("\n")}

## 5. CÂU LỆNH AI ĐỀ XUẤT (PROMPTS)
${report.ai_prompts.map((p, i) => `${i + 1}. ${p.prompt}`).join("\n")}
    `.trim();

    navigator.clipboard.writeText(md);
    setCopiedMd(true);
    setTimeout(() => setCopiedMd(false), 2000);
  };

  const handleDownloadJSON = () => {
    const dataStr =
      "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute(
      "download",
      `market-analysis-${report.topic.toLowerCase().replace(/\s+/g, "-")}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleCopyKeywords = () => {
    navigator.clipboard.writeText(report.seo_keywords.map((k) => `# ${k}`).join(", "));
    setCopiedKeywords(true);
    setTimeout(() => setCopiedKeywords(false), 2000);
  };

  const handleCopyPrompt = (promptText: string, index: number) => {
    navigator.clipboard.writeText(promptText);
    setCopiedPromptIndex(index);
    setTimeout(() => setCopiedPromptIndex(null), 2000);
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Title Header */}
      <div className="flex items-center space-x-2 text-slate-800 dark:text-slate-100 font-bold text-lg sm:text-xl">
        <BarChart3 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        <span>Báo Cáo Phân Tích Chiến Lược:</span>
        <span className="text-indigo-600 dark:text-indigo-400">{report.topic}</span>
      </div>

      {/* Export Action Bar */}
      <div className="bg-white/80 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-3.5 flex flex-wrap items-center justify-between gap-3 shadow-xs">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-700 dark:text-slate-300">
          <Share2 className="w-4 h-4 text-indigo-500" />
          <span>Xuất dữ liệu báo cáo phân tích</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopyMarkdown}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold transition-all cursor-pointer border border-slate-200 dark:border-slate-700"
          >
            {copiedMd ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedMd ? "Đã sao chép!" : "Sao chép Markdown"}</span>
          </button>
          <button
            onClick={handleDownloadJSON}
            className="flex items-center space-x-1.5 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all shadow-md shadow-indigo-500/20 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Tải xuống JSON</span>
          </button>
        </div>
      </div>

      {/* CARD 1: Phân Tích Ngách Thị Trường */}
      <div className="bg-white/90 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xs space-y-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 flex-shrink-0">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-slate-100">
                Phân Tích Ngách Thị Trường
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Đánh giá tiềm năng và cơ hội tăng trưởng
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              navigator.clipboard.writeText(report.niche_analysis.summary);
            }}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1.5 rounded-lg transition-colors"
            title="Sao chép phần này"
          >
            <Copy className="w-4 h-4" />
          </button>
        </div>

        <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed pt-1">
          {report.niche_analysis.summary}
        </p>

        <div className="pt-2 flex items-center space-x-2 text-xs font-semibold text-indigo-600 dark:text-indigo-400">
          <TrendingUp className="w-3.5 h-3.5" />
          <span>Tiềm năng tăng trưởng: {report.niche_analysis.growth_potential}</span>
        </div>
      </div>

      {/* ROW 2: Định Giá (Trái) & Rủi Ro (Phải) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* CARD 2: Chiến Lược Định Giá */}
        <div className="bg-white/90 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xs space-y-4 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 flex-shrink-0">
                <DollarSign className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-slate-100">
                  Chiến Lược Định Giá
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Mức giá đề xuất và luận điểm kinh doanh
                </p>
              </div>
            </div>

            {/* Khoảng giá tối ưu Badge */}
            <div className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-3.5 flex items-center justify-between">
              <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">
                Khoảng giá tối ưu:
              </span>
              <span className="px-3.5 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 font-extrabold text-xs sm:text-sm font-mono border border-indigo-200 dark:border-indigo-500/30">
                {report.pricing.price_range}
              </span>
            </div>

            {/* Cơ sở định giá */}
            <div className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-4 space-y-1.5">
              <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-800 dark:text-slate-200">
                <Info className="w-3.5 h-3.5 text-indigo-500" />
                <span>Cơ sở & Cơ chế định giá:</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                {report.pricing.rationale}
              </p>
            </div>
          </div>

          <div className="pt-2 flex items-center space-x-2 text-xs font-semibold text-indigo-600 dark:text-indigo-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{report.pricing.tagline}</span>
          </div>
        </div>

        {/* CARD 3: Rủi Ro & Thách Thức Kinh Doanh */}
        <div className="bg-white/90 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xs space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 flex items-center justify-center text-amber-600 dark:text-amber-400 flex-shrink-0">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-slate-100">
                Rủi Ro & Thách Thức Kinh Doanh
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Các yếu tố rủi ro chính cần kiểm soát
              </p>
            </div>
          </div>

          {/* Risk Items */}
          <div className="space-y-3 pt-1">
            {report.risks.map((risk, idx) => (
              <div
                key={idx}
                className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-3.5 flex items-start justify-between gap-3"
              >
                <div className="flex items-start space-x-2.5">
                  <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                    {risk.title}
                  </p>
                </div>
                <span className="px-2 py-0.5 rounded-md bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 text-amber-600 dark:text-amber-400 text-[10px] font-extrabold uppercase whitespace-nowrap flex-shrink-0">
                  CẦN LƯU Ý #{risk.index || idx + 1}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CARD 4: Từ Khóa SEO & Quảng Cáo Tiềm Năng (Khung viền cam) */}
      <div className="bg-white/90 dark:bg-slate-900/60 border border-amber-300/80 dark:border-amber-500/40 rounded-3xl p-6 sm:p-7 shadow-xs space-y-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 flex items-center justify-center text-amber-600 dark:text-amber-400 flex-shrink-0">
              <Search className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-slate-100">
                Từ Khóa SEO & Quảng Cáo Tiềm Năng
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Từ khóa độ tìm kiếm tốt cho nội dung & chạy ads
              </p>
            </div>
          </div>
          <button
            onClick={handleCopyKeywords}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30 text-amber-700 dark:text-amber-400 text-xs font-semibold hover:bg-amber-100 dark:hover:bg-amber-500/20 transition-all cursor-pointer"
          >
            {copiedKeywords ? (
              <Check className="w-3.5 h-3.5 text-emerald-500" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
            <span>{copiedKeywords ? "Đã chép!" : "Sao chép danh sách"}</span>
          </button>
        </div>

        {/* Keyword Tags */}
        <div className="flex flex-wrap gap-2 pt-2">
          {report.seo_keywords.map((kw, idx) => (
            <span
              key={idx}
              className="px-3 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-200/80 dark:border-slate-800 text-slate-700 dark:text-slate-300 text-xs font-medium hover:border-amber-400/60 transition-colors"
            >
              <span className="text-amber-500 font-bold mr-1">#</span>
              {kw}
            </span>
          ))}
        </div>
      </div>

      {/* CARD 5: Câu Lệnh AI Đề Xuất (Prompts) */}
      <div className="bg-white/90 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xs space-y-4">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 flex-shrink-0">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-slate-100">
              Câu Lệnh AI Đề Xuất (Prompts)
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Sử dụng trực tiếp cho ChatGPT, Claude hoặc Gemini
            </p>
          </div>
        </div>

        {/* Prompts list with copy button */}
        <div className="space-y-3 pt-1">
          {report.ai_prompts.map((p, idx) => (
            <div
              key={idx}
              className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-4 flex items-start justify-between gap-3 group hover:border-indigo-300 dark:hover:border-slate-700 transition-colors"
            >
              <div className="flex items-start space-x-2">
                <span className="text-indigo-500 font-mono font-bold select-none">&gt;_</span>
                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-mono">
                  {p.prompt}
                </p>
              </div>
              <button
                onClick={() => handleCopyPrompt(p.prompt, idx)}
                className="flex items-center space-x-1 px-3 py-1 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 rounded-lg text-xs font-semibold transition-all cursor-pointer flex-shrink-0 shadow-xs"
              >
                {copiedPromptIndex === idx ? (
                  <Check className="w-3.5 h-3.5 text-emerald-500" />
                ) : (
                  <Copy className="w-3.5 h-3.5 text-slate-400" />
                )}
                <span>{copiedPromptIndex === idx ? "Đã chép!" : "Sao chép"}</span>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
