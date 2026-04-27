<template>
  <el-form ref="form" label-position="top">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="章节">
          <el-select v-model="config.chapter" value-key="id">
            <el-option v-for="item in chapterOptions" :key="item.id" :label="item.label" :value="item" />
          </el-select>
        </el-form-item>
      </el-col>

      <el-col :span="8">
        <el-form-item label="知识点">
          <el-select v-model="config.knowledge_point" placeholder="请选择知识点">
            <el-option v-for="item in sectionOptions" :key="item.id" :label="item.label" :value="item.label" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <!-- 题型 + 数量 + 难度 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="题型选择">
          <el-select v-model="config.question_type" placeholder="请选择题型">
            <el-option label="判断题" value="true_false" />
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multiple_choice" />
          </el-select>
        </el-form-item>
      </el-col>

      <el-col :span="8">
        <el-form-item label="题目数量">
          <el-input-number v-model="config.question_count" :min="1" :max="50" />
        </el-form-item>
      </el-col>

      <el-col :span="8">
        <el-form-item label="题目难度">
          <el-select v-model="config.difficulty" placeholder="请选择难度">
            <el-option label="容易" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, defineExpose } from "vue";
import { ChapterOption } from "../plan/type";
import { ElMessage } from "element-plus";
import { getChapters, getSections } from "@/api/chat";
import type { QuestionGenConfig } from "./types";

/* ---------- 下拉数据源 ---------- */
const chapterOptions = ref<ChapterOption[]>([]);
const sectionOptions = ref<ChapterOption[]>([]);

/* ---------- 核心配置（唯一真相源） ---------- */
const config = ref<QuestionGenConfig>({
  chapter: null,
  knowledge_point: "",
  question_type: "single_choice",
  question_count: 5,
  difficulty: "medium"
});

/* ---------- 生命周期 ---------- */
onMounted(async () => {
  try {
    const res = await getChapters();
    chapterOptions.value = res.data ?? [];
  } catch {
    ElMessage.error("获取章节失败");
  }
});

/* ---------- 监听器 ---------- */
watch(
  () => config.value.chapter,
  async chapter => {
    if (!chapter) {
      sectionOptions.value = [];
      config.value.knowledge_point = "";
      return;
    }
    try {
      console.log(chapter);
      const res = await getSections(chapter.id);
      sectionOptions.value = res.data;
      config.value.knowledge_point = "";
    } catch {
      ElMessage.error("获取知识点失败");
    }
  }
);

/* ---------- 对外暴露 ---------- */
defineExpose({
  getData: () => config.value
});
</script>
