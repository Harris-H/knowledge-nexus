import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8081/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// ---- Papers ----
export interface Paper {
  id: string;
  title: string;
  abstract?: string;
  year?: number;
  venue?: string;
  domain_id?: string;
  url?: string;
  doi?: string;
  arxiv_id?: string;
  s2_id?: string;
  citation_count: number;
  influential_citation_count: number;
  impact_score: number;
  key_contributions?: string;
  summary?: string;
  fields_of_study?: string;
  ai_status: string;
  pdf_path?: string;
  authors: string[];
  created_at: string;
}

export interface PaperList {
  items: Paper[];
  total: number;
  page: number;
  size: number;
}

export const papersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaperList>("/papers/", { params }),
  get: (id: string) => api.get<Paper>(`/papers/${id}`),
  create: (data: Record<string, unknown>) => api.post<Paper>("/papers/", data),
  delete: (id: string) => api.delete(`/papers/${id}`),
  batchDelete: (ids: string[]) =>
    api.post<{ deleted: number }>("/papers/batch-delete", { ids }),
};

// ---- Graph ----
export interface GraphNode {
  id: string;
  type: string;
  label: string;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface Subgraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export const graphApi = {
  full: (minCitations = 0, limit = 100) =>
    api.get<Subgraph>("/graph/full", { params: { min_citations: minCitations, limit } }),
  subgraph: (center: string, depth = 1, limit = 50) =>
    api.get<Subgraph>("/graph/subgraph", { params: { center, depth, limit } }),
  addRelation: (data: Record<string, unknown>) =>
    api.post("/graph/relations", data),
};

// ---- Crawler ----
export interface CrawlTask {
  id: string;
  status: string;
  domain: string;
  subdomain?: string;
  source: string;
  searched: number;
  candidates: number;
  imported: number;
  failed: number;
  created_at: string;
}

export const crawlerApi = {
  start: (data: Record<string, unknown>) =>
    api.post<CrawlTask>("/crawler/start", data),
  getTask: (id: string) => api.get<CrawlTask>(`/crawler/tasks/${id}`),
  listTasks: () => api.get<CrawlTask[]>("/crawler/tasks"),
  cancelTask: (id: string) => api.post(`/crawler/tasks/${id}/cancel`),
};

// ---- Search ----
export interface SearchResult {
  id: string;
  type: string;
  title: string;
  snippet?: string;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
}

export const searchApi = {
  search: (q: string, params?: Record<string, unknown>) =>
    api.get<SearchResponse>("/search/", { params: { q, ...params } }),
};

// ---- KnowledgeNodes ----
export interface KnowledgeNode {
  id: string;
  name: string;
  node_type: string;
  domain: string;
  description?: string;
  summary?: string;
  source_info?: string;
  year?: number;
  tags?: string;
  created_at: string;
}

export interface KnowledgeNodeList {
  items: KnowledgeNode[];
  total: number;
}

export const knowledgeNodesApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<KnowledgeNodeList>("/knowledge-nodes/", { params }),
  create: (data: Record<string, unknown>) =>
    api.post<KnowledgeNode>("/knowledge-nodes/", data),
  delete: (id: string) => api.delete(`/knowledge-nodes/${id}`),
  batchDelete: (ids: string[]) =>
    api.post<{ deleted: number }>("/knowledge-nodes/batch-delete", { ids }),
};

// ---- AI Analysis ----
export interface AIDiscovery {
  source_id: string;
  source_name: string;
  source_type: string;
  target_id: string;
  target_name: string;
  target_type: string;
  relation_type: string;
  description: string;
  confidence: number;
  insight: string;
}

export interface DiscoverResult {
  discoveries: AIDiscovery[];
  total_nodes: number;
}

export interface DeriveResult {
  abstract_pattern?: {
    name: string;
    description: string;
  };
  transfer_ideas?: Array<{
    from_domain: string;
    to_domain: string;
    idea: string;
    feasibility: string;
  }>;
  missing_links?: Array<{
    description: string;
    potential_value: string;
  }>;
  new_hypotheses?: Array<{
    hypothesis: string;
    evidence_needed: string;
    impact: string;
  }>;
}

export interface PairAnalysis {
  has_relation: boolean;
  relation_type: string;
  description: string;
  confidence: number;
  structural_analogy: string;
  causal_link: string;
  complementarity: string;
  unified_framework: string;
  new_insight: string;
}

export const aiApi = {
  discover: (limit = 8) =>
    api.post<DiscoverResult>("/ai/discover", { limit }, { timeout: 120000 }),
  derive: (nodeIds: string[]) =>
    api.post<DeriveResult>("/ai/derive", { node_ids: nodeIds }, { timeout: 120000 }),
  analyzePair: (nodeAId: string, nodeBId: string) =>
    api.post<PairAnalysis>("/ai/analyze-pair", { node_a_id: nodeAId, node_b_id: nodeBId }, { timeout: 120000 }),
  saveDiscoveries: (discoveries: AIDiscovery[], autoConfirm = false) =>
    api.post<{ saved: number }>("/ai/save-discoveries", { discoveries, auto_confirm: autoConfirm }),
};

export default api;
