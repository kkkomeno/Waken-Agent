// ===== 工具类型 =====

export interface ToolDefinition {
  id: string;
  name: string;
  description: string;
  category: ToolCategory;
  inputSchema: Record<string, unknown>; // JSON Schema
  requiresAuth: boolean;
  isBuiltin: boolean;
  callCount: number;
  createdAt: string;
}

export type ToolCategory = 'search' | 'code' | 'file' | 'http' | 'ai' | 'custom';

export interface ToolExecutionResult {
  toolId: string;
  success: boolean;
  output?: unknown;
  error?: string;
  executionTime: number; // ms
}
