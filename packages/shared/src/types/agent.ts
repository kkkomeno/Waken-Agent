// ===== Agent 核心类型 =====

export type AgentStatus = 'idle' | 'running' | 'waiting' | 'done' | 'error';

export type AgentRole = 'researcher' | 'coder' | 'writer' | 'organizer' | 'general';

export interface AgentConfig {
  id: string;
  name: string;
  role: AgentRole;
  systemPrompt: string;
  model: ModelConfig;
  tools: string[]; // tool IDs
  permissions: AgentPermission[];
  maxSteps: number;
  timeout: number; // seconds
  createdAt: string;
  updatedAt: string;
}

export interface ModelConfig {
  provider: 'openai' | 'anthropic' | 'ollama';
  modelName: string;
  temperature: number;
  maxTokens: number;
}

export interface AgentPermission {
  toolId: string;
  allowed: boolean;
}

export interface AgentExecutionState {
  agentId: string;
  taskId: string;
  status: AgentStatus;
  currentStep: number;
  maxSteps: number;
  steps: AgentStep[];
  startTime: string;
  estimatedEndTime?: string;
}

export interface AgentStep {
  id: string;
  type: 'think' | 'act' | 'observe';
  content: string;
  toolCall?: ToolCall;
  timestamp: string;
}

export interface ToolCall {
  toolName: string;
  input: Record<string, unknown>;
  output?: unknown;
  error?: string;
}
