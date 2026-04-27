export type QuestionType = "判断题" | "单选题" | "简答题" | "编程题";

export interface Option {
  opt_a: string;
  opt_b: string;
  opt_c: string;
  opt_d: string;
  correct_answer: string;
}

export interface Question {
  id: number;
  type: QuestionType;
  knowledge: string;
  question: string;
  answer: string;
  analysis: string;
  status: boolean;
  create_time: string;
  option?: Option | null;
}
