// ===== 记忆系统类型 =====

export type MemoryLayer = 'working' | 'short_term' | 'long_term';

export interface Memory {
  id: string;
  userId: string;
  type: MemoryType;
  layer: MemoryLayer;
  content: string;
  embedding?: number[]; // vector
  metadata: Record<string, unknown>;
  importance: number; // 0-1, higher = more important
  createdAt: string;
  lastAccessedAt: string;
  accessCount: number;
}

export type MemoryType =
  | 'conversation' // 对话片段
  | 'document' // 文档/笔记
  | 'preference' // 用户偏好
  | 'fact' // 事实/知识
  | 'reflection'; // AI 自我反思

export interface Document {
  id: string;
  userId: string;
  title: string;
  content: string;
  chunks: DocumentChunk[];
  tags: string[];
  createdAt: string;
}

export interface DocumentChunk {
  id: string;
  documentId: string;
  content: string;
  embedding?: number[];
  index: number;
}

export interface SearchResult {
  memoryId: string;
  content: string;
  score: number; // similarity score
  metadata: Record<string, unknown>;
}

export interface MemoryStats {
  totalMemories: number;
  totalDocuments: number;
  totalTokens: number;
  byLayer: Record<MemoryLayer, number>;
  byType: Record<MemoryType, number>;
}
