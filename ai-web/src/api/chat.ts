import dify from "@/utils/http/dify";
import { http } from "@/utils/http";
import { GenerateLessonPlanParams } from "@/views/agent/plan/type";
import { AxiosResponse } from "axios";
import { Question } from "@/views/agent/exam/types";

export type AgentResponse = {
  event: string;
  task_id: string;
  id: string;
  message_id: string;
  conversation_id: string;
  mode: string;
  answer: string;
  metadata: {
    usage: object;
    retriever_resources: Array<object>;
  };
  created_at: number;
};

export type AgentRequest = {
  inputs: object;
  query: string;
  response_mode: string;
  conversation_id?: string;
  user: string;
  files?: Array<object>;
};

export type LessonPlanConfig = {
  chapter: string;
  sectionTitle: string;
  studentLevel: string;
  classHours: number;
  teachingStyle: string;
}

export type ChapterOption = {
  id: number,
  label: string;
  value: string;
}

export type ExamResponse = {
  questions: Question[];
}

export const chatWithAgent = (data: AgentRequest) => {
  return dify({
    url: "/dify/chat-messages",
    method: "post",
    data: data
  });
};

export const postQuestion = (data?: object) => {
  return http.request<object>("post", "/api/chat/ask", { data });
};

export const postExam = (
  data?: object
): Promise<ExamResponse> => {
  return http.request<ExamResponse>(
    "post",
    "/api/experts/question/",
    { data }
  );
};

export const postExamQuestions = (data?: object) => {
  return http.request<object>("post", "/api/exam/questions", { data });
};

export const getExamList = (params?: object) => {
  return http.request<object>("get", "/api/exam/questions", { params });
};

export const postQuestionStream = (data?: object) => {
  return http.request<object>("post", "/api/chat/stream", { data });
};

export const getStream = () => {
  return http.request<object>("get", "/api/chat/stream");
};

export const getChapters = () => {
  return http.request<ChapterOption[]>("get", "/api/course/lesson-plan/chapters");
};

export const getSections = (chapterId: number) => {
  return http.request<ChapterOption[]>("get", "/api/course/lesson-plan/sections", {
    params: {
      chapter_id: chapterId
    }
  });
};

export const generateLessonPlan = (data: GenerateLessonPlanParams) => {
  return http.request<{ content: string }>(
    "post",
    "/api/experts/lesson/",
    {
      data
    }
  );
};
