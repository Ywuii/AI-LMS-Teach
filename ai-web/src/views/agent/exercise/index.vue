<script setup lang="ts">
import { ref, computed, onBeforeUnmount, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getExamList } from "@/api/chat";
defineOptions({
  name: "AgentExercise"
});

interface Question {
  id: number;
  type: string;
  knowledge: string;
  question: string;
  answer: string; // 原始答案 A/B/C/D
  analysis: string;
  status: boolean;
  create_time: string;
  option: {
    opt_a?: string;
    opt_b?: string;
    opt_c?: string;
    opt_d?: string;
  } | null;
  shuffledOption?: Record<string, string>;
  shuffledAnswer?: string;
}

interface ExamConfig {
  timeLimit: number;
  knowledge: string[];
  selectedTypes: string[];
  typeCounts: Record<string, number>;
  shuffleOptions: boolean;
}

interface ScoreItem {
  type: string;
  count: number;
  correct: number;
  score: number;
}

// 响应式状态
const examConfig = ref<ExamConfig>({
  timeLimit: 10,
  knowledge: [],
  selectedTypes: ["判断题", "单选题"],
  typeCounts: {
    判断题: 2,
    单选题: 2,
    简答题: 1,
    编程题: 1
  },
  shuffleOptions: true
});

const questionBank = ref<Question[]>([]);
const knowledgeOptions = ref<string[]>([]);
const examDialogVisible = ref(false);
const examQuestions = ref<Question[]>([]);
const userAnswers = ref<Record<number, string>>({});
const showAnswers = ref(false);
const showScore = ref(false);
const activeCollapse = ref<number[]>([]);
const currentPage = ref(1);

const currentQuestion = computed(() => {
  return currentPageQuestions.value[0];
});

const currentPageQuestions = computed(() => {
  return examQuestions.value.slice(currentPage.value - 1, currentPage.value);
});

const remainingTime = ref(0);
const timer = ref<NodeJS.Timeout | null>(null);

const remainingTimeDisplay = computed(() => {
  const minutes = Math.floor(remainingTime.value / 60);
  const seconds = remainingTime.value % 60;
  return `${minutes}分${seconds}秒`;
});

const scoreData = ref<ScoreItem[]>([]);
const totalScore = ref(0);
const correctRate = ref(0);

const questionTypes = [
  { label: "判断题", value: "判断题" },
  { label: "单选题", value: "单选题" },
  { label: "简答题", value: "简答题" },
  { label: "编程题", value: "编程题" }
];

// 方法
function initKnowledgeOptions(questions: Question[]) {
  const knowledgeSet = new Set<string>();
  questions.forEach(q => knowledgeSet.add(q.knowledge));
  knowledgeOptions.value = Array.from(knowledgeSet);
}

async function fetchQuestions() {
  try {
    const response = await getExamList();
    questionBank.value = response.data;
    initKnowledgeOptions(response.data);
  } catch (error) {
    ElMessage.error("获取题库失败");
    console.error(error);
  }
}

function startExam() {
  if (!examConfig.value.selectedTypes.length) {
    ElMessage.warning("请至少选择一种题型");
    return;
  }
  if (!examConfig.value.knowledge.length) {
    ElMessage.warning("请至少选择一个知识点");
    return;
  }

  examQuestions.value = [];
  userAnswers.value = {};
  showAnswers.value = false;
  showScore.value = false;
  currentPage.value = 1;

  const filtered = questionBank.value.filter(q => examConfig.value.selectedTypes.includes(q.type) && examConfig.value.knowledge.includes(q.knowledge));

  examConfig.value.selectedTypes.forEach(type => {
    const typeQuestions = filtered.filter(q => q.type === type);
    const count = examConfig.value.typeCounts[type];
    const shuffled = [...typeQuestions].sort(() => 0.5 - Math.random());
    examQuestions.value.push(...shuffled.slice(0, count));
  });

  examQuestions.value = examQuestions.value.sort(() => 0.5 - Math.random());

  if (!examQuestions.value.length) {
    ElMessage.warning("没有找到符合条件的题目");
    return;
  }

  // 打乱所有单选题选项并记录新答案
  examQuestions.value.forEach(question => {
    if (question.type === "单选题" && examConfig.value.shuffleOptions) {
      const options = question.option;
      const rawOptions = [
        { key: "A", label: options?.opt_a || "" },
        { key: "B", label: options?.opt_b || "" },
        { key: "C", label: options?.opt_c || "" },
        { key: "D", label: options?.opt_d || "" }
      ];
      const shuffled = [...rawOptions].sort(() => 0.5 - Math.random());
      const newOption: Record<string, string> = {};
      let newCorrectAnswer = "";
      shuffled.forEach((item, index) => {
        const letter = String.fromCharCode(65 + index); // A=65, B=66...
        newOption[letter] = item.label;
        if (item.key === question.answer) {
          newCorrectAnswer = letter;
        }
      });
      question.shuffledOption = newOption;
      question.shuffledAnswer = newCorrectAnswer;
    } else {
      const options = question.option;
      question.shuffledOption = {
        A: options?.opt_a || "",
        B: options?.opt_b || "",
        C: options?.opt_c || "",
        D: options?.opt_d || ""
      };
      question.shuffledAnswer = question.answer;
    }
  });

  remainingTime.value = examConfig.value.timeLimit * 60;
  if (timer.value) clearInterval(timer.value);
  timer.value = setInterval(() => {
    remainingTime.value--;
    if (remainingTime.value <= 0) finishExam();
  }, 1000);

  examDialogVisible.value = true;
}

function shuffledOptions(question: Question) {
  return question.shuffledOption || {};
}

function submitAnswer() {
  if (!showAnswers.value) {
    if (currentQuestion.value.type === "判断题" || currentQuestion.value.type === "单选题") {
      showAnswers.value = true;
      activeCollapse.value = [currentQuestion.value.id];
    } else {
      showAnswers.value = true;
      activeCollapse.value = [currentQuestion.value.id];
    }
  } else {
    showAnswers.value = false;
    if (currentPage.value < examQuestions.value.length) {
      currentPage.value++;
    } else {
      finishExam();
    }
  }
}

function finishExam() {
  if (timer.value) clearInterval(timer.value);
  calculateScore();
  showScore.value = true;
  ElMessageBox.alert(`考试结束! 你的得分是: ${totalScore.value}分`, "考试结果", {
    confirmButtonText: "确定"
  });
  examDialogVisible.value = false;
}

function calculateScore() {
  const typeStats: Record<string, { count: number; correct: number }> = {};
  examConfig.value.selectedTypes.forEach(type => {
    typeStats[type] = { count: 0, correct: 0 };
  });

  examQuestions.value.forEach(question => {
    typeStats[question.type].count++;
    if (question.type === "判断题" || question.type === "单选题") {
      if (userAnswers.value[question.id] === question.shuffledAnswer) {
        typeStats[question.type].correct++;
      }
    }
  });

  scoreData.value = examConfig.value.selectedTypes.map(type => {
    let score = 0;
    if (type === "判断题") score = typeStats[type].correct * 5;
    if (type === "单选题") score = typeStats[type].correct * 10;
    return {
      type,
      count: typeStats[type].count,
      correct: typeStats[type].correct,
      score
    };
  });

  totalScore.value = scoreData.value.reduce((sum, item) => sum + item.score, 0);
  const totalQ = scoreData.value.reduce((sum, item) => sum + item.count, 0);
  const totalC = scoreData.value.reduce((sum, item) => sum + item.correct, 0);
  correctRate.value = Math.round((totalC / totalQ) * 100);
}

function cleanup() {
  if (timer.value) clearInterval(timer.value);
}

onBeforeUnmount(() => {
  cleanup();
});

onMounted(() => {
  fetchQuestions();
});
</script>

<template>
  <div>
    <!-- 考试设置表单 -->
    <el-form :model="examConfig" label-width="120px" class="exam-config-form">
      <h3>考试设置</h3>
      <el-form-item label="考试时间(分钟)">
        <el-input-number v-model="examConfig.timeLimit" :min="1" :max="30" />
      </el-form-item>
      <el-form-item label="知识点">
        <el-select v-model="examConfig.knowledge" multiple filterable allow-create default-first-option placeholder="选择或输入知识点" style="width: 300px">
          <el-option v-for="item in knowledgeOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="题型设置">
        <el-checkbox-group v-model="examConfig.selectedTypes">
          <div v-for="(type, index) in questionTypes" :key="type.value" class="question-type-item">
            <el-checkbox :label="type.value" :value="type.value">
              {{ type.label }}
            </el-checkbox>
            <el-input-number v-model="examConfig.typeCounts[type.value]" :min="0" :max="10" :disabled="!examConfig.selectedTypes.includes(type.value)" />
            <span class="type-label">{{ type.label }}</span>
          </div>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="startExam">开始考试</el-button>
      </el-form-item>
    </el-form>

    <div class="exam-score" v-if="showScore">
      <h3>考试成绩</h3>
      <el-table :data="scoreData" border style="width: 100%">
        <el-table-column prop="type" label="题型" />
        <el-table-column prop="count" label="题数" />
        <el-table-column prop="correct" label="正确" />
        <el-table-column prop="score" label="得分" />
      </el-table>
      <div class="total-score">
        <p>总分: {{ totalScore }} 分</p>
        <p>正确率: {{ correctRate }}%</p>
      </div>
    </div>

    <!-- 考试对话框 -->
    <el-dialog v-model="examDialogVisible" :title="`考试中 - ${remainingTimeDisplay}`" :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false">
      <div class="exam-content">
        <div class="exam-questions">
          <el-pagination v-model:current-page="currentPage" :page-size="1" :total="examQuestions.length" layout="prev, pager, next" hide-on-single-page />
          <div v-for="(question, index) in currentPageQuestions" :key="question.id" class="question-item">
            <div class="question-header">
              <span class="question-type">{{ question.type }}</span>
              <span class="question-index">第 {{ index + 1 }} 题</span>
            </div>
            <div class="question-content">
              <p>{{ question.question }}</p>
              <!-- 单选题 -->
              <div v-if="question.type === '单选题'" class="single-choice">
                <el-radio-group v-model="userAnswers[question.id]">
                  <el-radio v-for="(option, key) in shuffledOptions(question)" :key="key" :value="key" class="option-item"> {{ key }}. {{ option }} </el-radio>
                </el-radio-group>
              </div>
              <!-- 判断题 -->
              <div v-if="question.type === '判断题'" class="judgement">
                <el-radio-group v-model="userAnswers[question.id]">
                  <el-radio value="正确" class="option-item">正确</el-radio>
                  <el-radio value="错误" class="option-item">错误</el-radio>
                </el-radio-group>
              </div>
              <!-- 简答题 -->
              <div v-if="question.type === '简答题'" class="short-answer">
                <el-input v-model="userAnswers[question.id]" type="textarea" :rows="4" placeholder="请输入答案" />
              </div>
              <!-- 编程题 -->
              <div v-if="question.type === '编程题'" class="programming">
                <el-input v-model="userAnswers[question.id]" type="textarea" :rows="8" placeholder="请输入代码" />
              </div>
              <!-- 答案和解析 -->
              <div v-if="showAnswers && userAnswers[question.id]" class="answer-section">
                <el-collapse v-model="activeCollapse">
                  <el-collapse-item :title="`${question.type}答案`" :name="question.id">
                    <div v-if="question.type === '单选题' || question.type === '判断题'">
                      <p>你的答案: {{ userAnswers[question.id] }}</p>
                      <p>正确答案: {{ question.shuffledAnswer }}</p>
                      <p v-if="question.type === '单选题'">解析: {{ question.analysis }}</p>
                    </div>
                    <div v-else>
                      <p>参考答案:</p>
                      <pre v-if="question.type === '编程题'">{{ question.answer }}</pre>
                      <p v-else>{{ question.answer }}</p>
                      <p>解析: {{ question.analysis }}</p>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </div>
        </div>
        <div class="exam-controls">
          <el-button type="primary" @click="submitAnswer" :disabled="!userAnswers[currentQuestion?.id]">
            {{ showAnswers ? "下一题" : "提交答案" }}
          </el-button>
          <el-button type="danger" @click="finishExam" v-if="currentPage === examQuestions.length"> 结束考试 </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
/* 保持原有样式不变 */
.exam-container {
  padding: 10px;
}
.exam-config-form {
  padding: 10px;
  margin: 0 auto;
  background-color: var(--el-bg-color);
}
.question-type-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.question-type-item .el-input-number {
  margin: 0 10px;
}
.type-label {
  margin-right: 15px;
  min-width: 60px;
}
.exam-content {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 450px);
}
.exam-questions {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px;
}
.question-item {
  margin-bottom: 20px;
}
.question-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}
.question-type {
  font-weight: bold;
  color: #409eff;
}
.question-index {
  color: #666;
}
.option-item {
  display: block;
  margin: 10px 10px;
}
.answer-section {
  margin-top: 20px;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
}
.exam-controls {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
.exam-score {
  margin-top: 30px;
  padding: 20px;
  background-color: var(--el-bg-color);
  border-radius: 4px;
}
.total-score {
  margin-top: 20px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
}
.total-score p {
  margin: 5px 0;
}
</style>
