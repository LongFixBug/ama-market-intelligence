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

export interface MarketReport {
  id: string;
  topic: string;
  createdAt: string;
  niche_analysis: NicheAnalysis;
  pricing: PricingStrategy;
  risks: RiskItem[];
  seo_keywords: string[];
  ai_prompts: AIPromptItem[];
  graph_data?: KnowledgeGraphData;
}
