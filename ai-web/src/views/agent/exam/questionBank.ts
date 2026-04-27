// questionBank.ts
export interface Question {
  id: number;
  chapter: string;
  knowledgePoint: string;
  type: "single_choice";
  question: string;
  options: string[];
  answer: string;
  analysis: string;
}

export const staticQuestionBank: Question[] = [
  {
    id: 1,
    chapter: "第一章 程序设计基础",
    knowledgePoint: "程序文档",
    type: "single_choice",
    question: "程序文档中必须包含以下哪项内容？",
    options: ["程序名称", "运行环境", "程序功能", "编译器版本"],
    answer: "A",
    analysis: "程序文档应包含名称、功能、运行环境等信息。"
  },
  {
    id: 2,
    chapter: "第二章 程序编译与运行",
    knowledgePoint: "连接编辑程序",
    type: "single_choice",
    question: "连接编辑程序的作用是？",
    options: ["编译源代码", "连接函数库", "生成可执行文件", "调试程序"],
    answer: "C",
    analysis: "连接编辑程序负责生成可执行文件。"
  },
  {
    id: 3,
    chapter: "第二章 程序编译与运行",
    knowledgePoint: "程序运行流程",
    type: "single_choice",
    question: "程序运行阶段包括以下哪项？",
    options: ["编译", "连接", "运行", "调试"],
    answer: "C",
    analysis: "运行阶段指执行已生成的可执行程序。"
  }
];