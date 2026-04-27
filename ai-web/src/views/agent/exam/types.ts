import { ChapterOption } from "../plan/type";

// types.ts
export interface Question {
  question: string;
  answer: string;
  options?: string[];
  analysis: string;
}

// 类型定义
export interface Option {
  value: string;
  originalIndex: number;
}

export interface ShuffledQuestion extends Omit<Question, "options"> {
  options: Option[];
}

export interface Exam {
  type: string;
  knowledge: string;
  question: string;
  answer: string;
  options?: string[];
  analysis: string;
}

export interface QuestionGenConfig {
  chapter: ChapterOption | null;         // 章节对象（label 用）
  knowledge_point: string;       // 具体知识点
  question_type: string;         // 题型
  question_count: number;        // 题目数量
  difficulty: string;            // 难度
}