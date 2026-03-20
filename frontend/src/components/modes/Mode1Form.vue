<template>
  <el-form :model="form" label-width="120px" size="default">
    <el-card class="form-card">
      <template #header><span class="card-title">🔥 换热器冷边</span></template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="介质类型">
            <el-select v-model="form.cold.medium_type" placeholder="选择" @change="onMediumTypeChange('cold')">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8" v-if="form.cold.medium_type === 'single'">
          <el-form-item label="介质">
            <el-select v-model="form.cold.medium" @change="onMediumChange('cold')">
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
      
      <!-- 混合介质组分输入 -->
      <div v-if="form.cold.medium_type === 'mix'">
        <MixCompositionInput 
          v-model="form.cold.mixData"
        />
      </div>
      
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

      <!-- 阀门参数 -->
      <el-row :gutter="20" style="margin-top: 10px; padding-top: 15px; border-top: 1px solid #e4e7ed;">
        <el-col :span="8">
          <el-form-item label="阀门压差 (kPa)">
            <el-input-number v-model="form.cold.valve_dp" :min="1" :max="500" :step="5" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="阀门类型">
            <el-select v-model="form.cold.valve_type">
              <el-option label="蝶阀" value="butterfly" />
              <el-option label="截止阀" value="globe" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="form-card">
      <template #header><span class="card-title">🔥 换热器热边</span></template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="介质类型">
            <el-select v-model="form.hot.medium_type" placeholder="选择" @change="onMediumTypeChange('hot')">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8" v-if="form.hot.medium_type === 'single'">
          <el-form-item label="介质">
            <el-select v-model="form.hot.medium" @change="onMediumChange('hot')">
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
      
      <!-- 混合介质组分输入 -->
      <div v-if="form.hot.medium_type === 'mix'">
        <MixCompositionInput 
          v-model="form.hot.mixData"
        />
      </div>
      
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
import MixCompositionInput from '../common/MixCompositionInput.vue'

const emit = defineEmits(['calculate'])
const loading = ref(false)

const form = reactive({
  cold: {
    medium_type: 'single',
    medium: 'N2',
    mixData: { composition: { N2: 0, O2: 0, H2: 0, CO2: 0, H2O: 0 }, composition_type: 'mole' },
    flow_rate: 1000,
    flow_unit: 'Nm3/h',
    p_in: 0.5,
    p_out: 0.48,
    t_in: 20,
    t_out: 200,
    valve_dp: 30,        // 阀门压差默认值 (kPa)
    valve_type: 'butterfly'  // 阀门类型默认值
  },
  hot: { 
    medium_type: 'single', 
    medium: 'H2O', 
    mixData: { composition: { N2: 0, O2: 0, H2: 0, CO2: 0, H2O: 0 }, composition_type: 'mole' },
    flow_rate: 0.5, 
    flow_unit: 'T/h', 
    p_in: 0.6, 
    p_out: 0.55, 
    t_in: 250 
  },
  turbine: { p_out: 0.1, adiabatic_efficiency: 85 }
})

// 水/水蒸气时自动切换流量单位
function onMediumChange(side) {
  const medium = form[side].medium
  if (medium === 'H2O') {
    form[side].flow_unit = 'T/h'
  } else if (form[side].flow_unit === 'T/h') {
    // 只有当前是 T/h 时才切换回 Nm3/h（避免覆盖用户手动选择）
    form[side].flow_unit = 'Nm3/h'
  }
}

// 介质类型切换时初始化
function onMediumTypeChange(side) {
  if (form[side].medium_type === 'mix' && form[side].medium === 'H2O') {
    // 从 H2O 切换到混合介质时，保持 T/h
    form[side].flow_unit = 'T/h'
  } else if (form[side].medium_type === 'single') {
    // 切换回单一介质时，根据当前介质决定单位
    onMediumChange(side)
  }
}

const submit = async () => {
  // 校验混合介质组分
  if (form.cold.medium_type === 'mix') {
    const total = Object.values(form.cold.mixData.composition).reduce((a, b) => a + b, 0)
    if (Math.abs(total - 100) > 0.01) {
      alert('冷边混合介质组分合计不为 100%，请先点击归一化按钮')
      return
    }
  }
  if (form.hot.medium_type === 'mix') {
    const total = Object.values(form.hot.mixData.composition).reduce((a, b) => a + b, 0)
    if (Math.abs(total - 100) > 0.01) {
      alert('热边混合介质组分合计不为 100%，请先点击归一化按钮')
      return
    }
  }
  
  loading.value = true
  try {
    // 构建请求数据
    const coldData = form.cold.medium_type === 'single' 
      ? { 
          medium_type: 'single', 
          medium: form.cold.medium,
          flow_rate: form.cold.flow_rate,
          flow_unit: form.cold.flow_unit,
          p_in: form.cold.p_in,
          p_out: form.cold.p_out,
          t_in: form.cold.t_in,
          t_out: form.cold.t_out
        }
      : {
          medium_type: 'mix',
          mix_composition: form.cold.mixData.composition,
          composition_type: form.cold.mixData.composition_type,
          flow_rate: form.cold.flow_rate,
          flow_unit: form.cold.flow_unit,
          p_in: form.cold.p_in,
          p_out: form.cold.p_out,
          t_in: form.cold.t_in,
          t_out: form.cold.t_out
        }
    
    const hotData = form.hot.medium_type === 'single'
      ? {
          medium_type: 'single',
          medium: form.hot.medium,
          flow_rate: form.hot.flow_rate,
          flow_unit: form.hot.flow_unit,
          p_in: form.hot.p_in,
          p_out: form.hot.p_out,
          t_in: form.hot.t_in
        }
      : {
          medium_type: 'mix',
          mix_composition: form.hot.mixData.composition,
          composition_type: form.hot.mixData.composition_type,
          flow_rate: form.hot.flow_rate,
          flow_unit: form.hot.flow_unit,
          p_in: form.hot.p_in,
          p_out: form.hot.p_out,
          t_in: form.hot.t_in
        }
    
    const inputData = {
      cold_side: coldData,
      hot_side: hotData,
      turbine: { ...form.turbine }
    }
    
    // 保存输入数据到 localStorage 供导出使用
    localStorage.setItem('lastInputData', JSON.stringify(inputData))
    localStorage.setItem('lastInputData_mode1', JSON.stringify(inputData))
    
    const res = await axios.post('/api/calculate/mode1', inputData)
    
    // 处理后端返回的错误
    if (res.data.error) {
      emit('calculate', res.data)  // 传递错误信息给 ResultPanel 显示
    } else {
      emit('calculate', res.data)
    }
  } catch (e) {
    // 网络错误或其他异常
    emit('calculate', {
      error: true,
      error_message: '网络错误或服务器无响应，请稍后重试。'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-card { margin-bottom: 20px; background: #ffffff; border: 1px solid #dcdfe6; }
.card-title { color: #303133; font-weight: bold; }
:deep(.el-card__header) { background: #f5f7fa; border-bottom: 1px solid #dcdfe6; }
</style>
