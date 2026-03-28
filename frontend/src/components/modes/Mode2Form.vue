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

    <el-card class="form-card">
      <template #header><span class="card-title">🔥 换热器 (冷边出口)</span></template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="出口压力 (MPa.G)">
            <el-input-number v-model="form.hx_cold_out.p_out" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="出口温度 (°C)">
            <el-input-number v-model="form.hx_cold_out.t_out" :min="-273" :step="10" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="form-card">
      <template #header><span class="card-title">🔥 换热器 (热边)</span></template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="介质类型">
            <el-select v-model="form.hx_hot.medium_type" placeholder="选择" @change="onMediumTypeChange('hx_hot')">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6" v-if="form.hx_hot.medium_type === 'single'">
          <el-form-item label="介质">
            <el-select v-model="form.hx_hot.medium" @change="onMediumChange('hx_hot')">
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
          <el-form-item label="流量">
            <el-input-number v-model="form.hx_hot.flow_rate" :min="0" />
            <el-select v-model="form.hx_hot.flow_unit" style="width:90px;margin-left:5px;">
              <el-option label="T/h" value="T/h"/>
              <el-option label="Nm³/h" value="Nm3/h"/>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="入口压力 (MPa.G)">
            <el-input-number v-model="form.hx_hot.p_in" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="出口压力 (MPa.G)">
            <el-input-number v-model="form.hx_hot.p_out" :min="-0.1" :step="0.1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="入口温度 (°C)">
            <el-input-number v-model="form.hx_hot.t_in" :min="-273" :step="10" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 混合介质组分输入 -->
      <div v-if="form.hx_hot.medium_type === 'mix'">
        <MixCompositionInput 
          v-model="form.hx_hot.mixData"
        />
      </div>
    </el-card>

    <el-button type="primary" size="large" @click="submit" :loading="loading" style="margin-top:20px;width:200px;">🚀 开始计算</el-button>
  </el-form>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import api from '../../api.js'
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
    t_in: 250,
  },
  turbine_params: { p_out: 0.3, adiabatic_efficiency: 85 },
  hx_cold_out: { p_out: 0.28, t_out: 150 },
  hx_hot: {
    medium_type: 'single',
    medium: 'Air',
    mixData: { composition: { N2: 0, O2: 0, H2: 0, CO2: 0, H2O: 0 }, composition_type: 'mole' },
    flow_rate: 800,
    flow_unit: 'Nm3/h',
    p_in: 0.4,
    p_out: 0.35,
    t_in: 200
  }
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
  if (form.hx_hot.medium_type === 'mix') {
    const total = Object.values(form.hx_hot.mixData.composition).reduce((a, b) => a + b, 0)
    if (Math.abs(total - 100) > 0.01) {
      alert('换热器热边混合介质组分合计不为 100%，请先点击归一化按钮')
      return
    }
  }

  // H2O 介质入口温度预校验
  if (form.turbine_in.medium_type === 'single' && form.turbine_in.medium === 'H2O') {
    loading.value = true
    try {
      // 调用后端 API 获取饱和温度
      const p_abs = form.turbine_in.p_in + 0.101325  // MPa.G → MPa.A
      const satRes = await api.get('/thermo/water/saturation', { params: { p: p_abs } })
      const t_sat = satRes.saturation_temp

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

    const hxHotData = form.hx_hot.medium_type === 'single'
      ? {
          medium_type: 'single',
          medium: form.hx_hot.medium,
          flow_rate: form.hx_hot.flow_rate,
          flow_unit: form.hx_hot.flow_unit,
          p_in: form.hx_hot.p_in,
          p_out: form.hx_hot.p_out,
          t_in: form.hx_hot.t_in
        }
      : {
          medium_type: 'mix',
          mix_composition: form.hx_hot.mixData.composition,
          composition_type: form.hx_hot.mixData.composition_type,
          flow_rate: form.hx_hot.flow_rate,
          flow_unit: form.hx_hot.flow_unit,
          p_in: form.hx_hot.p_in,
          p_out: form.hx_hot.p_out,
          t_in: form.hx_hot.t_in
        }

    const inputData = {
      turbine_in: turbineInData,
      turbine_params: { ...form.turbine_params },
      hx_cold_out: { ...form.hx_cold_out },
      hx_hot: hxHotData
    }

    // 保存输入数据到 localStorage 供导出使用和持久化
    localStorage.setItem('lastInputData_mode2', JSON.stringify(inputData))
    localStorage.setItem('mode2_input', JSON.stringify(inputData)) // 持久化输入数据

    console.log('[Mode2] Sending API request to /api/calculate/mode2')
    const res = await api.post('/calculate/mode2', inputData)

    console.log('[Mode2] API response:', res)

    // 检查后端返回的错误
    if (res?.error || !res?.success) {
      alert('⚠️ 计算失败：\n\n' + (res?.error_message || '请检查输入参数是否合理'))
      loading.value = false
      return
    }

    // 保存完整的计算结果（输入 + 输出）供其他模块使用
    const fullResultData = {
      ...inputData,
      turbine: {
        ...inputData.turbine_in,  // 涡轮入口参数
        p_out: inputData.turbine_params.p_out,  // 涡轮出口压力
        ...res  // 合并后端返回的涡轮计算结果
      }
    }
    localStorage.setItem('lastInputData_mode2', JSON.stringify(fullResultData))

    emit('calculate', res)
  } catch (e) {
    console.error('[Mode2] Calculation error:', e)
    const errorMsg = e?.userMessage || e?.message || '未知错误'
    emit('calculate', {
      error: true,
      error_message: errorMsg + ' (详情请在浏览器控制台查看 F12)'
    })
  } finally {
    loading.value = false
  }
}

// 组件挂载时从 localStorage 读取数据
onMounted(() => {
  const storedData = localStorage.getItem('mode2_input')
  if (storedData) {
    try {
      const parsed = JSON.parse(storedData)
      // 恢复涡轮入口数据
      if (parsed.turbine_in) {
        const turbineIn = parsed.turbine_in
        form.turbine_in.medium_type = turbineIn.medium_type || 'single'
        form.turbine_in.medium = turbineIn.medium || 'N2'
        form.turbine_in.flow_rate = turbineIn.flow_rate || 1000
        form.turbine_in.flow_unit = turbineIn.flow_unit || 'Nm3/h'
        form.turbine_in.p_in = turbineIn.p_in || 0.6
        form.turbine_in.t_in = turbineIn.t_in || 250
        if (turbineIn.mix_composition) {
          form.turbine_in.mixData = { composition: turbineIn.mix_composition, composition_type: turbineIn.composition_type || 'mole' }
        }
      }
      // 恢复涡轮参数
      if (parsed.turbine_params) {
        form.turbine_params.p_out = parsed.turbine_params.p_out || 0.3
        form.turbine_params.adiabatic_efficiency = parsed.turbine_params.adiabatic_efficiency || 85
      }
      // 恢复冷边出口数据
      if (parsed.hx_cold_out) {
        form.hx_cold_out.p_out = parsed.hx_cold_out.p_out || 0.28
        form.hx_cold_out.t_out = parsed.hx_cold_out.t_out || 150
      }
      // 恢复热边数据
      if (parsed.hx_hot) {
        const hxHot = parsed.hx_hot
        form.hx_hot.medium_type = hxHot.medium_type || 'single'
        form.hx_hot.medium = hxHot.medium || 'Air'
        form.hx_hot.flow_rate = hxHot.flow_rate || 800
        form.hx_hot.flow_unit = hxHot.flow_unit || 'Nm3/h'
        form.hx_hot.p_in = hxHot.p_in || 0.4
        form.hx_hot.p_out = hxHot.p_out || 0.35
        form.hx_hot.t_in = hxHot.t_in || 200
        if (hxHot.mix_composition) {
          form.hx_hot.mixData = { composition: hxHot.mix_composition, composition_type: hxHot.composition_type || 'mole' }
        }
      }
    } catch (e) {
      console.error('读取历史数据失败', e)
    }
  }
})
</script>

<style scoped>
.form-card { margin-bottom: 20px; background: #ffffff; border: 1px solid #dcdfe6; }
.card-title { color: #303133; font-weight: bold; }
:deep(.el-card__header) { background: #f5f7fa; border-bottom: 1px solid #dcdfe6; }
</style>
