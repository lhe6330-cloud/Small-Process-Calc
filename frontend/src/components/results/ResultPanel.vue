<template>
  <el-card class="result-card" v-if="result">
    <template #header><span class="card-title">📊 计算结果</span></template>

    <!-- 错误提示 -->
    <el-alert
      v-if="result.error"
      title="⚠️ 程序计算错误，没有得到解"
      type="error"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    >
      <template #default>
        <p>{{ result.error_message || '请检查输入参数是否合理，或尝试调整参数范围。' }}</p>
      </template>
    </el-alert>

    <el-row :gutter="20" v-if="!result.error">
      <!-- 模式 1 和模式 2 才有换热器 -->
      <template v-if="activeMode === 'mode1' || activeMode === 'mode2'">
        <el-col :span="8">
          <el-statistic title="换热功率 (kW)" :value="result.heat_exchanger?.q_power?.toFixed(2) || 0" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="热边出口温度 (°C)" :value="result.heat_exchanger?.t_hot_out?.toFixed(1) || 0" />
        </el-col>
      </template>
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
        <el-statistic title="出口含液率 (%)" :value="result.turbine?.liquid_percent !== null ? result.turbine.liquid_percent.toFixed(1) : '--'" :value-style="result.turbine?.liquid_percent > 5 ? { color: '#ff9800' } : {}" />
      </el-col>
    </el-row>

    <!-- 出口含液率警告 -->
    <el-alert
      v-if="result.turbine?.liquid_warning"
      :title="result.turbine.liquid_warning"
      type="warning"
      :closable="false"
      show-icon
      style="margin-top: 15px"
    />

    <el-row :gutter="20" style="margin-top: 15px;">
      <el-col :span="8">
        <el-statistic title="电机选型 (kW)" :value="result.selection?.motor || 0" />
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
import { ElMessage } from 'element-plus'

const props = defineProps(['result', 'activeMode'])

const exporting = ref({ pdf: false, excel: false })

// 导出 PDF
const exportPDF = async () => {
  exporting.value.pdf = true

  try {
    const mode = props.activeMode
    const storageKey = 'lastInputData_' + mode
    const inputData = localStorage.getItem(storageKey)
    const input = inputData ? JSON.parse(inputData) : null

    if (!input) {
      ElMessage.error('未找到输入数据，请先进行计算')
      return
    }

    const response = await fetch(`/api/export/pdf/${mode}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error)
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${mode.toUpperCase()}_${new Date().getTime()}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElMessage.success('✅ PDF 导出成功')
  } catch (e) {
    ElMessage.error('❌ PDF 导出失败：' + e.message)
  } finally {
    exporting.value.pdf = false
  }
}

// 导出 Excel
const exportExcel = async () => {
  exporting.value.excel = true

  try {
    const mode = props.activeMode
    const storageKey = 'lastInputData_' + mode
    const inputData = localStorage.getItem(storageKey)
    const input = inputData ? JSON.parse(inputData) : null

    if (!input) {
      ElMessage.error('未找到输入数据，请先进行计算')
      return
    }

    const response = await fetch(`/api/export/excel/${mode}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error)
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${mode.toUpperCase()}_${new Date().getTime()}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElMessage.success('✅ Excel 导出成功')
  } catch (e) {
    ElMessage.error('❌ Excel 导出失败：' + e.message)
  } finally {
    exporting.value.excel = false
  }
}
</script>

<style scoped>
.result-card { margin-bottom: 20px; background: #ffffff; border: 1px solid #dcdfe6; }
.card-title { font-weight: 600; color: #303133; }
.export-actions { display: flex; gap: 10px; flex-wrap: wrap; }
</style>
