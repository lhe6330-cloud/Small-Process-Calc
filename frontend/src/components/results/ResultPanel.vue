<template>
  <el-card class="result-card" v-if="result">
    <template #header><span class="card-title">📊 计算结果</span></template>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-statistic title="换热功率 (kW)" :value="result.heat_exchanger?.q_power?.toFixed(2) || 0" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="热边出口温度 (°C)" :value="result.heat_exchanger?.t_hot_out?.toFixed(1) || 0" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="涡轮轴功率 (kW)" :value="result.turbine?.power_shaft?.toFixed(2) || 0" />
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-statistic title="发电功率 (kW)" :value="result.turbine?.power_electric?.toFixed(2) || 0" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="涡轮出口温度 (°C)" :value="result.turbine?.t_out?.toFixed(1) || 0" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="电机选型 (kW)" :value="result.selection?.motor || 0" />
      </el-col>
    </el-row>
    
    <el-divider />
    
    <el-row :gutter="20">
      <el-col :span="8">
        <div class="result-item">
          <div class="label">进口管道</div>
          <div class="value">DN{{ result.selection?.pipe_inlet?.recommended_dn }} (v={{ result.selection?.pipe_inlet?.velocity?.toFixed(1) }} m/s)</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="result-item">
          <div class="label">出口管道</div>
          <div class="value">DN{{ result.selection?.pipe_outlet?.recommended_dn }} (v={{ result.selection?.pipe_outlet?.velocity?.toFixed(1) }} m/s)</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="result-item">
          <div class="label">阀门</div>
          <div class="value">DN{{ result.selection?.valve?.valve_dn }} (Kv={{ result.selection?.valve?.kv_rated }})</div>
        </div>
      </el-col>
    </el-row>
    
    <el-divider />
    
    <div class="export-actions">
      <el-button type="success" @click="exportPDF" :loading="exporting.pdf">
        📄 导出 PDF
      </el-button>
      <el-button type="warning" @click="exportExcel" :loading="exporting.excel">
        📊 导出 Excel
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps(['result'])
const emitting = defineEmits(['calculate'])

const exporting = ref({ pdf: false, excel: false })

// 获取当前激活的模式（从 URL 或父组件传递）
const getCurrentMode = () => {
  // 简单实现：检查哪个 localStorage 有数据
  if (localStorage.getItem('lastInputData_mode3')) return 'mode3'
  if (localStorage.getItem('lastInputData_mode2')) return 'mode2'
  return 'mode1'
}

const getInputData = () => {
  const mode = getCurrentMode()
  const savedData = localStorage.getItem(`lastInputData_${mode === 'mode1' ? '' : mode}`)
  return savedData ? JSON.parse(savedData) : null
}

const exportPDF = async () => {
  exporting.value.pdf = true
  try {
    const inputData = getInputData()
    if (!inputData) {
      alert('未找到输入数据，请重新计算')
      return
    }
    
    const mode = getCurrentMode()
    const response = await fetch(`/api/export/pdf/${mode}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputData)
    })
    
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error)
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${mode.toUpperCase()}_PDF_${new Date().getTime()}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    alert('✅ PDF 导出成功！')
  } catch (e) {
    alert('❌ PDF 导出失败：' + e.message)
  } finally {
    exporting.value.pdf = false
  }
}

const exportExcel = async () => {
  exporting.value.excel = true
  try {
    const inputData = getInputData()
    if (!inputData) {
      alert('未找到输入数据，请重新计算')
      return
    }
    
    const mode = getCurrentMode()
    const response = await fetch(`/api/export/excel/${mode}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputData)
    })
    
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error)
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${mode.toUpperCase()}_Excel_${new Date().getTime()}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    alert('✅ Excel 导出成功！')
  } catch (e) {
    alert('❌ Excel 导出失败：' + e.message)
  } finally {
    exporting.value.excel = false
  }
}
</script>

<style scoped>
.result-card { margin-top: 20px; background: #1E293B; border: 1px solid #00FF88; }
.card-title { color: #00FF88; font-weight: bold; }
:deep(.el-card__header) { background: #0F172A; border-bottom: 1px solid #334155; }
:deep(.el-statistic__title) { color: #94A3B8; }
:deep(.el-statistic__content) { color: #00D4FF; font-weight: bold; }
.result-item { padding: 15px; background: #0F172A; border-radius: 8px; text-align: center; }
.label { color: #94A3B8; font-size: 14px; margin-bottom: 8px; }
.value { color: #F1F5F9; font-size: 18px; font-weight: bold; }
.export-actions { display: flex; gap: 10px; justify-content: center; margin-top: 20px; }
</style>
