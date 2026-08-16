"use client";

import React, { useState } from "react";
import { MarketReport } from "@/types/report";
import { PriceChart } from "./PriceChart";
import { KnowledgeGraphViewer } from "./KnowledgeGraphViewer";
import {
  TrendingUp,
  Users,
  DollarSign,
  ShieldAlert,
  Search,
  Network,
  Calendar,
  Download,
  Copy,
  Printer,
  Check,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Target,
  Share2,
  ExternalLink,
} from "lucide-react";

interface ReportDashboardProps {
  report: MarketReport;
}

export const ReportDashboard: React.FC<ReportDashboardProps> = ({ report }) => {
  const [activeTab, setActiveTab] = useState<
    "overview" | "competitors" | "pricing" | "risks" | "seo" | "graph" | "gtm"
  >("overview");
  const [copied, setCopied] = useState(false);
  const [competitorFilter, setCompetitorFilter] = useState<"all" | "Trực tiếp" | "Gián tiếp">("all");
  const [riskFilter, setRiskFilter] = useState<string>("all");

  const handleCopyMarkdown = () => {
    const md = `
# BÁO CÁO PHÂN TÍCH THỊ TRƯỜNG: ${report.topic}
*Ngày lập: ${report.createdAt} | Quy mô: ${report.market_size_est} | Tăng trưởng: ${report.growth_rate}*

## 1. TÓM TẮT THỊ TRƯỜNG
${report.executive_summary}

## 2. ĐỐI THỦ CẠNH TRANH
${report.competitors
  .map(
    (c) => `### ${c.name} (${c.type})
- Định vị: ${c.positioning}
- Khoảng giá: ${c.price_range}
- Điểm mạnh: ${c.strengths.join(", ")}
- Điểm yếu: ${c.weaknesses.join(", ")}`
  )
  .join("\n\n")}

## 3. CHIẾN LƯỢC ĐỊNH GIÁ
- Giá tối thiểu: ${report.pricing.min_market_price.toLocaleString()} VNĐ
- Giá trung vị: ${report.pricing.median_market_price.toLocaleString()} VNĐ
- Giá đề xuất: ${report.pricing.recommended_price.toLocaleString()} VNĐ
- Giá cao cấp: ${report.pricing.premium_market_price.toLocaleString()} VNĐ
- Lý do định giá: ${report.pricing.pricing_logic}

## 4. QUẢN TRỊ RỦI RO
${report.risks.map((r) => `- [${r.risk_level}] ${r.risk_title}: ${r.mitigation}`).join("\n")}

## 5. TỪ KHÓA SEO TIỀM NĂNG
${report.seo_strategy.map((s) => `- ${s.keyword} (${s.intent} - Volume: ${s.search_volume_est})`).join("\n")}
    `.trim();

    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `market-report-${report.topic.toLowerCase().replace(/\s+/g, "-")}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handlePrint = () => {
    window.print();
  };

  const filteredCompetitors = report.competitors.filter((c) =>
    competitorFilter === "all" ? true : c.type === competitorFilter
  );

  const filteredRisks = report.risks.filter((r) =>
    riskFilter === "all" ? true : r.category === riskFilter || r.risk_level === riskFilter
  );

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Executive Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 backdrop-blur-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full text-xs font-semibold uppercase tracking-wider">
                Báo Cáo Hoàn Chỉnh &bull; GraphRAG AI
              </span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                {report.createdAt}
              </span>
            </div>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-slate-100 tracking-tight">
              {report.topic}
            </h2>
          </div>

          {/* Action Export Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleCopyMarkdown}
              className="flex items-center space-x-1.5 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition-all cursor-pointer"
              title="Sao chép toàn bộ báo cáo dạng Markdown"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Đã sao chép MD!" : "Copy Markdown"}</span>
            </button>
            <button
              onClick={handleDownloadJSON}
              className="flex items-center space-x-1.5 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition-all cursor-pointer"
              title="Tải file JSON dữ liệu"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Tải JSON</span>
            </button>
            <button
              onClick={handlePrint}
              className="flex items-center space-x-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all cursor-pointer"
              title="In hoặc Xuất PDF"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>In / PDF</span>
            </button>
          </div>
        </div>

        {/* Quick Highlights Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
            <span className="text-[11px] text-slate-400 block">Quy mô thị trường ước tính</span>
            <p className="text-sm sm:text-base font-bold text-indigo-300 mt-1">
              {report.market_size_est || "Đang tăng trưởng"}
            </p>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
            <span className="text-[11px] text-slate-400 block">Tốc độ tăng trưởng hàng năm</span>
            <p className="text-sm sm:text-base font-bold text-emerald-400 mt-1">
              {report.growth_rate || "18% CAGR"}
            </p>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
            <span className="text-[11px] text-slate-400 block">Số đối thủ đã bóc tách</span>
            <p className="text-sm sm:text-base font-bold text-purple-300 mt-1">
              {report.competitors.length} thương hiệu
            </p>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
            <span className="text-[11px] text-slate-400 block">Khoảng giá ngọt (Sweet Spot)</span>
            <p className="text-sm sm:text-base font-bold text-amber-300 mt-1">
              {report.pricing?.recommended_price ? `${report.pricing.recommended_price.toLocaleString()} đ` : "Tùy biến"}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 custom-scrollbar">
        {[
          { id: "overview", label: "Tổng quan & Khách hàng", icon: TrendingUp },
          { id: "competitors", label: "Đối thủ & SWOT", icon: Users, count: report.competitors.length },
          { id: "pricing", label: "Chiến lược Định giá", icon: DollarSign },
          { id: "risks", label: "Quản trị Rủi ro", icon: ShieldAlert, count: report.risks.length },
          { id: "seo", label: "SEO & Từ khóa", icon: Search, count: report.seo_strategy.length },
          { id: "graph", label: "Đồ thị Tri thức (GraphRAG)", icon: Network },
          { id: "gtm", label: "Lộ trình Go-To-Market", icon: Target },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-2xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
                isActive
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 scale-100"
                  : "bg-slate-900/90 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] ${
                    isActive ? "bg-white/20 text-white" : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Executive Summary */}
          <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl space-y-3 shadow-xl">
            <div className="flex items-center space-x-2 text-indigo-400 font-bold text-sm">
              <Flame className="w-4 h-4 text-amber-400" />
              <span>Tóm Tắt Tổng Quan Thị Trường (Executive Summary)</span>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              {report.executive_summary}
            </p>
          </div>

          {/* Target Audience Personas */}
          <div className="space-y-3">
            <h3 className="text-xs uppercase tracking-wider font-bold text-slate-400">
              Chân Dung Khách Hàng Mục Tiêu (Target Personas)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {report.target_audience.map((aud, i) => (
                <div
                  key={i}
                  className="bg-slate-900/80 border border-slate-800 p-5 rounded-3xl space-y-3 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <span className="w-7 h-7 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center font-bold text-xs">
                      0{i + 1}
                    </span>
                    <h4 className="font-bold text-sm text-slate-100">{aud.title}</h4>
                    <p className="text-xs text-slate-400 leading-relaxed">{aud.desc}</p>
                  </div>
                  <div className="space-y-1.5 pt-3 border-t border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-rose-400 block">
                      Nỗi đau chính (Pain Points):
                    </span>
                    {aud.pain_points.map((p, pIdx) => (
                      <div key={pIdx} className="flex items-start space-x-1.5 text-xs text-slate-300">
                        <span className="text-rose-400 font-bold">&bull;</span>
                        <span>{p}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Market Gaps & Opportunities */}
          <div className="space-y-3">
            <h3 className="text-xs uppercase tracking-wider font-bold text-slate-400">
              Khoảng Trống Thị Trường & Cơ Hội Chưa Khai Thác (Market Gaps)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {report.market_gaps.map((gap, i) => (
                <div
                  key={i}
                  className="bg-slate-900/80 border border-slate-800 p-5 rounded-3xl space-y-2 flex items-start space-x-3"
                >
                  <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 flex-shrink-0 mt-1">
                    <Target className="w-4 h-4" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-bold text-sm text-slate-100">{gap.title}</h4>
                      <span
                        className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase ${
                          gap.priority === "Cao"
                            ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                            : "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30"
                        }`}
                      >
                        Ưu tiên {gap.priority}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{gap.opportunity}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* SWOT Matrix */}
          {report.swot && (
            <div className="space-y-3">
              <h3 className="text-xs uppercase tracking-wider font-bold text-slate-400">
                Ma Trận SWOT Thị Trường Toàn Diện
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-slate-900/80 border border-emerald-900/40 p-5 rounded-3xl space-y-2.5">
                  <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Điểm Mạnh (Strengths)</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {report.swot.strengths.map((s, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-emerald-400 font-bold">&check;</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-900/80 border border-rose-900/40 p-5 rounded-3xl space-y-2.5">
                  <div className="flex items-center space-x-2 text-rose-400 font-bold text-xs uppercase tracking-wider">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Điểm Yếu (Weaknesses)</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {report.swot.weaknesses.map((w, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-rose-400 font-bold">&times;</span>
                        <span>{w}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-900/80 border border-indigo-900/40 p-5 rounded-3xl space-y-2.5">
                  <div className="flex items-center space-x-2 text-indigo-400 font-bold text-xs uppercase tracking-wider">
                    <Flame className="w-4 h-4" />
                    <span>Cơ Hội (Opportunities)</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {report.swot.opportunities.map((o, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-indigo-400 font-bold">&#8593;</span>
                        <span>{o}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-900/80 border border-amber-900/40 p-5 rounded-3xl space-y-2.5">
                  <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
                    <ShieldAlert className="w-4 h-4" />
                    <span>Thách Thức (Threats)</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {report.swot.threats.map((t, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-amber-400 font-bold">&#33;</span>
                        <span>{t}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: COMPETITORS */}
      {activeTab === "competitors" && (
        <div className="space-y-4">
          {/* Filter Pills */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-medium">Lọc:</span>
            {["all", "Trực tiếp", "Gián tiếp"].map((type) => (
              <button
                key={type}
                onClick={() => setCompetitorFilter(type as any)}
                className={`px-3 py-1 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  competitorFilter === type
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                {type === "all" ? "Tất cả đối thủ" : `Đối thủ ${type}`}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredCompetitors.map((comp, idx) => (
              <div
                key={idx}
                className="bg-slate-900/80 border border-slate-800 p-6 rounded-3xl space-y-4 shadow-xl flex flex-col justify-between hover:border-indigo-500/40 transition-colors"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="font-extrabold text-base text-slate-100">{comp.name}</h4>
                        <span
                          className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase ${
                            comp.type === "Trực tiếp"
                              ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                              : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                          }`}
                        >
                          {comp.type}
                        </span>
                      </div>
                      <p className="text-xs text-indigo-300/90 font-medium mt-0.5">
                        {comp.positioning}
                      </p>
                    </div>
                    <span className="text-xs bg-slate-800 text-slate-300 font-mono px-2.5 py-1 rounded-xl border border-slate-700">
                      {comp.price_range}
                    </span>
                  </div>

                  {comp.market_share_est && (
                    <p className="text-[11px] text-slate-400">
                      Ước lượng thị phần ngách:{" "}
                      <b className="text-emerald-400">{comp.market_share_est}</b>
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-slate-800">
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-emerald-400">
                      Điểm mạnh nổi trội:
                    </span>
                    <ul className="space-y-1 text-xs text-slate-300">
                      {comp.strengths.map((s, sIdx) => (
                        <li key={sIdx} className="flex items-start space-x-1.5">
                          <span className="text-emerald-400">&bull;</span>
                          <span>{s}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-rose-400">
                      Điểm yếu / Lỗ hổng:
                    </span>
                    <ul className="space-y-1 text-xs text-slate-300">
                      {comp.weaknesses.map((w, wIdx) => (
                        <li key={wIdx} className="flex items-start space-x-1.5">
                          <span className="text-rose-400">&bull;</span>
                          <span>{w}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {comp.website && (
                  <a
                    href={comp.website}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors pt-1"
                  >
                    <span>Xem website chính thức</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: PRICING */}
      {activeTab === "pricing" && (
        <div className="space-y-6">
          <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl space-y-2">
            <h4 className="text-xs uppercase tracking-wider font-bold text-indigo-400">
              Cơ Sở & Lý Luận Chiến Lược Định Giá (Pricing Rationale)
            </h4>
            <p className="text-sm text-slate-300 leading-relaxed">
              {report.pricing.pricing_logic}
            </p>
          </div>

          <PriceChart pricing={report.pricing} />
        </div>
      )}

      {/* TAB 4: RISKS */}
      {activeTab === "risks" && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2 overflow-x-auto pb-1">
            <span className="text-xs text-slate-400 font-medium">Lọc theo:</span>
            {["all", "Cao", "Trung bình", "Pháp lý", "Vận hành", "Đối thủ", "Tài chính"].map((cat) => (
              <button
                key={cat}
                onClick={() => setRiskFilter(cat)}
                className={`px-3 py-1 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                  riskFilter === cat
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                {cat === "all" ? "Tất cả rủi ro" : cat}
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {filteredRisks.map((risk, idx) => (
              <div
                key={idx}
                className="bg-slate-900/90 border border-slate-800 p-5 rounded-3xl space-y-3 shadow-md hover:border-slate-700 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`text-[9px] px-2.5 py-0.5 rounded-full font-bold uppercase ${
                        risk.risk_level === "Cao"
                          ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                      }`}
                    >
                      Rủi ro {risk.risk_level}
                    </span>
                    <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-lg border border-slate-700">
                      Danh mục: {risk.category}
                    </span>
                    <h4 className="text-sm font-bold text-slate-100">{risk.risk_title}</h4>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
                  <div className="bg-slate-950/60 p-3 rounded-2xl border border-slate-800/80">
                    <span className="text-rose-400 font-bold block mb-1">Mức độ tác động (Impact):</span>
                    <p className="text-slate-300">{risk.impact}</p>
                  </div>
                  <div className="bg-indigo-950/30 p-3 rounded-2xl border border-indigo-900/30">
                    <span className="text-indigo-300 font-bold block mb-1">
                      Kế hoạch giảm thiểu (Mitigation Strategy):
                    </span>
                    <p className="text-slate-300">{risk.mitigation}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: SEO */}
      {activeTab === "seo" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {report.seo_strategy.map((seo, idx) => (
              <div
                key={idx}
                className="bg-slate-900/80 border border-slate-800 p-5 rounded-3xl space-y-3 flex flex-col justify-between hover:border-indigo-500/40 transition-colors"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-bold text-sm text-indigo-300 leading-snug">{seo.keyword}</h4>
                    <span
                      className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase flex-shrink-0 ${
                        seo.intent.includes("Commercial") || seo.intent.includes("Mua hàng")
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30"
                      }`}
                    >
                      {seo.intent}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                    <span>
                      Volume: <b className="text-slate-200">{seo.search_volume_est}</b>
                    </span>
                    <span>
                      Độ cạnh tranh: <b className="text-slate-200">{seo.competition}</b>
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-slate-950 rounded-2xl border border-slate-800/80 text-xs">
                  <span className="text-[10px] text-slate-500 font-bold uppercase block mb-0.5">
                    Gợi ý bài viết / Content Angle:
                  </span>
                  <p className="text-slate-300 italic">{seo.content_angle}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 6: KNOWLEDGE GRAPH */}
      {activeTab === "graph" && <KnowledgeGraphViewer data={report.graph_data} />}

      {/* TAB 7: GTM ROADMAP */}
      {activeTab === "gtm" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {report.gtm_roadmap.map((phase, idx) => (
              <div
                key={idx}
                className="bg-slate-900/80 border border-slate-800 p-6 rounded-3xl space-y-4 relative overflow-hidden"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2 text-indigo-400 text-xs font-bold">
                    <span className="w-5 h-5 rounded-full bg-indigo-600/30 flex items-center justify-center text-[10px]">
                      {idx + 1}
                    </span>
                    <span>{phase.timeline}</span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-100">{phase.phase}</h4>
                </div>

                <div className="space-y-2 pt-2 border-t border-slate-800 text-xs text-slate-300">
                  {phase.key_actions.map((act, aIdx) => (
                    <div key={aIdx} className="flex items-start space-x-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span>{act}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
