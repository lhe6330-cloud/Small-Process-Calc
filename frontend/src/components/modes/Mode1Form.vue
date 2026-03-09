<template>
  <el-form :model="form" label-width="120px" size="default">
    <el-card class="form-card">
      <template #header><span class="card-title">🔥 换热器冷边</span></template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="介质类型">
            <el-select v-model="form.cold.medium_type" placeholder="选择">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8" v-if="form.cold.medium_type === 'single'">
          <el-form-item label="介质">
            <el-select v-model="form.cold.medium">
              <el-option label="氮气 (N₂)" value="N2" />
              <el-option label="氧气 (O₂)" value="O2" />
              <el-option label="空气" value="Air" />
              <el-option label="二氧化碳" value="CO2" />
              <el-option label="氢气" value="H2" />
              <el-option label="水/水蒸气" value="H2O" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="流量">
            <el-input-number v-model="form.cold.flow_rate" :min="0" :step="100" />
            <el-select v-model="form.cold.flow_unit" style="width: 100px; margin-left: 10px;">
              <el-option label="T/h" value="T/h" />
              <el-option label="Nm³/h" value="Nm3/h" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="入口压力 (MPa.G)">
            <el-input-number v-model="form.cold.p_in" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="出口压力 (MPa.G)">
            <el-input-number v-model="form.cold.p_out" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="入口温度 (°C)">
            <el-input-number v-model="form.cold.t_in" :min="-273" :step="10" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="出口温度 (°C)">
            <el-input-number v-model="form.cold.t_out" :min="-273" :step="10" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="form-card">
      <template #header><span class="card-title">🔥 换热器热边</span></template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="介质类型">
            <el-select v-model="form.hot.medium_type" placeholder="选择">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8" v-if="form.hot.medium_type === 'single'">
          <el-form-item label="介质">
            <el-select v-model="form.hot.medium">
              <el-option label="氮气 (N₂)" value="N2" />
              <el-option label="氧气 (O₂)" value="O2" />
              <el-option label="空气" value="Air" />
              <el-option label="二氧化碳" value="CO2" />
              <el-option label="氢气" value="H2" />
              <el-option label="水/水蒸气" value="H2O" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="流量">
            <el-input-number v-model="form.hot.flow_rate" :min="0" :step="0.1" />
            <el-select v-model="form.hot.flow_unit" style="width: 100px; margin-left: 10px;">
              <el-option label="T/h" value="T/h" />
              <el-option label="Nm³/h" value="Nm3/h" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="入口压力 (MPa.G)">
            <el-input-number v-model="form.hot.p_in" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="出口压力 (MPa.G)">
            <el-input-number v-model="form.hot.p_out" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="入口温度 (°C)">
            <el-input-number v-model="form.hot.t_in" :min="-273" :step="10" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="form-card">
      <template #header><span class="card-title">⚡ 涡轮发电机组</span></template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="出口压力 (MPa.G)">
            <el-input-number v-model="form.turbine.p_out" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="绝热效率 (%)">
            <el-input-number v-model="form.turbine.adiabatic_efficiency" :min="0" :max="100" :step="1" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <el-button type="primary" size="large" @click="submit" :loading="loading" style="margin-top: 20px; width: 200px;">
      🚀 开始计算
    </el-button>
  </el-form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['calculate'])
const loading = ref(false)

const form = reactive({
  cold: { medium_type: 'single', medium: 'N2', flow_rate: 1000, flow_unit: 'Nm3/h', p_in: 0.5, p_out: 0.48, t_in: 20, t_out: 200 },
  hot: { medium_type: 'single', medium: 'H2O', flow_rate: 0.5, flow_unit: 'T/h', p_in: 0.6, p_out: 0.55, t_in: 250 },
  turbine: { p_out: 0.1, adiabatic_efficiency: 85 }
})

const submit = async () => {
  loading.value = true
  try {
    // 保存输入数据到 localStorage 供导出使用
    const inputData = {
      cold_side: { ...form.cold },
      hot_side: { ...form.hot },
      turbine: { ...form.turbine }
    }
    localStorage.setItem('lastInputData', JSON.stringify(inputData))
    
    const res = await axios.post('/api/calculate/mode1', inputData)
    emit('calculate', res.data)
  } catch (e) {
    alert('计算失败：' + e.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-card { margin-bottom: 20px; background: #1E293B; border: 1px solid #00D4FF; }
.card-title { color: #00D4FF; font-weight: bold; }
:deep(.el-card__header) { background: #0F172A; border-bottom: 1px solid #334155; }
</style>
