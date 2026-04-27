<template>
  <div class="workflow-container">
    <el-card style="max-width: 100%">
      <template #header>
        <div class="card-header">
          <el-steps :active="activeStep" align-center finish-status="success">
            <el-step title="任务目标" />
            <el-step title="任务要求" />
            <el-step title="输出结果" />
            <el-step title="MCP操作" />
          </el-steps>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="任务目标" name="target">
          <TargetView ref="targetRef" />
        </el-tab-pane>
        <el-tab-pane label="任务要求" name="requirement">
          <RequirementView ref="requirementRef" :questionType="qtype" />
        </el-tab-pane>
        <el-tab-pane label="输出结果" name="result">
          <ResultView ref="resultRef" :params="resultParams" @update-questions="qs => (questions = qs)" />
        </el-tab-pane>
        <el-tab-pane label="MCP操作" name="mcp">
          <McpView ref="mcpRef" :questionType="qtype" :knowledge="knowledge" :questions="questions" />
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <div class="card-footer">
          <el-button type="primary" @click="prevStep" :disabled="activeStep === 0">上一步</el-button>
          <el-button type="success" @click="nextStep" :disabled="activeStep === 3">下一步</el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import TargetView from "./TargetView.vue";
import RequirementView from "./RequirementView.vue";
import ResultView from "./ResultView.vue";
import McpView from "./McpView.vue";
import { usePromptGenerator } from "@/hooks/usePromptGenerator";
import type { Question } from "./types";
import type { QuestionGenConfig } from "./types";

const questions = ref<Question[]>([]);

const activeStep = ref(0);
const activeTab = ref("target");

const targetRef = ref<InstanceType<typeof TargetView>>();
const requirementRef = ref<InstanceType<typeof RequirementView>>();
const resultRef = ref<InstanceType<typeof ResultView>>();
const mcpRef = ref<InstanceType<typeof McpView>>();

const qtype = ref("");
const knowledge = ref("");

/* ---------- 真实数据源 ---------- */
const targetData = ref<QuestionGenConfig | null>(null);
const requirementData = ref<any>(null);

const updateFormData = () => {
  if (targetRef.value) {
    targetData.value = targetRef.value.getData();
  }
  if (requirementRef.value) {
    requirementData.value = requirementRef.value.getData();
  }
};

/* ---------- 合并参数 ---------- */
const resultParams = computed(() => {
  const t = targetData.value;
  const r = requirementData.value;

  if (!t || !r) return null;

  return {
    chapter: t.chapter?.id ?? "",
    knowledge_type: t.chapter?.label ?? "",
    knowledge_point: t.knowledge_point,
    question_type: t.question_type,
    question_count: t.question_count,
    difficulty: t.difficulty,

    use_kg: r.useKnowledgeGraph,
    use_rag: r.useRag,
    include_answer: r.includeAnswer,
    include_explanation: r.includeAnalysis,
    custom_key: r.customRequirementKey,
    custom_value: r.customRequirementValue
  };
});

/* ---------- Prompt ---------- */

/* ---------- 派生字段 ---------- */
watch(resultParams, params => {
  if (!params) return;
  qtype.value = params.question_type;
  knowledge.value = params.knowledge_point || params.knowledge_type;
});

/* ---------- Step / Tab 联动 ---------- */
watch(activeStep, newVal => {
  const tabs = ["target", "requirement", "result", "mcp"];
  activeTab.value = tabs[newVal];
});

watch(activeTab, newVal => {
  const stepsMap = { target: 0, requirement: 1, result: 2, mcp: 3 };
  activeStep.value = stepsMap[newVal as keyof typeof stepsMap];
});

const prevStep = () => {
  updateFormData();
  if (activeStep.value > 0) activeStep.value--;
};

const nextStep = () => {
  updateFormData();
  if (activeStep.value < 3) activeStep.value++;
};

const handleTabChange = () => {
  updateFormData();
};
</script>

<style scoped>
.workflow-container {
  max-width: 100%;
}
.card-header {
  text-align: center;
}
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
