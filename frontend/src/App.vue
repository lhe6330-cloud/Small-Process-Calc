<template>
  <div class="app-container">
    <header class="header">
      <h1>🍮 PDS CALC</h1>
      <span class="subtitle">小型过程系统设计计算软件</span>
    </header>

    <main class="main">
      <el-tabs v-model="activeTab" type="card">
        <el-tab-pane label="模式 1: 先加热再膨胀" name="mode1"></el-tab-pane>
        <el-tab-pane label="模式 2: 先膨胀后回热" name="mode2"></el-tab-pane>
        <el-tab-pane label="模式 3: 直接膨胀" name="mode3"></el-tab-pane>
        <el-tab-pane label="📐 管道计算" name="pipe"></el-tab-pane>
        <el-tab-pane label="🔧 阀门计算" name="valve"></el-tab-pane>
        <el-tab-pane label="📐 分离器计算" name="separator"></el-tab-pane>
        <el-tab-pane label="⚙️ 涡轮一维设计" name="turbine1d"></el-tab-pane>
      </el-tabs>

      <div class="content">
        <!-- 模式表单 -->
        <Mode1Form v-if="activeTab === 'mode1'" @calculate="handleCalculate" />
        <Mode2Form v-else-if="activeTab === 'mode2'" @calculate="handleCalculate" />
        <Mode3Form v-else-if="activeTab === 'mode3'" @calculate="handleCalculate" />

        <!-- 独立计算页面 -->
        <PipeCalculator v-else-if="activeTab === 'pipe'" />
        <ValveCalculator v-else-if="activeTab === 'valve'" />
        <SeparatorCalculator v-else-if="activeTab === 'separator'" />
        <Turbine1dCalculator v-else-if="activeTab === 'turbine1d'" />

        <!-- 结果面板（仅模式 1/2/3 显示） -->
        <ResultPanel v-if="currentResult && ['mode1', 'mode2', 'mode3'].includes(activeTab)"
          :result="currentResult" :active-mode="activeTab" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Mode1Form from './components/modes/Mode1Form.vue'
import Mode2Form from './components/modes/Mode2Form.vue'
import Mode3Form from './components/modes/Mode3Form.vue'
import ResultPanel from './components/results/ResultPanel.vue'
import PipeCalculator from './components/calculators/PipeCalculator.vue'
import ValveCalculator from './components/calculators/ValveCalculator.vue'
import SeparatorCalculator from './components/calculators/SeparatorCalculator.vue'
import Turbine1dCalculator from './components/calculators/Turbine1dCalculator.vue'

const activeTab = ref('mode1')
const results = ref({
  mode1: null,
  mode2: null,
  mode3: null,
})

const currentResult = computed(() => results.value[activeTab.value])

const handleCalculate = (res) => {
  results.value[activeTab.value] = res
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Microsoft YaHei', sans-serif; background: #ffffff; color: #303133; }
.app-container { min-height: 100vh; background: #ffffff; }
.header { background: #f5f7fa; padding: 20px; text-align: center; border-bottom: 2px solid #dcdfe6; }
.header h1 { color: #303133; font-size: 28px; }
.subtitle { color: #666; font-size: 14px; }
.main { padding: 15px; max-width: 1400px; margin: 0 auto; }
.content { margin-top: 15px; }
:deep(.el-tabs) { --el-bg-color: #ffffff; --el-text-color-primary: #303133; }
:deep(.el-tabs__item) { color: #666; border: 1px solid #dcdfe6; background: #f5f7fa; }
:deep(.el-tabs__item.is-active) { color: #409EFF; border-color: #409EFF; background: #ffffff; }
:deep(.el-form-item__label) { color: #303133; font-size: 13px; }
:deep(.el-input__wrapper) { background: #ffffff; border-color: #dcdfe6; }
:deep(.el-input__inner) { color: #303133; }
:deep(.el-button--primary) { background: #409EFF; border-color: #409EFF; }

/* ========== 紧凑布局样式 - 模式 1/2/3 ========== */
/* 卡片间距缩小 */
.mode-form-card { margin-bottom: 15px; background: #ffffff; border: 1px solid #dcdfe6; }
.mode-form-card :deep(.el-card__header) { padding: 10px 15px; background: #f5f7fa; border-bottom: 1px solid #dcdfe6; }
.mode-form-card :deep(.el-card__body) { padding: 12px; }
.mode-form-card .card-title { color: #303133; font-weight: bold; font-size: 14px; }

/* 表单行紧凑布局 */
.mode-form-row { display: flex; align-items: center; gap: 12px; margin-bottom: 9px; flex-wrap: wrap; }
.mode-form-row.nowrap { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 9px; border-bottom: 1px solid #ebeef5; }
.mode-form-group { display: flex; align-items: center; gap: 8px; }
.mode-form-label { color: #606266; font-size: 13px; width: 70px; text-align: right; }
.mode-form-label.short { width: 50px; }

/* 输入框/下拉框尺寸 - 缩小到 2/3 */
.mode-input-sm { width: 70px; height: 28px; font-size: 13px; }
.mode-input-md { width: 80px; height: 28px; font-size: 13px; }
.mode-input-lg { width: 100px; height: 28px; font-size: 13px; }
.mode-select-sm { width: 90px; height: 28px; font-size: 13px; }
.mode-select-md { width: 100px; height: 28px; font-size: 13px; }
.mode-unit-text { color: #909399; font-size: 13px; min-width: 45px; }

/* 混合介质紧凑输入样式 */
.mode-mix-row { display: flex; align-items: center; gap: 8px; }
.mode-mix-item { display: flex; align-items: center; gap: 4px; }
.mode-mix-item input {
  width: 45px; height: 28px; font-size: 13px; padding: 4px 6px;
  border: 1px solid #dcdfe6; border-radius: 4px; text-align: center;
}
.mode-mix-item input::-webkit-outer-spin-button,
.mode-mix-item input::-webkit-inner-spin-button {
  -webkit-appearance: none; margin: 0;
}
.mode-mix-item input[type=number] { -moz-appearance: textfield; }
.mode-mix-item span { color: #606266; font-size: 13px; min-width: 30px; }
.mode-mix-item .percent { color: #909399; font-size: 13px; min-width: 12px; }
.mode-mix-footer { display: flex; align-items: center; gap: 8px; margin-left: 10px; }
.mode-total-label { color: #606266; font-size: 13px; white-space: nowrap; }
.mode-total-value { font-weight: bold; font-size: 13px; color: #303133; min-width: 45px; }
.mode-normalize-btn {
  background: #409EFF; color: #fff; border: none;
  padding: 5px 10px; border-radius: 4px; font-size: 12px;
  cursor: pointer; height: 28px; white-space: nowrap;
}
.mode-normalize-btn:disabled { background: #a0cfff; cursor: not-allowed; }

/* 分隔线 */
.mode-divider { width: 1px; height: 24px; background: #dcdfe6; margin: 0 8px; }

/* 组分类型单选 */
.mode-radio-label {
  display: inline-flex; align-items: center; gap: 3px;
  cursor: pointer; color: #606266; font-size: 12px; white-space: nowrap;
}
.mode-radio-label input[type="radio"] {
  cursor: pointer; width: 14px; height: 14px; accent-color: #409EFF;
}

/* 计算按钮 */
.mode-calc-btn {
  background: #409EFF; color: #fff; border: none;
  padding: 10px 40px; border-radius: 4px; font-size: 14px;
  cursor: pointer; margin-top: 15px; height: 36px;
}

/* ========== 紧凑布局样式 - 管道/阀门/分离器/涡轮 ========== */
.tool-form-card { margin-bottom: 15px; background: #ffffff; border: 1px solid #dcdfe6; }
.tool-form-card :deep(.el-card__header) { padding: 10px 15px; background: #f5f7fa; border-bottom: 1px solid #dcdfe6; }
.tool-form-card :deep(.el-card__body) { padding: 12px; }
.tool-item { margin-bottom: 15px; }
.tool-card-header { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.tool-card-title { font-weight: 600; color: #303133; font-size: 14px; }

/* el-form 紧凑化 */
.tool-form :deep(.el-form-item__label) { font-size: 13px; }
.tool-form :deep(.el-form-item) { margin-bottom: 12px; }
.tool-form :deep(.el-input-number) { width: 120px; font-size: 13px; }
.tool-form :deep(.el-select) { width: 120px; font-size: 13px; }
.tool-form :deep(.el-radio-group) { display: flex; gap: 10px; }

/* el-descriptions 紧凑化 */
.tool-descriptions :deep(.el-descriptions__label) { font-size: 12px; padding: 8px 12px; }
.tool-descriptions :deep(.el-descriptions__content) { font-size: 13px; padding: 8px 12px; }

/* el-divider 紧凑化 */
.tool-divider { margin: 10px 0; }
.tool-divider :deep(.el-divider__text) { font-size: 13px; font-weight: 600; color: #303133; }

/* 按钮紧凑化 */
.tool-btn { padding: 8px 15px; font-size: 13px; height: 32px; }
.tool-btn :deep(.el-button--small) { padding: 5px 10px; font-size: 12px; height: 28px; }

/* 标题和描述 */
.tool-title { color: #303133; margin-bottom: 8px; font-size: 20px; }
.tool-description { color: #666; margin-bottom: 15px; font-size: 13px; }
</style>
