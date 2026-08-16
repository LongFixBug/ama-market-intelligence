import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AMA Market Intelligence - Nền Tảng Phân Tích Thị Trường & GraphRAG",
  description: "Báo cáo phân tích thị trường, chiến lược giá và nghiên cứu từ khóa SEO tự động ứng dụng Multi-Agent + GraphRAG.",
  keywords: ["Nghiên cứu thị trường", "Multi-Agent", "GraphRAG", "LlamaIndex", "Gemini 2.0 Flash", "Định giá thị trường"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="vi"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}
