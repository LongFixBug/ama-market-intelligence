"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  CartesianGrid,
} from "recharts";
import { PricingStrategy } from "@/types/report";
import { DollarSign, TrendingUp, CheckCircle2 } from "lucide-react";

export const PriceChart: React.FC<{ pricing: PricingStrategy }> = ({ pricing }) => {
  const minPrice = pricing.min_market_price ?? 0;
  const medianPrice = pricing.median_market_price ?? 0;
  const recPrice = pricing.recommended_price ?? 0;
  const premiumPrice = pricing.premium_market_price ?? 0;

  const chartData = [
    {
      name: "Tối thiểu",
      price: minPrice,
      color: "#64748b",
      label: "Giá thấp nhất",
    },
    {
      name: "Trung vị",
      price: medianPrice,
      color: "#94a3b8",
      label: "Trung bình ngành",
    },
    {
      name: "Khuyến nghị",
      price: recPrice,
      color: "#6366f1",
      label: "Điểm ngọt (Sweet Spot)",
    },
    {
      name: "Cao cấp",
      price: premiumPrice,
      color: "#f59e0b",
      label: "Phân khúc Premium",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Metric Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-800/40 border border-slate-700/50 p-4 rounded-2xl">
          <span className="text-[11px] text-slate-400 block">Thấp nhất thị trường</span>
          <p className="text-base sm:text-lg font-bold text-slate-200 mt-1">
            {minPrice.toLocaleString()} đ
          </p>
        </div>
        <div className="bg-slate-800/40 border border-slate-700/50 p-4 rounded-2xl">
          <span className="text-[11px] text-slate-400 block">Trung vị ngành</span>
          <p className="text-base sm:text-lg font-bold text-slate-200 mt-1">
            {medianPrice.toLocaleString()} đ
          </p>
        </div>
        <div className="bg-indigo-950/40 border border-indigo-500/50 p-4 rounded-2xl ring-1 ring-indigo-500/30">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-indigo-300 font-semibold block">Giá đề xuất</span>
            <span className="text-[9px] bg-indigo-500/30 text-indigo-300 px-1.5 py-0.5 rounded font-bold">
              Tối ưu
            </span>
          </div>
          <p className="text-base sm:text-lg font-extrabold text-indigo-300 mt-1">
            {recPrice.toLocaleString()} đ
          </p>
        </div>
        <div className="bg-slate-800/40 border border-slate-700/50 p-4 rounded-2xl">
          <span className="text-[11px] text-slate-400 block">Biên lợi nhuận gộp</span>
          <p className="text-base sm:text-lg font-bold text-emerald-400 mt-1">
            {pricing.margin_est || "60% - 70%"}
          </p>
        </div>
      </div>

      {/* Interactive Bar Chart */}
      <div className="bg-slate-800/30 border border-slate-700/40 rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs sm:text-sm font-bold text-slate-200">
              Phân Phối & So Sánh Mức Giá Thị Trường ({pricing.unit || "VNĐ"})
            </h4>
          </div>
        </div>

        <div className="h-64 sm:h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 20, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickFormatter={(v) => `${(v / 1000).toLocaleString()}k`}
                tickLine={false}
              />
              <Tooltip
                formatter={(value: any, name: any, item: any) => [
                  `${Number(value).toLocaleString()} đ`,
                  item.payload.label,
                ]}
                contentStyle={{
                  backgroundColor: "#090d16",
                  borderColor: "#334155",
                  borderRadius: "12px",
                  color: "#f8fafc",
                  fontSize: "12px",
                  boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.5)",
                }}
              />
              <Bar dataKey="price" radius={[8, 8, 0, 0]} maxBarSize={60}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.color}
                    className="transition-all duration-300 hover:opacity-80 cursor-pointer"
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pricing Tiers Packaging */}
      {pricing.tiers && pricing.tiers.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs uppercase tracking-wider font-bold text-slate-400">
            Gói Sản Phẩm & Mô Hình Đóng Gói Khuyến Nghị
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {pricing.tiers.map((tier, idx) => (
              <div
                key={idx}
                className={`p-5 rounded-2xl border flex flex-col justify-between space-y-4 transition-all ${
                  idx === 1
                    ? "bg-indigo-950/30 border-indigo-500/60 ring-1 ring-indigo-500/40 relative shadow-lg shadow-indigo-950/40"
                    : "bg-slate-800/40 border-slate-700/50"
                }`}
              >
                {idx === 1 && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-[10px] uppercase font-extrabold px-3 py-0.5 rounded-full shadow-sm">
                    Khuyên Dùng Nhất
                  </div>
                )}
                <div className="space-y-2">
                  <div className="flex justify-between items-start">
                    <h5 className="font-bold text-sm text-slate-100">{tier.tier}</h5>
                  </div>
                  <p className="text-xl font-extrabold text-indigo-300 font-mono">
                    {tier.price.toLocaleString()} đ
                  </p>
                  <p className="text-xs text-slate-400">{tier.description}</p>
                </div>

                <div className="space-y-2 pt-2 border-t border-slate-700/60">
                  {tier.features.map((feat, fIdx) => (
                    <div key={fIdx} className="flex items-start space-x-2 text-xs text-slate-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span>{feat}</span>
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
