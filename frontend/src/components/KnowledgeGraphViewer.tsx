"use client";

import React, { useState } from "react";
import { KnowledgeGraphData, GraphNode } from "@/types/report";
import { Network } from "lucide-react";

const CATEGORY_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  product: { bg: "#6366f1", border: "#818cf8", text: "#ffffff" },
  competitor: { bg: "#ec4899", border: "#f472b6", text: "#ffffff" },
  segment: { bg: "#10b981", border: "#34d399", text: "#ffffff" },
  price: { bg: "#f59e0b", border: "#fbbf24", text: "#000000" },
  risk: { bg: "#ef4444", border: "#f87171", text: "#ffffff" },
  keyword: { bg: "#8b5cf6", border: "#a78bfa", text: "#ffffff" },
};

export const KnowledgeGraphViewer: React.FC<{ data: KnowledgeGraphData }> = ({ data }) => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 text-xs">
        Chưa có dữ liệu đồ thị tri thức cho báo cáo này.
      </div>
    );
  }

  // Calculate layout coordinates in a circular/force layout
  const width = 700;
  const height = 420;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = 150;

  const nodePositions = data.nodes.map((node, index) => {
    if (node.category === "product" || index === 0) {
      return { ...node, x: centerX, y: centerY };
    }
    const angle = ((index - 1) / (data.nodes.length - 1)) * 2 * Math.PI;
    const distance = radius + (index % 2 === 0 ? 30 : -20);
    return {
      ...node,
      x: centerX + distance * Math.cos(angle),
      y: centerY + distance * Math.sin(angle),
    };
  });

  const nodeMap = new Map(nodePositions.map((n) => [n.id, n]));

  return (
    <div className="space-y-4">
      {/* Legend & Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-800/40 p-4 rounded-2xl border border-slate-700/50">
        <div className="flex items-center space-x-2">
          <Network className="w-4 h-4 text-indigo-400" />
          <h4 className="text-xs sm:text-sm font-bold text-slate-200">
            Mạng Lưới Thực Thể & Quan Hệ Đa Chiều (GraphRAG Triples)
          </h4>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-[10px]">
          {Object.entries(CATEGORY_COLORS).map(([cat, colors]) => (
            <span
              key={cat}
              className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800"
            >
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: colors.bg }} />
              <span className="capitalize text-slate-300">{cat}</span>
            </span>
          ))}
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative bg-slate-950 border border-slate-800 rounded-3xl p-4 overflow-hidden flex items-center justify-center min-h-[440px]">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-full max-h-[440px] select-none"
        >
          {/* Background Grid Accent */}
          <defs>
            <radialGradient id="graph-glow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
            </radialGradient>
          </defs>
          <circle cx={centerX} cy={centerY} r="200" fill="url(#graph-glow)" />

          {/* Links */}
          {data.links.map((link, idx) => {
            const sourceNode = nodeMap.get(link.source);
            const targetNode = nodeMap.get(link.target);
            if (!sourceNode || !targetNode) return null;

            const midX = (sourceNode.x + targetNode.x) / 2;
            const midY = (sourceNode.y + targetNode.y) / 2;

            return (
              <g key={`link-${idx}`}>
                <line
                  x1={sourceNode.x}
                  y1={sourceNode.y}
                  x2={targetNode.x}
                  y2={targetNode.y}
                  stroke="#334155"
                  strokeWidth="1.5"
                  strokeDasharray="4 2"
                />
                <rect
                  x={midX - 35}
                  y={midY - 8}
                  width="70"
                  height="16"
                  rx="4"
                  fill="#090d16"
                  stroke="#1e293b"
                  strokeWidth="0.5"
                />
                <text
                  x={midX}
                  y={midY + 3.5}
                  textAnchor="middle"
                  fill="#94a3b8"
                  fontSize="8"
                  fontWeight="600"
                  className="pointer-events-none uppercase tracking-wider"
                >
                  {link.relationship}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {nodePositions.map((node) => {
            const colors = CATEGORY_COLORS[node.category] || {
              bg: "#6366f1",
              border: "#818cf8",
              text: "#fff",
            };
            const isSelected = selectedNode?.id === node.id;
            const size = node.size || 16;

            return (
              <g
                key={node.id}
                onClick={() => setSelectedNode(node)}
                className="cursor-pointer transition-transform duration-200 hover:scale-110"
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={size + 6}
                  fill={colors.bg}
                  fillOpacity="0.2"
                  className={isSelected ? "animate-ping" : ""}
                />
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={size}
                  fill={colors.bg}
                  stroke={isSelected ? "#ffffff" : colors.border}
                  strokeWidth={isSelected ? "3" : "1.5"}
                />
                <text
                  x={node.x}
                  y={node.y + size + 14}
                  textAnchor="middle"
                  fill={isSelected ? "#ffffff" : "#cbd5e1"}
                  fontSize="10"
                  fontWeight="700"
                  className="pointer-events-none drop-shadow"
                >
                  {node.name}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected Node Details Floating Card */}
        {selectedNode && (
          <div className="absolute bottom-4 right-4 bg-slate-900/95 border border-indigo-500/40 backdrop-blur-md p-3.5 rounded-2xl max-w-xs text-xs space-y-1.5 shadow-2xl animate-fade-in">
            <div className="flex items-center justify-between">
              <span className="font-bold text-indigo-300">{selectedNode.name}</span>
              <span
                className="text-[9px] px-2 py-0.5 rounded-full font-bold uppercase"
                style={{
                  backgroundColor: `${CATEGORY_COLORS[selectedNode.category]?.bg}33`,
                  color: CATEGORY_COLORS[selectedNode.category]?.border,
                }}
              >
                {selectedNode.category}
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Thực thể được trích xuất tự động qua LlamaIndex Property Graph Schema.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
