import { create } from "zustand";
import { papersApi, graphApi, crawlerApi, searchApi } from "../api";
import type {
  Paper,
  GraphNode,
  GraphEdge,
  CrawlTask,
  SearchResult,
} from "../api";

interface AppState {
  // Papers
  papers: Paper[];
  papersTotal: number;
  papersLoading: boolean;
  paperSort: { field: string; order: "asc" | "desc" };
  fetchPapers: (page?: number, size?: number, q?: string) => Promise<void>;
  setPaperSort: (field: string, order: "asc" | "desc") => void;

  // Graph
  graphNodes: GraphNode[];
  graphEdges: GraphEdge[];
  graphLoading: boolean;
  fetchFullGraph: (minCitations?: number) => Promise<void>;
  fetchSubgraph: (centerId: string, depth?: number) => Promise<void>;

  // Crawler
  crawlTasks: CrawlTask[];
  activeCrawlTask: CrawlTask | null;
  fetchCrawlTasks: () => Promise<void>;
  startCrawl: (data: Record<string, unknown>) => Promise<CrawlTask>;
  pollCrawlTask: (taskId: string) => void;
  stopPolling: () => void;

  // Search
  searchResults: SearchResult[];
  searchLoading: boolean;
  doSearch: (query: string) => Promise<void>;
}

let pollTimer: ReturnType<typeof setInterval> | null = null;

export const useStore = create<AppState>((set, get) => ({
  // ---- Papers ----
  papers: [],
  papersTotal: 0,
  papersLoading: false,
  paperSort: { field: "created_at", order: "desc" },

  fetchPapers: async (page = 1, size = 20, q?: string) => {
    set({ papersLoading: true });
    try {
      const { field, order } = get().paperSort;
      const params: Record<string, unknown> = { page, size, sort: field, order };
      if (q) params.q = q;
      const { data } = await papersApi.list(params);
      set({ papers: data.items, papersTotal: data.total });
    } finally {
      set({ papersLoading: false });
    }
  },

  setPaperSort: (field, order) => {
    set({ paperSort: { field, order } });
  },

  // ---- Graph ----
  graphNodes: [],
  graphEdges: [],
  graphLoading: false,

  fetchFullGraph: async (minCitations = 0) => {
    set({ graphLoading: true });
    try {
      const { data } = await graphApi.full(minCitations, 200);
      set({ graphNodes: data.nodes, graphEdges: data.edges });
    } finally {
      set({ graphLoading: false });
    }
  },

  fetchSubgraph: async (centerId: string, depth = 2) => {
    set({ graphLoading: true });
    try {
      const { data } = await graphApi.subgraph(centerId, depth, 100);
      set({ graphNodes: data.nodes, graphEdges: data.edges });
    } finally {
      set({ graphLoading: false });
    }
  },

  // ---- Crawler ----
  crawlTasks: [],
  activeCrawlTask: null,

  fetchCrawlTasks: async () => {
    const { data } = await crawlerApi.listTasks();
    set({ crawlTasks: data });
    // 自动检测进行中的任务并启动轮询
    const running = data.find(
      (t: CrawlTask) => t.status === "running" || t.status === "queued"
    );
    if (running) {
      set({ activeCrawlTask: running });
      get().pollCrawlTask(running.id);
    }
  },

  startCrawl: async (params) => {
    const { data } = await crawlerApi.start(params);
    set({ activeCrawlTask: data });
    get().pollCrawlTask(data.id);
    return data;
  },

  pollCrawlTask: (taskId: string) => {
    get().stopPolling();
    pollTimer = setInterval(async () => {
      try {
        const { data } = await crawlerApi.getTask(taskId);
        set({ activeCrawlTask: data });
        if (["completed", "failed", "cancelled", "preview_ready"].includes(data.status)) {
          get().stopPolling();
          if (data.status === "completed") {
            get().fetchPapers();
          }
          get().fetchCrawlTasks();
        }
      } catch {
        get().stopPolling();
      }
    }, 3000);
  },

  stopPolling: () => {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  },

  // ---- Search ----
  searchResults: [],
  searchLoading: false,

  doSearch: async (query: string) => {
    set({ searchLoading: true });
    try {
      const { data } = await searchApi.search(query);
      set({ searchResults: data.results });
    } finally {
      set({ searchLoading: false });
    }
  },
}));
