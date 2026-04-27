<template>
  <div class="code-review">
    <!-- 页面标题 & 学习提示 -->
    <div class="header">
      <h2>🧠 C 语言代码评测专家</h2>
      <p class="tip">
        在这里练习 C 语言编程。<br />
        提交后，AI 会从
        <strong>正确性、简洁度、运行效率</strong>
        三个维度为你点评。
      </p>
    </div>

    <!-- 练习说明 -->
    <el-alert title="当前练习：C 语言基础输入输出" type="info" :closable="false" style="margin-bottom: 12px" />

    <!-- Monaco 编辑器 -->
    <div ref="editorRef" class="editor-wrapper"></div>

    <!-- 提交按钮 -->
    <div class="actions">
      <el-button type="primary" size="large" @click="submitCode"> ✨ 提交并获取评测 </el-button>
    </div>

    <!-- 评测结果弹窗 -->
    <el-dialog v-model="dialogVisible" title="📋 代码评测报告" width="720px">
      <div v-if="reviewResult" class="review-result">
        <!-- 正确性 -->
        <el-result :icon="reviewResult.correctness.has_error ? 'error' : 'success'" :title="reviewResult.correctness.has_error ? '发现代码问题' : '代码逻辑正确 ✅'">
          <template #sub-title>
            {{ reviewResult.correctness.error_description }}
          </template>
        </el-result>

        <!-- 简洁度 & 效率 -->
        <el-descriptions :column="1" border margin-top="20px">
          <el-descriptions-item label="简洁度评分"> {{ reviewResult.simplicity.score }} / 100 </el-descriptions-item>

          <el-descriptions-item label="评价">
            {{ reviewResult.simplicity.comment }}
          </el-descriptions-item>

          <el-descriptions-item label="时间复杂度">
            {{ reviewResult.efficiency.time_complexity }}
          </el-descriptions-item>

          <el-descriptions-item label="效率分析">
            {{ reviewResult.efficiency.comment }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 建议 -->
        <div v-if="reviewResult.suggestions.length" class="suggestions">
          <h4>💡 改进建议</h4>
          <ul>
            <li v-for="(s, i) in reviewResult.suggestions" :key="i">
              {{ s }}
            </li>
          </ul>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import * as monaco from "monaco-editor";
import { ElButton, ElDialog, ElDescriptions, ElDescriptionsItem, ElAlert, ElResult } from "element-plus";

/* -------------------------
   Monaco Editor
-------------------------- */
const editorRef = ref<HTMLElement>();

let editor: monaco.editor.IStandaloneCodeEditor;

const code = ref(`#include <stdio.h>

int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d\\n", a + b);
    return 0;
}
`);

onMounted(() => {
  editor = monaco.editor.create(editorRef.value!, {
    value: code.value,
    language: "c",
    theme: "vs-dark",
    automaticLayout: true
  });

  editor.onDidChangeModelContent(() => {
    code.value = editor.getValue();
  });
});

/* -------------------------
   评测结果（静态）
-------------------------- */
const dialogVisible = ref(false);

const reviewResult = ref({
  correctness: {
    has_error: false,
    error_description: "代码逻辑正确，未发现语法或运行时错误，实现方式稳健。"
  },
  simplicity: {
    score: 85,
    comment: "变量命名具有语义，main 函数结构清晰；若能将输入逻辑拆分为独立函数会更佳。"
  },
  efficiency: {
    time_complexity: "O(1)",
    comment: "本例为常量时间操作，不包含循环或递归，效率极高。"
  },
  suggestions: ["建议将输入与计算逻辑拆分为独立函数，提高可维护性", "可在第 4 行为变量 a、b 增加注释说明用途"]
});

/* -------------------------
   提交评测
-------------------------- */
const submitCode = () => {
  if (!code.value.trim()) {
    alert("请先输入 C 语言代码");
    return;
  }
  dialogVisible.value = true;
};
</script>

<style scoped>
.code-review {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.header h2 {
  margin-bottom: 8px;
}

.tip {
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
}

.editor-wrapper {
  height: 420px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #ddd;
}

.actions {
  margin-top: 16px;
  text-align: right;
}

.review-result {
  max-height: 520px;
  overflow-y: auto;
}

.suggestions {
  margin-top: 20px;
}

.suggestions ul {
  padding-left: 20px;
}
</style>
