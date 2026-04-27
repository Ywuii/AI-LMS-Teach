<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import * as echarts from "echarts";
import type { EChartsOption } from "echarts";

const props = defineProps<{
  chartData: {
    dates: string[];
    seriesData: Array<{ name: string; data: number[] }>;
  };
}>();

const chartDom = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const initChart = () => {
  if (!chartDom.value) return;

  const option: EChartsOption = {
    tooltip: {
      trigger: "axis"
    },
    legend: {
      data: props.chartData.seriesData.map(item => item.name)
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: props.chartData.dates
    },
    yAxis: {
      type: "value"
    },
    series: props.chartData.seriesData.map(item => ({
      name: item.name,
      type: "line",
      data: item.data
    }))
  };

  if (chart) {
    chart.setOption(option, true); // 更新已有图表配置
  } else {
    chart = echarts.init(chartDom.value);
    chart.setOption(option);
  }
};

// 初始渲染
onMounted(() => {
  initChart();
});

// 监听 chartData 变化，重新绘制图表
watch(
  () => props.chartData,
  () => {
    initChart();
  },
  { deep: true }
);
</script>

<template>
  <div ref="chartDom" style="width: 100%; height: 300px"></div>
</template>
