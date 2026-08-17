"use client";

import React, { useEffect, useRef, useState } from "react";
import { CalendarClock, Check, Globe2, Loader2, Send, ShieldCheck, Sparkles } from "lucide-react";
import { ContentCampaign, ContentDraft, ContentPlatform, MarketReport } from "@/types/report";

interface ContentCampaignPanelProps {
  report: MarketReport;
  backendUrl: string;
  isMockMode: boolean;
}

const PLATFORM_LABELS: Record<ContentPlatform, string> = {
  blog: "SEO Blog",
  x: "X",
  linkedin: "LinkedIn",
  facebook: "Facebook Page",
};

const DEFAULT_PLATFORMS: ContentPlatform[] = ["blog", "x", "linkedin", "facebook"];

type CampaignEvent = Partial<ContentCampaign> & {
  stage?: string;
  campaign?: ContentCampaign;
};

function buildMockDrafts(report: MarketReport, platforms: ContentPlatform[]): ContentDraft[] {
  return platforms.map((platform, index) => ({
    id: `mock-draft-${platform}-${index}`,
    platform,
    title: platform === "blog" ? `${report.topic}: cơ hội và rủi ro` : "",
    body:
      platform === "blog"
        ? `# ${report.topic}\n\n${report.niche_analysis.summary}\n\nKhoảng giá tham khảo: ${report.pricing.price_range}.\n\nTừ khóa SEO: ${report.seo_keywords.join(", ")}.`
        : platform === "x"
        ? `${report.topic}: ${report.niche_analysis.summary.slice(0, 150)} ${report.pricing.price_range}.`
        : platform === "linkedin"
        ? `Một góc nhìn về ${report.topic}:\n\n${report.niche_analysis.summary}\n\nMức giá tham khảo: ${report.pricing.price_range}.`
        : `Đang tìm hiểu ${report.topic}? ${report.niche_analysis.summary} Mức giá tham khảo: ${report.pricing.price_range}.`,
    seo_keywords: report.seo_keywords.slice(0, 5),
    hashtags: report.seo_keywords.slice(0, 3).map((keyword) => `#${keyword.replace(/\s+/g, "")}`),
    content_hash: `mock-${platform}-${index}`,
    status: "draft",
  }));
}

export const ContentCampaignPanel: React.FC<ContentCampaignPanelProps> = ({
  report,
  backendUrl,
  isMockMode,
}) => {
  const [platforms, setPlatforms] = useState<ContentPlatform[]>(DEFAULT_PLATFORMS);
  const [campaign, setCampaign] = useState<ContentCampaign | null>(null);
  const [campaignToken, setCampaignToken] = useState("");
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scheduleAt, setScheduleAt] = useState("");
  const eventSourceRef = useRef<EventSource | null>(null);
  const streamGenerationRef = useRef(0);

  useEffect(() => () => {
    streamGenerationRef.current += 1;
    eventSourceRef.current?.close();
  }, []);

  const togglePlatform = (platform: ContentPlatform) => {
    setPlatforms((current) =>
      current.includes(platform)
        ? current.filter((item) => item !== platform)
        : [...current, platform],
    );
  };

  const applyCampaignEvent = (data: CampaignEvent) => {
    if (data.campaign) {
      setCampaign(data.campaign);
    } else if (data.status) {
      setCampaign((current) => (current ? { ...current, ...data } : current));
    }
  };

  const streamCampaign = async (campaignId: string, token: string, generation: number) => {
    const isCurrent = () => streamGenerationRef.current === generation;
    const terminalStatuses = ["completed", "needs_review", "failed", "cancelled"];
    let streamToken: string | undefined;

    try {
      // Creation is asynchronous: the campaign may not have a snapshot yet
      // when the 202 response reaches the browser. Retry only the bounded
      // not-ready case; all other failures remain visible to the user.
      for (let attempt = 0; attempt < 10 && isCurrent(); attempt += 1) {
        const ticketResponse = await fetch(
          `${backendUrl}/api/content-campaigns/${campaignId}/stream-ticket`,
          { method: "POST", headers: { Authorization: `Bearer ${token}` } },
        );
        if (ticketResponse.ok) {
          const ticketData = (await ticketResponse.json()) as { stream_token?: string };
          streamToken = ticketData.stream_token;
          break;
        }
        if (ticketResponse.status !== 409) throw new Error("Stream ticket rejected");
        await new Promise((resolve) => setTimeout(resolve, 750));
      }
      if (!isCurrent()) return;
      if (!streamToken) throw new Error("Campaign did not become ready in time");

      eventSourceRef.current?.close();
      const source = new EventSource(
        `${backendUrl}/api/content-campaigns/${campaignId}/stream?stream_token=${encodeURIComponent(streamToken)}`,
      );
      eventSourceRef.current = source;
      source.onmessage = (event) => {
        try {
          if (!isCurrent()) return;
          const data = JSON.parse(event.data) as CampaignEvent;
          applyCampaignEvent(data);
          if (data.stage === "waiting_approval" || data.stage === "scheduled") {
            setWorking(false);
          }
          if (terminalStatuses.includes(data.stage ?? "")) {
            source.close();
            setWorking(false);
          }
        } catch {
          setError("Không đọc được trạng thái chiến dịch.");
          source.close();
          setWorking(false);
        }
      };
      source.onerror = () => {
        if (isCurrent() && source.readyState === EventSource.CLOSED) {
          setError("Mất kết nối tới luồng chiến dịch.");
          setWorking(false);
        }
      };

      // SSE is the fast path. Polling the authorized snapshot is a bounded
      // fallback for a connection that lands on a different worker or misses
      // an event during a reload; it never puts the campaign bearer in a URL.
      for (let attempt = 0; attempt < 15 && isCurrent(); attempt += 1) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        const snapshotResponse = await fetch(
          `${backendUrl}/api/content-campaigns/${campaignId}`,
          { headers: { Authorization: `Bearer ${token}` } },
        );
        if (!snapshotResponse.ok) continue;
        const snapshot = (await snapshotResponse.json()) as ContentCampaign;
        if (!isCurrent()) return;
        setCampaign(snapshot);
        if (snapshot.status === "waiting_approval" || snapshot.status === "scheduled") {
          setWorking(false);
          return;
        }
        if (terminalStatuses.includes(snapshot.status)) {
          source.close();
          setWorking(false);
          return;
        }
      }
    } catch {
      if (isCurrent()) {
        setError("Không thể mở luồng trạng thái chiến dịch.");
        setWorking(false);
      }
    }
  };

  const createCampaign = async () => {
    if (!platforms.length || working) return;
    const generation = streamGenerationRef.current + 1;
    streamGenerationRef.current = generation;
    eventSourceRef.current?.close();
    setWorking(true);
    setError(null);
    setCampaign(null);
    setCampaignToken("");
    if (isMockMode) {
      setCampaign({
        id: "mock-campaign",
        report_id: report.id,
        topic: report.topic,
        platforms,
        status: "waiting_approval",
        step: 4,
        claims: [],
        drafts: buildMockDrafts(report, platforms),
        publish_results: [],
        issues: [],
        actions: [],
        revision_count: 0,
        approval_required: true,
        created_at: new Date().toISOString(),
      });
      setCampaignToken("mock-token");
      setWorking(false);
      return;
    }

    try {
      const scheduledAt = scheduleAt ? new Date(scheduleAt).toISOString() : undefined;
      const response = await fetch(`${backendUrl}/api/content-campaigns`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          report,
          platforms,
          ...(scheduledAt ? { scheduled_at: scheduledAt } : {}),
        }),
      });
      if (!response.ok) throw new Error(`Campaign rejected (${response.status})`);
      const data = (await response.json()) as {
        campaign_id: string;
        campaign_token: string;
      };
      setCampaignToken(data.campaign_token);
      void streamCampaign(data.campaign_id, data.campaign_token, generation);
    } catch {
      setError("Không thể khởi tạo chiến dịch nội dung.");
      setWorking(false);
    }
  };

  const approveAndPublish = async () => {
    if (!campaign || !campaignToken || working) return;
    setWorking(true);
    setError(null);
    if (isMockMode) {
      setCampaign({
        ...campaign,
        status: "completed",
        drafts: campaign.drafts.map((draft) => ({
          ...draft,
          status: "published",
          provider_post_id: `mock-${draft.platform}`,
        })),
        completed_at: new Date().toISOString(),
      });
      setWorking(false);
      return;
    }

    try {
      const approve = await fetch(
        `${backendUrl}/api/content-campaigns/${campaign.id}/approve`,
        { method: "POST", headers: { Authorization: `Bearer ${campaignToken}` } },
      );
      if (!approve.ok) throw new Error("Approval failed");
      const publish = await fetch(
        `${backendUrl}/api/content-campaigns/${campaign.id}/publish`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${campaignToken}`,
            "Idempotency-Key": `${campaign.id}-publish-${Date.now()}`,
          },
        },
      );
      if (!publish.ok) throw new Error("Publish failed");
      streamGenerationRef.current += 1;
      void streamCampaign(campaign.id, campaignToken, streamGenerationRef.current);
    } catch {
      setError("Không thể duyệt hoặc đăng chiến dịch.");
      setWorking(false);
    }
  };

  const cancelScheduledCampaign = async () => {
    if (!campaign || !campaignToken || working || campaign.status !== "scheduled" || isMockMode) return;
    setWorking(true);
    setError(null);
    try {
      const response = await fetch(
        `${backendUrl}/api/content-campaigns/${campaign.id}/cancel`,
        { method: "POST", headers: { Authorization: `Bearer ${campaignToken}` } },
      );
      if (!response.ok) throw new Error("Cancel failed");
      setCampaign({ ...campaign, status: "cancelled" });
      eventSourceRef.current?.close();
    } catch {
      setError("Không thể huỷ lịch đăng.");
    } finally {
      setWorking(false);
    }
  };

  const canApprove = campaign?.status === "waiting_approval" || campaign?.status === "needs_review";
  const canCancel = campaign?.status === "scheduled";
  const approvalLabel = campaign?.status === "needs_review"
    ? "Duyệt lại & đăng phần còn thiếu"
    : "Duyệt & đăng bài";

  return (
    <div className="bg-white/90 dark:bg-slate-900/60 border border-indigo-200/80 dark:border-indigo-500/30 rounded-3xl p-6 sm:p-7 shadow-xs space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-slate-100">
              Agentic SEO & đăng đa nền tảng
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Agent lập claim, tạo biến thể, kiểm tra trùng lặp rồi chờ bạn duyệt.
            </p>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" /> Approval bắt buộc
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {DEFAULT_PLATFORMS.map((platform) => {
          const selected = platforms.includes(platform);
          return (
            <button
              key={platform}
              type="button"
              onClick={() => togglePlatform(platform)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-semibold transition-colors ${
                selected
                  ? "bg-indigo-600 border-indigo-500 text-white"
                  : "bg-slate-100 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-500"
              }`}
            >
              {selected && <Check className="inline w-3 h-3 mr-1" />}
              {PLATFORM_LABELS[platform]}
            </button>
          );
        })}
        <button
          type="button"
          onClick={createCampaign}
          disabled={working || !platforms.length}
          className="ml-auto inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
        >
          {working ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Globe2 className="w-3.5 h-3.5" />}
          {campaign ? "Tạo lại bản nháp" : "Tạo chiến dịch"}
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 px-3 py-2">
        <CalendarClock className="w-4 h-4 text-indigo-500" />
        <label htmlFor="campaign-schedule" className="text-xs font-semibold text-slate-600 dark:text-slate-300">
          Đăng lúc (tuỳ chọn)
        </label>
        <input
          id="campaign-schedule"
          type="datetime-local"
          value={scheduleAt}
          onChange={(event) => setScheduleAt(event.target.value)}
          disabled={working || isMockMode}
          className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1 text-xs text-slate-700 dark:text-slate-200 disabled:opacity-50"
        />
        <span className="text-[11px] text-slate-500 dark:text-slate-400">
          Tối đa 31 ngày; server sẽ chuẩn hoá múi giờ và kiểm tra lại.
        </span>
      </div>

      {campaign && (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              Trạng thái: <span className="text-indigo-500">{campaign.status}</span>
            </span>
            {canApprove && (
              <button
                type="button"
                onClick={approveAndPublish}
                disabled={working}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold disabled:opacity-50"
              >
                {working ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                {approvalLabel}
              </button>
            )}
            {canCancel && (
              <button
                type="button"
                onClick={cancelScheduledCampaign}
                disabled={working}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-rose-300 dark:border-rose-900 text-rose-600 dark:text-rose-400 font-semibold disabled:opacity-50"
              >
                Huỷ lịch đăng
              </button>
            )}
          </div>

          {campaign.drafts.map((draft) => (
            <div key={draft.id} className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/50 p-4 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{PLATFORM_LABELS[draft.platform]}</span>
                <span className="text-[10px] uppercase text-slate-500 font-semibold">{draft.status}</span>
              </div>
              {draft.title && <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">{draft.title}</h4>}
              <p className="text-xs leading-relaxed whitespace-pre-wrap text-slate-600 dark:text-slate-300">{draft.body}</p>
              {draft.hashtags.length > 0 && <p className="text-[11px] text-indigo-500">{draft.hashtags.join(" ")}</p>}
            </div>
          ))}
        </div>
      )}

      {error && <p role="alert" className="text-xs text-rose-500">{error}</p>}
      <p className="text-[11px] text-slate-500 dark:text-slate-400">
        {isMockMode
          ? "Demo mode: không gọi tài khoản bên ngoài."
          : "Live mode: cần cấu hình connector và tài khoản nền tảng trước khi đăng."}
      </p>
    </div>
  );
};
