<script setup lang="ts">
defineOptions({
  name: "AgentReport"
});
import { ref, onMounted, reactive, computed } from "vue";
import LineChart from "@/components/LineChart.vue";
import { getExamList } from "@/api/chat";
import { getOperationlog } from "@/api/monitor";

const questions = ref([]);

const dataList = ref([]);
const form = reactive({
  request_modular: "",
  status: "",
  page: 1,
  size: 100
});
const total = ref(0);

// 题型统计
const questionStats = ref([
  { type: "判断题", count: 0 },
  { type: "单选题", count: 0 },
  { type: "简答题", count: 0 },
  { type: "编程题", count: 0 },
  { type: "总数量", count: 0 }
]);

// 模块名称列表
const moduleNames = ["在线学习助手", "实时练习评测助手", "测试题生成专家", "教学方案设计专家", "实践报告评阅专家"];

// 筛选出今日日志
const todayDate = computed(() => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
});

const todayLogs = computed(() => {
  return dataList.value.filter(log => {
    const logDate = log.create_time?.split(" ")[0] || "";
    return logDate === todayDate.value;
  });
});

// 计算当日各模块使用次数
const activeModuleUsage = computed(() => {
  const usageMap = Object.fromEntries(moduleNames.map(name => [name, 0]));

  todayLogs.value.forEach(log => {
    if (moduleNames.includes(log.request_modular)) {
      usageMap[log.request_modular]++;
    }
  });

  return moduleNames.map(name => ({
    name,
    usage: usageMap[name]
  }));
});

// 获取最近七天日期数组（格式：YYYY-MM-DD）
const lastSevenDays = computed(() => {
  const result = [];
  const today = new Date();

  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    result.push(`${year}-${month}-${day}`);
  }

  return result;
});

// 按模块和日期分组统计使用次数
const weeklyUsageByModule = computed(() => {
  const days = lastSevenDays.value;
  const usageMap = Object.fromEntries(moduleNames.map(name => [name, Array(days.length).fill(0)]));

  dataList.value.forEach(log => {
    if (!log.create_time || !log.request_modular) return;

    const logDateStr = log.create_time.split(" ")[0]; // 取 'YYYY-MM-DD'
    const match = logDateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/); // 格式校验
    if (!match) return;

    const normalizedLogDate = logDateStr;

    const dayIndex = days.indexOf(normalizedLogDate);

    if (dayIndex !== -1 && moduleNames.includes(log.request_modular)) {
      usageMap[log.request_modular][dayIndex]++;
    }
  });

  return usageMap;
});

// 折线图数据
const lineChartData = computed(() => {
  const dates = lastSevenDays.value.map(dateStr => {
    const [year, month, day] = dateStr.split("-");
    return `${month}-${day}`;
  });

  return {
    dates,
    seriesData: moduleNames.map(name => ({
      name,
      data: weeklyUsageByModule.value[name]
    }))
  };
});

function getQuestionCounts() {
  getExamList().then(res => {
    questions.value = res.data;
    updateQuestionStats();
  });
}

function updateQuestionStats() {
  const stats = [
    { type: "判断题", count: 0 },
    { type: "单选题", count: 0 },
    { type: "简答题", count: 0 },
    { type: "编程题", count: 0 }
  ];

  stats.forEach(stat => {
    stat.count = questions.value.filter(q => q.type === stat.type).length;
  });

  const totalCount = stats.reduce((sum, item) => sum + item.count, 0);

  questionStats.value = [...stats, { type: "总数量", count: totalCount }];
}

async function getLogCounts() {
  await getOperationlog(form).then(res => {
    dataList.value = res.data;
  });
}

onMounted(() => {
  getQuestionCounts();
  getLogCounts();
});
</script>

<template>
  <div>
    <!-- 第一行：题型统计 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <div class="card-header">试题库题型统计</div>
          <el-row :gutter="10">
            <el-col v-for="(item, index) in questionStats" :key="index" :span="4">
              <div class="stat-block">
                <p class="title">{{ item.type }}</p>
                <p class="count">{{ item.count }}</p>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：当日最活跃模块 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <div class="card-header">当日最活跃模块</div>
          <el-row :gutter="10">
            <el-col v-for="(item, index) in activeModuleUsage" :key="index" :span="4">
              <div class="stat-block">
                <p class="title">{{ item.name }}</p>
                <p class="count">{{ item.usage }}次</p>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第四行：折线图 -->
    <el-row>
      <el-col :span="24">
        <el-card shadow="hover">
          <div class="card-header">近七日AI使用趋势</div>
          <line-chart :chart-data="lineChartData" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<style scoped>
.card-header {
  font-weight: bold;
  font-size: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.stat-block {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease-in-out;
  margin-bottom: 10px;
}

.stat-block:hover {
  transform: translateY(-2px);
}

.title {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.count {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}
</style>
