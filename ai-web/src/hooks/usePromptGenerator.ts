import { computed, ComputedRef } from "vue";

export interface FormData {
  // 添加TargetView中的字段
  selectedChapter: string;
  selectedCategory: string;
  selectedKnowledge: string;
  questionType: string;
  questionCount: number;
  questionLevel: string;

  // RequirementView中的字段
  useKnowledgeGraph: boolean;
  useRag: boolean;
  includeAnswer: boolean;
  includeAnalysis: boolean;
  customRequirementKey: string;
  customRequirementValue: string;
}

// 修改参数类型为ComputedRef
export function usePromptGenerator(formData: ComputedRef<Partial<FormData>>) {
  const promptText = computed(() => {
    let prompt = "你是一个基于知识库和知识图谱的测试题生成专家。请根据提供的上下文生成测试题。不要编造信息。\n";

    // 任务目标
    prompt += "\n";
    prompt += "=== 测试题范围 ===\n";
    if (formData.value.selectedChapter) prompt += `章节：${formData.value.selectedChapter}\n`;
    if (formData.value.selectedCategory) prompt += `知识点分类：${formData.value.selectedCategory}\n`;
    if (formData.value.selectedKnowledge) prompt += `具体知识点：${formData.value.selectedKnowledge}\n`;

    prompt += "\n";
    prompt += "=== 测试题基本信息 ===\n";
    if (formData.value.questionType) prompt += `题型：${formData.value.questionType}\n`;
    if (formData.value.questionCount) prompt += `题目数量：${formData.value.questionCount}\n`;
    if (formData.value.questionLevel) prompt += `题目难度：${formData.value.questionLevel}\n`;

    // 检索要求
    prompt += "\n";
    prompt += "=== 检索要求 ===\n";
    prompt += `- 知识图谱检索：${formData.value.useKnowledgeGraph ? "{kg_context}" : ""}\n`;
    prompt += `- 知识库RAG检索：${formData.value.useRag ? "{rag_context}" : "禁用"}\n`;

    // 输出结果要求
    prompt += "\n";
    prompt += "=== 输出要求 ===\n";
    prompt += `- 参考答案：${formData.value.includeAnswer ? "需要" : "不需要"}\n`;
    prompt += `- 答案解析：${formData.value.includeAnalysis ? "需要" : "不需要"}\n`;

    // 其他要求
    prompt += "\n";
    if (formData.value.customRequirementKey || formData.value.customRequirementValue) {
      prompt += "=== 其他要求 ===\n";
      prompt += `- ${formData.value.customRequirementKey}: ${formData.value.customRequirementValue}\n`;
    }

    return prompt;
  });

  return {
    promptText
  };
}
