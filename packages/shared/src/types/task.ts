// ===== 任务类型 =====

export type TaskStatus = 'pending' | 'decomposing' | 'running' | 'waiting_input' | 'done' | 'error';

export type CollaborationMode = 'pipeline' | 'parallel' | 'debate';

export interface Task {
  id: string;
  userId: string;
  title: string;
  description: string;
  status: TaskStatus;
  collaborationMode: CollaborationMode;
  subTasks: SubTask[];
  agents: string[]; // assigned agent IDs
  tags: string[];
  createdAt: string;
  completedAt?: string;
}

export interface SubTask {
  id: string;
  parentTaskId: string;
  assignedAgent: string; // agent ID
  status: TaskStatus;
  input: string;
  output?: string;
  steps: import('./agent').AgentStep[];
  createdAt: string;
  completedAt?: string;
}

export interface TaskTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  collaborationMode: CollaborationMode;
  agentRoles: import('./agent').AgentRole[];
  promptTemplate: string;
}

export interface CreateTaskInput {
  title: string;
  description: string;
  collaborationMode: CollaborationMode;
  agentRoles?: import('./agent').AgentRole[];
  templateId?: string;
}
