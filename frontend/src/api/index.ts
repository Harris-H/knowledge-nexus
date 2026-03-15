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

export default api;
