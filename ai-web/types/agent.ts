export interface Agent {
  id: string;
  name: string;
  icon: string;
  description: string;
  prompt: string;
  apiKey: string;
  endpoint: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}
