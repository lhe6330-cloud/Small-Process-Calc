<template>
  <div class="mode-form-container">
    <!-- 涡轮发电机组卡片 -->
    <el-card class="mode-form-card">
      <template #header><span class="card-title">⚡ 涡轮发电机组</span></template>
      <div class="card-body">
        <!-- 第一行：介质类型、介质/组分 -->
        <div class="mode-form-row">
          <div class="mode-form-group">
            <label class="mode-form-label">介质类型</label>
            <el-select v-model="form.turbine_in.medium_type" placeholder="选择" @change="onMediumTypeChange('turbine_in')" class="mode-select-md">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </div>

          <!-- 单一介质时显示介质选择 -->
          <div class="mode-form-group" v-if="form.turbine_in.medium_type === 'single'">
            <label class="mode-form-label short">介质</label>
            <el-select v-model="form.turbine_in.medium" @change="onMediumChange('turbine_in')" class="mode-select-md">
              <el-option label="氮气 (N₂)" value="N2" />
              <el-option label="氧气 (O₂)" value="O2" />
              <el-option label="空气" value="Air" />
              <el-option label="二氧化碳" value="CO2" />
              <el-option label="氢气" value="H2" />
              <el-option label="水/水蒸气" value="H2O" />
            </el-select>
          </div>

          <!-- 混合介质时显示组分类型 + 5 组分 + 合计 + 归一化 -->
          <div class="mode-form-group" v-if="form.turbine_in.medium_type === 'mix'">
            <div class="mode-divider"></div>
            <div class="mode-form-group">
              <span class="mode-form-label" style="width: auto; font-size: 12px;">组分类型：</span>
              <label class="mode-radio-label">
                <input type="radio" v-model="form.turbine_in.mixData.composition_type" value="mole" />
                <span>摩尔</span>
              </label>
              <label class="mode-radio-label">
                <input type="radio" v-model="form.turbine_in.mixData.composition_type" value="mass" />
                <span>质量</span>
              </label>
            </div>
            <div class="mode-divider"></div>
            <div class="mode-mix-row">
              <div class="mode-mix-item" v-for="(value, key) in form.turbine_in.mixData.composition" :key="key">
                <input type="number" v-model.number="form.turbine_in.mixData.composition[key]" :step="key === 'H2O' || key === 'CO2' ? 0.1 : 1" />
                <span>{{ getMediumLabel(key) }}</span>
                <span class="percent">%</span>
              </div>
            </div>
            <div class="mode-mix-footer">
              <span class="mode-total-label">合计：</span>
              <span class="mode-total-value" :style="{ color: totalTurbine !== 100 ? '#f59e0b' : '#22c55e' }">{{ totalTurbine.toFixed(1) }}%</span>
              <button class="mode-normalize-btn" @click="normalizeTurbine" :disabled="totalTurbine === 0 || Math.abs(totalTurbine - 100) < 0.01">🔄</button>
            </div>
          </div>
        </div>

        <!-- 第二行：流量、入口压力、入口温度、出口压力、绝热效率 -->
        <div class="mode-form-row">
          <div class="mode-form-group">
            <label class="mode-form-label short">流量</label>
            <el-input v-model.number="form.turbine_in.flow_rate" type="number" class="mode-input-md" />
            <el-select v-model="form.turbine_in.flow_unit" class="mode-select-sm">
              <el-option label="T/h" value="T/h" />
              <el-option label="Nm³/h" value="Nm3/h" />
            </el-select>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">入口压力</label>
            <el-input v-model.number="form.turbine_in.p_in" type="number" step="0.1" class="mode-input-md" />
            <span class="mode-unit-text">MPa.G</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">入口温度</label>
            <el-input v-model.number="form.turbine_in.t_in" type="number" step="1" class="mode-input-md" />
            <span class="mode-unit-text">°C</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">出口压力</label>
            <el-input v-model.number="form.turbine_params.p_out" type="number" step="0.1" class="mode-input-md" />
            <span class="mode-unit-text">MPa.G</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">绝热效率</label>
            <el-input v-model.number="form.turbine_params.adiabatic_efficiency" type="number" step="1" class="mode-input-md" />
            <span class="mode-unit-text">%</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 计算按钮 -->
    <button class="mode-calc-btn" @click="submit" :disabled="loading">
      🚀 开始计算
    </button>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import api from '../../api.js'

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
  turbine_params: { p_out: 0.3, adiabatic_efficiency: 85 }
})

const mediumLabels = {
  N2: 'N₂',
  O2: 'O₂',
  H2: 'H₂',
  CO2: 'CO₂',
  H2O: 'H₂O'
}

const getMediumLabel = (key) => mediumLabels[key] || key

const totalTurbine = computed(() => {
  return Object.values(form.turbine_in.mixData.composition).reduce((sum, val) => sum + Number(val), 0)
})

const normalizeTurbine = () => {
  if (totalTurbine.value === 0 || Math.abs(totalTurbine.value - 100) < 0.01) return
  const factor = 100 / totalTurbine.value
  for (const key in form.turbine_in.mixData.composition) {
    form.turbine_in.mixData.composition[key] = Math.round(form.turbine_in.mixData.composition[key] * factor * 100) / 100
  }
}

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
    if (Math.abs(totalTurbine.value - 100) > 0.01) {
      alert('涡轮入口混合介质组分合计不为 100%，请先点击归一化按钮')
      return
    }
  }

  // H2O 介质入口温度预校验
  if (form.turbine_in.medium_type === 'single' && form.turbine_in.medium === 'H2O') {
    loading.value = true
    try {
      const p_abs = form.turbine_in.p_in + 0.101325
      const satRes = await api.get('/thermo/water/saturation', { params: { p: p_abs } })
      const t_sat = satRes.saturation_temp
      if (form.turbine_in.t_in <= t_sat) {
        alert(`⚠️ 涡轮入口温度过低！\n\n当前温度：${form.turbine_in.t_in}°C\n饱和温度：${t_sat.toFixed(2)}°C\n\n请确保入口为过热蒸汽状态。`)
        loading.value = false
        return
      }
    } catch (e) {
      console.warn('获取饱和温度失败，继续提交给后端校验')
    }
  }

  loading.value = true
  try {
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

    localStorage.setItem('lastInputData_mode3', JSON.stringify(inputData))
    localStorage.setItem('mode3_input', JSON.stringify(inputData))

    const res = await api.post('/calculate/mode3', inputData)

    if (res?.error || !res?.success) {
      alert('⚠️ 计算失败：\n\n' + (res?.error_message || '请检查输入参数是否合理'))
      loading.value = false
      return
    }

    const fullResultData = {
      ...inputData,
      turbine: {
        ...inputData.turbine_in,
        p_out: inputData.turbine_params.p_out,
        ...res.turbine  // 展开 res.turbine 而不是 res
      }
    }
    localStorage.setItem('lastInputData_mode3', JSON.stringify(fullResultData))

    emit('calculate', res)
  } catch (e) {
    console.error('[Mode3] Calculation error:', e)
    emit('calculate', {
      error: true,
      error_message: (e?.userMessage || e?.message || '未知错误') + ' (详情请在浏览器控制台查看 F12)'
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const storedData = localStorage.getItem('mode3_input')
  if (storedData) {
    try {
      const parsed = JSON.parse(storedData)
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
      if (parsed.turbine_params) {
        form.turbine_params.p_out = parsed.turbine_params.p_out || 0.3
        form.turbine_params.adiabatic_efficiency = parsed.turbine_params.adiabatic_efficiency || 85
      }
    } catch (e) {
      console.error('读取历史数据失败', e)
    }
  }
})
</script>

<style scoped>
.mode-form-container { }
.card-body { }
.card-title { color: #303133; font-weight: bold; font-size: 14px; }

/* ========== 移动端响应式样式 ========== */
@media screen and (max-width: 768px) {
  .mode-form-row {
    gap: 10px;
  }

  .mode-form-label {
    font-size: 12px;
  }

  .mode-input-sm, .mode-input-md, .mode-input-lg,
  .mode-select-sm, .mode-select-md {
    font-size: 12px;
  }

  .mode-unit-text {
    font-size: 12px;
  }
}

/* ========== 小屏幕手机适配 (max-width: 480px) ========== */
@media screen and (max-width: 480px) {
  /* 表单行垂直布局 */
  .mode-form-row {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .mode-form-group {
    width: 100%;
    justify-content: space-between;
  }

  /* 标签自适应 */
  .mode-form-label {
    width: 80px !important;
    text-align: left;
    flex-shrink: 0;
  }

  /* 输入框全宽 */
  .mode-input-sm, .mode-input-md, .mode-input-lg,
  .mode-select-sm, .mode-select-md {
    width: 100%;
    max-width: 140px;
  }

  /* 单位文字缩小 */
  .mode-unit-text {
    min-width: 35px;
    font-size: 11px;
  }

  /* 混合介质组分垂直排列 */
  .mode-mix-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .mode-mix-item {
    width: 100%;
    justify-content: space-between;
    padding: 4px 0;
  }

  .mode-mix-item input {
    width: 80px;
    max-width: 100px;
  }

  /* 计算按钮全宽 */
  .mode-calc-btn {
    width: 100%;
    padding: 12px 20px;
  }
}
</style>
