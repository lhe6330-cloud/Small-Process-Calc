<template>
  <div class="mode5-container">
    <h2>⚙️ 涡轮一维通流设计</h2>
    <p class="description">径流式（向心）涡轮的一维设计计算</p>
    
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">📊 涡轮参数（从 {{ activeMode === 'mode1' ? '模式 1' : activeMode === 'mode2' ? '模式 2' : '模式 3' }} - 涡轮膨胀机带入）</span>
          <el-tag type="success">实时同步</el-tag>
        </div>
      </template>
      
      <el-descriptions :column="3" border v-if="turbineParams">
        <el-descriptions-item label="流量">{{ turbineParams.flow_rate }} {{ turbineParams.flow_unit }}</el-descriptions-item>
        <el-descriptions-item label="介质">{{ turbineParams.medium }}</el-descriptions-item>
        <el-descriptions-item label="进口压力">{{ turbineParams.p_in }} MPa.G</el-descriptions-item>
        <el-descriptions-item label="出口压力">{{ turbineParams.p_out }} MPa.G</el-descriptions-item>
        <el-descriptions-item label="进口温度">{{ turbineParams.t_in }} °C</el-descriptions-item>
        <el-descriptions-item label="出口温度">{{ turbineParams.t_out }} °C</el-descriptions-item>
        <el-descriptions-item label="进口密度">{{ turbineParams.rho_in }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="出口密度">{{ turbineParams.rho_out }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="轴功率" :span="2">{{ turbineParams.power_shaft }} kW</el-descriptions-item>
        <el-descriptions-item label="电功率" :span="2">{{ turbineParams.power_electric }} kW</el-descriptions-item>
      </el-descriptions>
      
      <el-empty v-else description="请先进行模式计算" />
    </el-card>
    
    <!-- 设计参数 -->
    <el-card class="design-card" v-if="turbineParams">
      <template #header>
        <span class="card-title">⚙️ 设计参数（可编辑）</span>
      </template>
      
      <el-form :model="designParams" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="* 转速 n">
              <el-input-number v-model="designParams.speedRpm" :min="1000" :max="20000" step="500" />
              <span style="margin-left: 10px">rpm</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="* 叶片数 Z">
              <el-input-number v-model="designParams.bladeCount" :min="9" :max="21" step="1" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="* 速比 u/C₀">
              <el-input-number v-model="designParams.speedRatio" :min="0.6" :max="0.75" :step="0.01" :precision="2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="* 反动度 Ω">
              <el-input-number v-model="designParams.reaction" :min="0" :max="100" step="5" />
              <span style="margin-left: 10px">%</span>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button type="primary" @click="calculateTurbine" :loading="calculating">
            🚀 开始计算
          </el-button>
          <el-button @click="exportPDF" :loading="exporting">📄 导出 PDF</el-button>
          <el-button @click="exportExcel" :loading="exporting">📊 导出 Excel</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 计算结果 -->
    <el-card class="result-card" v-if="turbineResult">
      <template #header>
        <span class="card-title">📊 计算结果</span>
        <el-tag :type="turbineResult.performance?.match ? 'success' : 'warning'">
          {{ turbineResult.performance?.match ? '✅ 验证通过' : '⚠️ 需校核' }}
        </el-tag>
      </template>
      
      <h4>📐 基本尺寸</h4>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="叶轮外径 D₁">{{ turbineResult.dimensions?.D1 }} mm</el-descriptions-item>
        <el-descriptions-item label="叶轮内径 D₂">{{ turbineResult.dimensions?.D2 }} mm</el-descriptions-item>
        <el-descriptions-item label="进口叶片高度 b₁">{{ turbineResult.dimensions?.b1 }} mm</el-descriptions-item>
        <el-descriptions-item label="出口叶片高度 b₂">{{ turbineResult.dimensions?.b2 }} mm</el-descriptions-item>
        <el-descriptions-item label="叶片数 Z" :span="2">{{ turbineResult.dimensions?.Z }}</el-descriptions-item>
      </el-descriptions>
      
      <h4 style="margin-top: 20px">🔺 速度三角形 - 进口</h4>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="C₁">{{ turbineResult.velocity_triangle_in?.C1 }} m/s</el-descriptions-item>
        <el-descriptions-item label="W₁">{{ turbineResult.velocity_triangle_in?.W1 }} m/s</el-descriptions-item>
        <el-descriptions-item label="U₁">{{ turbineResult.velocity_triangle_in?.U1 }} m/s</el-descriptions-item>
        <el-descriptions-item label="α₁">{{ turbineResult.velocity_triangle_in?.alpha1 }}°</el-descriptions-item>
        <el-descriptions-item label="β₁">{{ turbineResult.velocity_triangle_in?.beta1 }}°</el-descriptions-item>
      </el-descriptions>
      
      <h4 style="margin-top: 20px">🔺 速度三角形 - 出口</h4>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="C₂">{{ turbineResult.velocity_triangle_out?.C2 }} m/s</el-descriptions-item>
        <el-descriptions-item label="W₂">{{ turbineResult.velocity_triangle_out?.W2 }} m/s</el-descriptions-item>
        <el-descriptions-item label="U₂">{{ turbineResult.velocity_triangle_out?.U2 }} m/s</el-descriptions-item>
        <el-descriptions-item label="α₂">{{ turbineResult.velocity_triangle_out?.alpha2 }}°</el-descriptions-item>
        <el-descriptions-item label="β₂">{{ turbineResult.velocity_triangle_out?.beta2 }}°</el-descriptions-item>
      </el-descriptions>
      
      <h4 style="margin-top: 20px">🔥 热力参数</h4>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="级效率 η">{{ turbineResult.thermo_params?.eta }}%</el-descriptions-item>
        <el-descriptions-item label="反动度 Ω">{{ turbineResult.thermo_params?.omega }}%</el-descriptions-item>
        <el-descriptions-item label="速比 u/C₀">{{ turbineResult.thermo_params?.speed_ratio }}</el-descriptions-item>
        <el-descriptions-item label="计算功率">{{ turbineResult.performance?.P_calc }} kW</el-descriptions-item>
        <el-descriptions-item label="输入功率">{{ turbineResult.performance?.P_input }} kW</el-descriptions-item>
        <el-descriptions-item label="压降 ΔP">{{ turbineResult.performance?.delta_p }} MPa</el-descriptions-item>
      </el-descriptions>
      
      <el-alert 
        :title="turbineResult.message" 
        type="success"
        :closable="false"
        show-icon
        style="margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps({
  activeMode: {
    type: String,
    default: 'mode1',
  },
  result: {
    type: Object,
    default: null,
  },
})

const calculating = ref(false)
const exporting = ref(false)
const turbineResult = ref(null)

const designParams = reactive({
  speedRpm: 3000,
  bladeCount: 13,
  speedRatio: 0.65,
  reaction: 50,
})

// 从父组件传递的结果中计算涡轮参数
const turbineParams = computed(() => {
  if (!props.result || !props.result.turbine) {
    return null
  }
  
  const turbine = props.result.turbine
  
  // 介质名称转换
  const mediumMap = {
    'H2O': '水/水蒸气',
    'N2': 'N₂',
    'O2': 'O₂',
    'CO2': 'CO₂',
    'H2': 'H₂',
    'Air': '空气',
  }
  const mediumName = mediumMap[turbine.medium || 'N2'] || turbine.medium || 'N₂'
  
  return {
    flow_rate: turbine.flow_rate,
    flow_unit: turbine.flow_unit,
    medium: mediumName,
    p_in: turbine.p_in,
    p_out: turbine.p_out,
    t_in: turbine.t_in,
    t_out: typeof turbine.t_out === 'number' ? parseFloat(turbine.t_out.toFixed(4)) : turbine.t_out,
    rho_in: turbine.rho_in,
    rho_out: turbine.rho_out,
    power_shaft: typeof turbine.power_shaft === 'number' ? parseFloat(turbine.power_shaft.toFixed(4)) : turbine.power_shaft,
    power_electric: turbine.power_electric ? (typeof turbine.power_electric === 'number' ? parseFloat(turbine.power_electric.toFixed(4)) : turbine.power_electric) : null,
  }
})

const calculateTurbine = async () => {
  if (!turbineParams.value) {
    ElMessage.warning('请先进行模式计算')
    return
  }
  
  calculating.value = true
  
  try {
    const response = await fetch('http://localhost:8000/api/calculate/mode5', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: props.activeMode,
        flow_rate: turbineParams.value.flow_rate,
        flow_unit: turbineParams.value.flow_unit,
        p_in: turbineParams.value.p_in,
        p_out: turbineParams.value.p_out,
        t_in: turbineParams.value.t_in,
        t_out: turbineParams.value.t_out,
        rho_in: turbineParams.value.rho_in,
        rho_out: turbineParams.value.rho_out,
        power_shaft: turbineParams.value.power_shaft,
        speed_rpm: designParams.speedRpm,
        blade_count: designParams.bladeCount,
        speed_ratio: designParams.speedRatio,
        reaction: designParams.reaction,
      }),
    })
    
    const data = await response.json()
    if (data.success) {
      turbineResult.value = data
      ElMessage.success('涡轮一维设计计算完成')
    } else {
      ElMessage.error('计算失败：' + (data.detail || data.message))
    }
  } catch (e) {
    ElMessage.error('请求失败：' + e.message)
  } finally {
    calculating.value = false
  }
}

const exportPDF = async () => {
  if (!turbineParams.value) {
    ElMessage.warning('请先进行模式计算')
    return
  }
  
  exporting.value = true
  try {
    const response = await fetch('http://localhost:8000/api/export/pdf/mode5', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: props.activeMode,
        flow_rate: turbineParams.value.flow_rate,
        flow_unit: turbineParams.value.flow_unit,
        p_in: turbineParams.value.p_in,
        p_out: turbineParams.value.p_out,
        t_in: turbineParams.value.t_in,
        t_out: turbineParams.value.t_out,
        rho_in: turbineParams.value.rho_in,
        rho_out: turbineParams.value.rho_out,
        power_shaft: turbineParams.value.power_shaft,
        speed_rpm: designParams.speedRpm,
        blade_count: designParams.bladeCount,
        speed_ratio: designParams.speedRatio,
        reaction: designParams.reaction,
      }),
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `turbine_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('PDF 导出成功')
    } else {
      ElMessage.error('导出失败')
    }
  } catch (e) {
    ElMessage.error('导出失败：' + e.message)
  } finally {
    exporting.value = false
  }
}

const exportExcel = async () => {
  if (!turbineParams.value) {
    ElMessage.warning('请先进行模式计算')
    return
  }
  
  exporting.value = true
  try {
    const response = await fetch('http://localhost:8000/api/export/excel/mode5', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: props.activeMode,
        flow_rate: turbineParams.value.flow_rate,
        flow_unit: turbineParams.value.flow_unit,
        p_in: turbineParams.value.p_in,
        p_out: turbineParams.value.p_out,
        t_in: turbineParams.value.t_in,
        t_out: turbineParams.value.t_out,
        rho_in: turbineParams.value.rho_in,
        rho_out: turbineParams.value.rho_out,
        power_shaft: turbineParams.value.power_shaft,
        speed_rpm: designParams.speedRpm,
        blade_count: designParams.bladeCount,
        speed_ratio: designParams.speedRatio,
        reaction: designParams.reaction,
      }),
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `turbine_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('Excel 导出成功')
    } else {
      ElMessage.error('导出失败')
    }
  } catch (e) {
    ElMessage.error('导出失败：' + e.message)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.mode5-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: 600; color: #F1F5F9; }
.form-card, .data-card, .design-card, .result-card { margin-bottom: 20px; }
h4 { color: #F1F5F9; margin: 15px 0 10px 0; font-size: 16px; }
</style>
