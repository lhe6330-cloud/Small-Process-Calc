<template>
  <el-form :model="form" label-width="120px">
    <el-card class="form-card">
      <template #header><span class="card-title">⚡ 涡轮发电机组</span></template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="介质类型">
            <el-select v-model="form.turbine_in.medium_type" placeholder="选择" @change="onMediumTypeChange('turbine_in')">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6" v-if="form.turbine_in.medium_type === 'single'">
          <el-form-item label="介质">
            <el-select v-model="form.turbine_in.medium" @change="onMediumChange('turbine_in')">
              <el-option label="N₂" value="N2"/>
              <el-option label="O₂" value="O2"/>
              <el-option label="Air" value="Air"/>
              <el-option label="CO₂" value="CO2"/>
              <el-option label="H₂" value="H2"/>
              <el-option label="H₂O" value="H2O"/>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="入口压力 (MPa.G)">
            <el-input-number v-model="form.turbine_in.p_in" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="入口温度 (°C)">
            <el-input-number v-model="form.turbine_in.t_in" :min="-273" :step="10" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="流量">
            <el-input-number v-model="form.turbine_in.flow_rate" :min="0" />
            <el-select v-model="form.turbine_in.flow_unit" style="width:90px;margin-left:5px;">
              <el-option label="T/h" value="T/h"/>
              <el-option label="Nm³/h" value="Nm3/h"/>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="出口压力 (MPa.G)">
            <el-input-number v-model="form.turbine_params.p_out" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="绝热效率 (%)">
            <el-input-number v-model="form.turbine_params.adiabatic_efficiency" :min="0" :max="100" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 混合介质组分输入 -->
      <div v-if="form.turbine_in.medium_type === 'mix'">
        <MixCompositionInput 
          v-model="form.turbine_in.mixData"
        />
      </div>
    </el-card>
    
    <el-button type="primary" size="large" @click="submit" :loading="loading" style="margin-top:20px;width:200px;">🚀 开始计算</el-button>
  </el-form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'
import MixCompositionInput from '../common/MixCompositionInput.vue'

const emit = defineEmits(['calculate'])
const loading = ref(false)

const form = reactive({
  turbine_in: { 
    medium_type: 'single', 
    medium: 'N2', 
    mixData: { composition: { N2: 0, O2: 0, H2: 0, CO2: 0, H2O: 0 }, composition_type: 'mole' },
    flow_rate: 1000, 
    flow_unit: 'Nm3/h', 
    p_in: 0.6, 
    p_out: 0.3, 
    t_in: 250 
  },
  turbine_params: { p_out: 0.3, adiabatic_efficiency: 85 }
})

// 水/水蒸气时自动切换流量单位
function onMediumChange(side) {
  const medium = form[side].medium
  if (medium === 'H2O') {
    form[side].flow_unit = 'T/h'
  } else if (form[side].flow_unit === 'T/h') {
    form[side].flow_unit = 'Nm3/h'
  }
}

// 介质类型切换时初始化
function onMediumTypeChange(side) {
  if (form[side].medium_type === 'mix' && form[side].medium === 'H2O') {
    form[side].flow_unit = 'T/h'
  } else if (form[side].medium_type === 'single') {
    onMediumChange(side)
  }
}

const submit = async () => {
  // 校验混合介质组分
  if (form.turbine_in.medium_type === 'mix') {
    const total = Object.values(form.turbine_in.mixData.composition).reduce((a, b) => a + b, 0)
    if (Math.abs(total - 100) > 0.01) {
      alert('涡轮入口混合介质组分合计不为 100%，请先点击归一化按钮')
      return
    }
  }

  // H2O 介质入口温度预校验
  if (form.turbine_in.medium_type === 'single' && form.turbine_in.medium === 'H2O') {
    loading.value = true
    try {
      // 调用后端 API 获取饱和温度
      const p_abs = form.turbine_in.p_in + 0.101325  // MPa.G → MPa.A
      const satRes = await axios.get('http://localhost:8000/api/thermo/water/saturation', { params: { p: p_abs } })
      const t_sat = satRes.data.saturation_temp

      if (form.turbine_in.t_in <= t_sat) {
        alert(`⚠️ 涡轮入口温度过低！\n\n当前温度：${form.turbine_in.t_in}°C\n饱和温度：${t_sat.toFixed(2)}°C\n\n请确保入口为过热蒸汽状态（入口温度需高于饱和温度）。`)
        loading.value = false
        return
      }
    } catch (e) {
      // 如果 API 调用失败，继续让后端校验
      console.warn('获取饱和温度失败，继续提交给后端校验')
    }
  }

  loading.value = true
  try {
    // 构建请求数据
    const turbineInData = form.turbine_in.medium_type === 'single'
      ? {
          medium_type: 'single',
          medium: form.turbine_in.medium,
          flow_rate: form.turbine_in.flow_rate,
          flow_unit: form.turbine_in.flow_unit,
          p_in: form.turbine_in.p_in,
          p_out: form.turbine_params.p_out,
          t_in: form.turbine_in.t_in
        }
      : {
          medium_type: 'mix',
          mix_composition: form.turbine_in.mixData.composition,
          composition_type: form.turbine_in.mixData.composition_type,
          flow_rate: form.turbine_in.flow_rate,
          flow_unit: form.turbine_in.flow_unit,
          p_in: form.turbine_in.p_in,
          p_out: form.turbine_params.p_out,
          t_in: form.turbine_in.t_in
        }

    const inputData = {
      turbine_in: turbineInData,
      turbine_params: { ...form.turbine_params }
    }

    // 保存输入数据到 localStorage 供导出使用
    localStorage.setItem('lastInputData_mode3', JSON.stringify(inputData))

    const res = await axios.post('/api/calculate/mode3', inputData)

    // 检查后端返回的错误
    if (res.data.error || !res.data.success) {
      alert('⚠️ 计算失败：\n\n' + (res.data.error_message || '请检查输入参数是否合理'))
      loading.value = false
      return
    }

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
