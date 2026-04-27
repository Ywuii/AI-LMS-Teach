<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { ChapterOption, LessonPlanConfig } from "./type";
import { generateLessonPlan, getChapters, getSections } from "@/api/chat";

const config = ref<LessonPlanConfig>({
  chapter: null, // ✅ 章节对象（或 null）
  sectionTitle: "", // ✅ 知识点字符串
  studentLevel: "零基础",
  classHours: 90,
  teachingStyle: "案例驱动"
});
const chapterOptions = ref<ChapterOption[]>([]);
const sectionOptions = ref<ChapterOption[]>([]);

const loading = ref(false);
const resultVisible = ref(false);

async function handleGenerate() {
  if (!config.value.chapter || !config.value.sectionTitle) {
    ElMessage.warning("请选择章节和知识点");
    return;
  }

  loading.value = true;
  try {
    const res = await generateLessonPlan({
      chapter: config.value.chapter.label,
      section_title: config.value.sectionTitle,
      student_level: config.value.studentLevel,
      class_hours: config.value.classHours,
      teaching_style: config.value.teachingStyle
    });

    ElMessage.success("教案生成成功");
    resultVisible.value = true;
    console.log(res);
  } catch (err) {
    ElMessage.error("教案生成失败");
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  try {
    const res = await getChapters();
    chapterOptions.value = res.data;
    console.log(chapterOptions);
  } catch {
    ElMessage.error("获取章节失败");
  }
});

watch(
  () => config.value.chapter,
  async chapter => {
    if (!chapter) {
      sectionOptions.value = [];
      config.value.sectionTitle = "";
      return;
    }

    try {
      const res = await getSections(chapter.id);
      sectionOptions.value = res.data;
      config.value.sectionTitle = "";
    } catch {
      ElMessage.error("获取知识点失败");
    }
  }
);
</script>

<template>
  <div class="lesson-plan-config">
    <h3>教案生成配置</h3>

    <el-form :model="config" label-width="140px" class="config-form">
      <el-form-item label="章节">
        <el-select v-model="config.chapter" placeholder="选择章节" style="width: 300px" value-key="id">
          <el-option v-for="item in chapterOptions" :key="item.id" :label="item.label" :value="item" />
        </el-select>
      </el-form-item>

      <el-form-item label="知识点">
        <el-select v-model="config.sectionTitle" placeholder="选择知识点" style="width: 300px">
          <el-option v-for="item in sectionOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>

      <el-form-item label="学生基础">
        <el-radio-group v-model="config.studentLevel">
          <el-radio label="零基础" />
          <el-radio label="入门" />
          <el-radio label="有编程经验" />
        </el-radio-group>
      </el-form-item>

      <el-form-item label="建议课时（分钟）">
        <el-input-number v-model="config.classHours" :min="40" :max="120" />
      </el-form-item>

      <el-form-item label="教学风格">
        <el-select v-model="config.teachingStyle" placeholder="选择教学风格">
          <el-option label="讲授型" value="讲授型" />
          <el-option label="案例驱动" value="案例驱动" />
          <el-option label="问题导向" value="问题导向" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="loading" @click="handleGenerate"> 生成教案 </el-button>
      </el-form-item>
    </el-form>

    <el-dialog v-model="resultVisible" title="教案生成结果" width="70%">
      <pre>{{ config }}</pre>
    </el-dialog>
  </div>
</template>
<style scoped>
.lesson-plan-config {
  padding: 20px;
  background-color: var(--el-bg-color);
}

.config-form {
  max-width: 600px;
  margin-top: 20px;
}
</style>
