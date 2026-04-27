<template>
  <el-form ref="form" label-position="top" label-width="auto">
    <el-row :gutter="20">
      <el-col :span="12">
        <!-- 检索要求分组 -->
        <el-card shadow="never" style="margin-bottom: 10px">
          <template #header>
            <span>检索要求</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="知识图谱检索">
                <el-radio-group v-model="useKnowledgeGraph">
                  <el-radio :value="true">是</el-radio>
                  <el-radio :value="false">否</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item label="知识库RAG检索">
                <el-radio-group v-model="useRag">
                  <el-radio :value="true">是</el-radio>
                  <el-radio :value="false">否</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col :span="12">
        <!-- 输出结果要求分组 -->
        <el-card shadow="never" style="margin-bottom: 10px">
          <template #header>
            <span>输出结果要求</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="输出参考答案">
                <el-radio-group v-model="includeAnswer" class="horizontal-radio-group">
                  <el-radio :value="true">是</el-radio>
                  <el-radio :value="false">否</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item label="输出答案解析" class="horizontal-radio-group">
                <el-radio-group v-model="includeAnalysis">
                  <el-radio :value="true">是</el-radio>
                  <el-radio :value="false">否</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="其他要求">
          <el-select v-model="customRequirementKey" placeholder="请选择项目，右侧填写值" @change="handleChange">
            <el-option v-for="item in customOptions" :key="item.key" :label="item.label" :value="item.key" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item>
          <el-input v-model="customRequirementValue" type="textarea" :autosize="{ minRows: 2, maxRows: 10 }" style="margin-top: 30px" />
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
</template>

<script setup lang="ts">
import { ref, defineProps, defineExpose, computed } from "vue";
const props = defineProps<{
  questionType: string;
}>();
const qtype = computed(() => props.questionType);

const useKnowledgeGraph = ref(false);
const useRag = ref(true);
const includeAnswer = ref(true);
const includeAnalysis = ref(true);

const customRequirementKey = ref("");
const customRequirementValue = ref("");

const customOptions = [{ key: "输出格式要求", label: "输出格式要求" }];

const handleChange = value => {
  if (qtype.value === "判断题") {
    customRequirementValue.value = "输出格式示例：\n" + "【题目】张量是不可变对象\n" + "【答案】正确 \n" + "【解析】张量的值是不可变的。\n";
  }
  if (qtype.value === "单选题") {
    customRequirementValue.value = "输出格式示例：\n" + "【题目】张量的核心特征是什么？\n" + "【选项】 A.一维数组 B.多维数组 C.二进制数据 D.标量值 \n" + "【答案】B \n" + "【解析】张量是多维数组的统称，用于表示任意维度的数据结构，是数学和计算机科学中的基础运算单元。\n";
  }
  if (qtype.value === "简答题") {
    customRequirementValue.value = "输出格式示例：\n" + "【题目】TensorFlow.js的API有几种类型?\n" + "【答案】TensorFlow.js的API有Layers API和Core API两种类型。 \n" + "【解析】Layers API 是高级 API, 提供模块化接口; Core API 是低级 API, 提供张量操作。\n";
  }
  if (qtype.value === "编程题") {
    customRequirementValue.value = "输出格式示例：\n" + "【题目】使用 TensorFlow.js 实现线性回归模型。\n" + "【答案】使用 tf.sequential() 创建模型; 添加一个全连接层，激活函数为 relu。答案需提供代码。 \n" + "【解析】使用TensorFlow.js 训练线性回归模型，预测汽车油耗效率。\n";
  }
};

function getData() {
  return {
    useKnowledgeGraph: useKnowledgeGraph.value,
    useRag: useRag.value,
    includeAnswer: includeAnswer.value,
    includeAnalysis: includeAnalysis.value,
    customRequirementKey: customRequirementKey.value,
    customRequirementValue: customRequirementValue.value
  };
}

defineExpose({ getData });
</script>

<style scoped>
.horizontal-radio-group .el-radio {
  display: inline-block;
  margin-right: 15px;
}
</style>
