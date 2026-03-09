<template>
  <el-form :model="form" label-width="120px">
    <el-card class="form-card">
      <template #header><span class="card-title">⚡ 涡轮发电机组</span></template>
      <el-row :gutter="20">
        <el-col :span="6"><el-form-item label="入口压力 (MPa.G)"><el-input-number v-model="form.turbine_in.p_in" :min="-0.1" :step="0.1" /></el-form-item></el-col>
        <el-col :span="6"><el-form-item label="入口温度 (°C)"><el-input-number v-model="form.turbine_in.t_in" :min="-273" :step="10" /></el-form-item></el-col>
        <el-col :span="6"><el-form-item label="流量"><el-input-number v-model="form.turbine_in.flow_rate" :min="0" /><el-select v-model="form.turbine_in.flow_unit" style="width:90px;margin-left:5px;"><el-option label="T/h" value="T/h"/><el-option label="Nm³/h" value="Nm3/h"/></el-select></el-form-item></el-col>
        <el-col :span="6"><el-form-item label="介质"><el-select v-model="form.turbine_in.medium"><el-option label="N₂" value="N2"/><el-option label="O₂" value="O2"/><el-option label="Air" value="Air"/><el-option label="CO₂" value="CO2"/><el-option label="H₂" value="H2"/><el-option label="H₂O" value="H2O"/></el-select></el-form-item></el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="8"><el-form-item label="出口压力 (MPa.G)"><el-input-number v-model="form.turbine_params.p_out" :min="-0.1" :step="0.1" /></el-form-item></el-col>
        <el-col :span="8"><el-form-item label="绝热效率 (%)"><el-input-number v-model="form.turbine_params.adiabatic_efficiency" :min="0" :max="100" /></el-form-item></el-col>
      </el-row>
    </el-card>
    <el-button type="primary" size="large" @click="submit" :loading="loading" style="margin-top:20px;width:200px;">🚀 开始计算</el-button>
  </el-form>
</template>
<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'
const emit = defineEmits(['calculate'])
const loading = ref(false)
const form = reactive({
  turbine_in: { medium_type: 'single', medium: 'N2', flow_rate: 1000, flow_unit: 'Nm3/h', p_in: 0.6, p_out: 0.3, t_in: 250 },
  turbine_params: { p_out: 0.3, adiabatic_efficiency: 85 }
})
const submit = async () => {
  loading.value = true
  try {
    // 保存输入数据到 localStorage 供导出使用
    const inputData = {
      turbine_in: { ...form.turbine_in },
      turbine_params: { ...form.turbine_params }
    }
    localStorage.setItem('lastInputData_mode3', JSON.stringify(inputData))
    
    const res = await axios.post('/api/calculate/mode3', inputData)
    emit('calculate', res.data)
  } catch (e) { alert('计算失败：' + e.message) }
  finally { loading.value = false }
}
</script>
<style scoped>
.form-card { margin-bottom: 20px; background: #1E293B; border: 1px solid #00D4FF; }
.card-title { color: #00D4FF; font-weight: bold; }
:deep(.el-card__header) { background: #0F172A; border-bottom: 1px solid #334155; }
</style>
