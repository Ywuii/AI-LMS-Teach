<script setup lang="ts">
import { ref } from "vue";
const answer = ref("");
const question = ref("");
const isFetching = ref(false);

// 处理流式响应
async function startStream() {
  answer.value = "";

  const url = "http://localhost:8000/api/chat/stream"; // 替换为你的 API 地址
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      question: question.value
    })
  });

  if (!response.ok || !response.body) {
    alert("请求失败");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    parseAndAppend(chunk);
  }

  function parseAndAppend(chunk: string) {
    // 解析 SSE 格式：data: {...}
    const lines = chunk.split("\n");
    for (const line of lines) {
      if (line.startsWith("data:")) {
        try {
          const jsonStr = line.slice(5).trim();
          if (!jsonStr) continue;
          const data = JSON.parse(jsonStr);
          if (data.token) {
            answer.value += data.token;
          }
        } catch (e) {
          console.error("JSON 解析失败:", e);
        }
      }
    }
  }
}
</script>

<template>
  <div class="container">
    <el-input v-model="question" placeholder="请输入你的问题..." />
    <el-button @click="startStream" :disabled="isFetching">提问</el-button>
    <p>AI智能体 回答：{{ answer }}</p>
  </div>
</template>

<style scoped>
.container {
  padding: 20px;
}
</style>
