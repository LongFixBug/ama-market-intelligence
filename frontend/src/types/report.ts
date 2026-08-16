export interface TargetAudience {
  title: string;
  desc: string;
  pain_points: string[];
}

export interface MarketGap {
  title: string;
  opportunity: string;
  priority: "Cao" | "Trung bình" | "Thấp";
}

export interface SWOT {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface CompetitorItem {
  name: string;
  type: "Trực tiếp" | "Gián tiếp";
  positioning: string;
  strengths: string[];
  weaknesses: string[];
  price_range: string;
  market_share_est?: string;
  website?: string;
}

export interface PricingTier {
  tier: string;
  price: number;
  description: string;
  features: string[];
}

export interface PricingStrategy {
  min_market_price: number;
  median_market_price: number;
  recommended_price: number;
  premium_market_price: number;
  unit: string;
  pricing_logic: string;
  margin_est: string;
  tiers: PricingTier[];
}

export interface RiskItem {
  category: "Thị trường" | "Đối thủ" | "Vận hành" | "Pháp lý" | "Tài chính";
  risk_title: string;
  risk_level: "Cao" | "Trung bình" | "Thấp";
  impact: string;
  mitigation: string;
}

export interface SEOKeywordItem {
  keyword: string;
  intent: "Mua hàng (Commercial)" | "Tìm hiểu (Informational)" | "So sánh (Navigational)";
  search_volume_est: "Rất cao" | "Cao" | "Trung bình" | "Ngách";
  competition: "Cao" | "Trung bình" | "Thấp";
  content_angle: string;
}

export interface GTMRoadmapPhase {
  phase: string;
  timeline: string;
  key_actions: string[];
}

export interface GraphNode {
  id: string;
  name: string;
  category: "competitor" | "product" | "segment" | "price" | "risk" | "keyword";
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

export interface MarketReport {
  id: string;
  topic: string;
  createdAt: string;
  executive_summary: string;
  market_size_est: string;
  growth_rate: string;
  target_audience: TargetAudience[];
  market_gaps: MarketGap[];
  swot: SWOT;
  competitors: CompetitorItem[];
  pricing: PricingStrategy;
  risks: RiskItem[];
  seo_strategy: SEOKeywordItem[];
  gtm_roadmap: GTMRoadmapPhase[];
  graph_data: KnowledgeGraphData;
}

export interface AgentStep {
  id: string;
  title: string;
  agent: string;
  status: "pending" | "running" | "completed" | "error";
  message: string;
  timestamp?: string;
  logs?: string[];
}
