import axios, { type AxiosResponse } from "axios";
import type { Agent, Message } from "@/types/agent";

// 获取智能体列表
export const getAgents = async (): Promise<AxiosResponse<Agent[]>> => {
  return axios.get("/api/agents");
};

// 与智能体对话
export const chatWithAgent = async (
  params: {
    agentId: string;
    messages: Array<{
      role: "system" | "user" | "assistant";
      content: string;
    }>;
    apiKey: string;
    endpoint: string;
  },
  options?: {
    onMessage: (content: string) => void;
  }
): Promise<void> => {
  const user_msg_last = params.messages.length > 0 ? params.messages.at(-1) : undefined;
  console.log("收到的用户输入: ", user_msg_last.content);
  const response = await axios.post(
    params.endpoint,
    // dify配置
    // {
    //   inputs: {},
    //   query: user_msg_last.content,

    //   response_mode: "blocking",
    //   user: "abc-123"
    // },
    // {
    //   headers: {
    //     Authorization: `Bearer ${params.apiKey}`,
    //     "Content-Type": "application/json"
    //   }
    // },
    {
      question: user_msg_last.content
    }
  );
  // 取出思考think之间的内容 dify配置
  // const answer = response.data.answer.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
  // langchain配置
  const answer = response.data.data;
  options?.onMessage(answer);
};
