<template>
  <div class="app-container">
    <header class="header">
      <h1>🍮 PDS CALC</h1>
      <span class="subtitle">小型过程系统设计计算软件</span>
    </header>
    
    <main class="main">
      <el-tabs v-model="activeMode" type="card">
        <el-tab-pane label="模式 1: 先加热再膨胀" name="mode1"></el-tab-pane>
        <el-tab-pane label="模式 2: 先膨胀后回热" name="mode2"></el-tab-pane>
        <el-tab-pane label="模式 3: 直接膨胀" name="mode3"></el-tab-pane>
        <el-tab-pane label="分离器 (V2.0)" name="mode4" disabled></el-tab-pane>
        <el-tab-pane label="一维设计 (V2.0)" name="mode5" disabled></el-tab-pane>
      </el-tabs>
      
      <div class="content">
        <Mode1Form v-if="activeMode === 'mode1'" @calculate="handleCalculate" />
        <Mode2Form v-else-if="activeMode === 'mode2'" @calculate="handleCalculate" />
        <Mode3Form v-else-if="activeMode === 'mode3'" @calculate="handleCalculate" />
        <ResultPanel v-if="result" :result="result" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Mode1Form from './components/modes/Mode1Form.vue'
import Mode2Form from './components/modes/Mode2Form.vue'
import Mode3Form from './components/modes/Mode3Form.vue'
import ResultPanel from './components/results/ResultPanel.vue'

const activeMode = ref('mode1')
const result = ref(null)

const handleCalculate = (res) => {
  result.value = res
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Microsoft YaHei', sans-serif; background: #0F172A; color: #F1F5F9; }
.app-container { min-height: 100vh; }
.header { background: #1E293B; padding: 20px; text-align: center; border-bottom: 2px solid #00D4FF; }
.header h1 { color: #00D4FF; font-size: 28px; }
.subtitle { color: #94A3B8; font-size: 14px; }
.main { padding: 20px; max-width: 1400px; margin: 0 auto; }
.content { margin-top: 20px; }
:deep(.el-tabs) { --el-bg-color: #1E293B; --el-text-color-primary: #F1F5F9; }
:deep(.el-tabs__item) { color: #94A3B8; border: 1px solid #334155; }
:deep(.el-tabs__item.is-active) { color: #00D4FF; border-color: #00D4FF; }
:deep(.el-form-item__label) { color: #F1F5F9; }
:deep(.el-input__wrapper) { background: #0F172A; border-color: #334155; }
:deep(.el-input__inner) { color: #F1F5F9; }
:deep(.el-button--primary) { background: #00D4FF; border-color: #00D4FF; }
</style>
