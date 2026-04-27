<template>
  <div class="session-list">
    <button @click="$emit('create')">+ 新建会话</button>

    <ul>
      <li v-for="s in sessions" :key="s.session_id" :class="{ active: s.session_id === activeId }" @click="$emit('select', s.session_id)">
        <div class="title">{{ s.title || "无标题" }}</div>
        <div class="time">{{ formatTime(s.updated_at) }}</div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  sessions: any[];
  activeId?: string | null;
}>();

defineEmits(["select", "create"]);

function formatTime(t: string) {
  return new Date(t).toLocaleString();
}
</script>

<style scoped>
.session-list {
  width: 260px;
  border-right: 1px solid #ddd;
  padding: 12px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 8px;
  cursor: pointer;
}

li.active {
  background-color: #e6f7ff;
}

.title {
  font-weight: bold;
}

.time {
  font-size: 12px;
  color: #888;
}
</style>
