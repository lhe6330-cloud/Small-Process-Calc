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
.main { padding: 20px; max-width: 1400px; margin: 0 auto; }
.content { margin-top: 20px; }
:deep(.el-tabs) { --el-bg-color: #ffffff; --el-text-color-primary: #303133; }
:deep(.el-tabs__item) { color: #666; border: 1px solid #dcdfe6; background: #f5f7fa; }
:deep(.el-tabs__item.is-active) { color: #409EFF; border-color: #409EFF; background: #ffffff; }
:deep(.el-form-item__label) { color: #303133; }
:deep(.el-input__wrapper) { background: #ffffff; border-color: #dcdfe6; }
:deep(.el-input__inner) { color: #303133; }
:deep(.el-button--primary) { background: #409EFF; border-color: #409EFF; }
</style>
