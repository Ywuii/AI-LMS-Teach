<script setup lang="ts">
import { ref } from "vue";
const response = ref("");
const isFetching = ref(false);

function getResponse() {
  if (isFetching.value) return;

  isFetching.value = true;
  const eventSource = new EventSource("http://127.0.0.1:8000/api/chat/stream");

  eventSource.onmessage = event => {
    try {
      const data = JSON.parse(event.data);
      response.value += data.token;
    } catch (e) {
      console.error("解析失败:", e);
    }
  };

  eventSource.onopen = () => {
    console.log("SSE 连接已建立");
  };

  eventSource.onerror = err => {
    console.error("SSE 错误:", err);
    eventSource.close();
    isFetching.value = false;
  };

  eventSource.addEventListener("complete", () => {
    eventSource.close();
    isFetching.value = false;
  });
}
</script>

<template>
  <div>
    <el-button @click="getResponse">开始</el-button>
    {{ response }}
  </div>
</template>

<style scoped>
.container {
  padding: 20px;
}
</style>
