<template>
  <el-card shadow="hover">
    <div style="text-align: center">
      <el-avatar :size="32" :src="member.avatar" />
      <h3>{{ member.name }}</h3>
      <p style="color: gray">{{ member.role }}</p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
interface Member {
  name: string;
  role: string;
  avatar: string;
}

defineProps<{
  member: Member;
}>();
</script>
