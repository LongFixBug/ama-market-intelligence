export interface NicheAnalysis {
  summary: string;
  growth_potential: string;
}

export interface PricingStrategy {
  price_range: string;
  rationale: string;
  tagline: string;
  min_market_price?: number;
  median_market_price?: number;
  recommended_price?: number;
  premium_market_price?: number;
  unit?: string;
  pricing_logic?: string;
  margin_est?: string;
  tiers?: Array<{
    tier: string;
    price: number;
    description: string;
    features: string[];
  }>;
}

export interface RiskItem {
  index: number;
  title: string;
  category?: string;
  risk_title?: string;
  risk_level?: string;
  impact?: string;
  mitigation?: string;
}

export interface AIPromptItem {
  prompt: string;
}

export interface GraphNode {
  id: string;
  name: string;
  category: "product" | "competitor" | "feature" | "price" | "risk" | "audience" | "keyword";
  size?: number;
}

export interface GraphLink {
  source: string;
  target: string;
  relationship: string;
}

export interface KnowledgeGraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface SourceRef {
  title: string;
  url: string;
  snippet?: string;
  published_at?: string | null;
}

export interface MarketReport {
  id: string;
  topic: string;
  createdAt: string;
  niche_analysis: NicheAnalysis;
  pricing: PricingStrategy;
  risks: RiskItem[];
  seo_keywords: string[];
  ai_prompts: AIPromptItem[];
  sources?: SourceRef[];
  graph_data?: KnowledgeGraphData;
}

export type ContentPlatform = "blog" | "x" | "linkedin" | "facebook";

export interface ContentDraft {
  id: string;
  platform: ContentPlatform;
  title: string;
  slug?: string;
  excerpt?: string;
  body: string;
  canonical_url?: string | null;
  seo_keywords: string[];
  hashtags: string[];
  content_hash: string;
  status: string;
  provider_post_id?: string | null;
  published_url?: string | null;
  error_code?: string | null;
}

export interface ContentPublishResult {
  platform: ContentPlatform;
  success: boolean;
  code: string;
  provider_post_id?: string | null;
  published_url?: string | null;
  verified: boolean;
  detail?: string | null;
}

export interface ContentCampaign {
  id: string;
  report_id: string;
  topic: string;
  platforms: ContentPlatform[];
  status: string;
  step: number;
  claims: Array<{
    text: string;
    evidence: SourceRef[];
    confidence: number;
  }>;
  drafts: ContentDraft[];
  publish_results: ContentPublishResult[];
  issues: string[];
  actions: Array<{
    action: string;
    step: number;
    message: string;
    created_at: string;
  }>;
  revision_count: number;
  approval_required: boolean;
  approved_at?: string | null;
  scheduled_at?: string | null;
  created_at: string;
  completed_at?: string | null;
}
