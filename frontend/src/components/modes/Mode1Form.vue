<template>
  <div class="mode-form-container">
    <!-- 换热器冷边卡片 -->
    <el-card class="mode-form-card">
      <template #header><span class="card-title">🔥 换热器冷边</span></template>
      <div class="card-body">
        <!-- 单一介质时：显示介质类型 + 介质；混合介质时：显示介质类型 + 组分类型 + 5 组分 + 合计 + 归一化 -->
        <div class="mode-form-row">
          <div class="mode-form-group">
            <label class="mode-form-label">介质类型</label>
            <el-select v-model="form.cold.medium_type" placeholder="选择" @change="onMediumTypeChange('cold')" class="mode-select-md">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </div>

          <!-- 单一介质时显示介质选择 -->
          <div class="mode-form-group" v-if="form.cold.medium_type === 'single'">
            <label class="mode-form-label short">介质</label>
            <el-select v-model="form.cold.medium" @change="onMediumChange('cold')" class="mode-select-md">
              <el-option label="氮气 (N₂)" value="N2" />
              <el-option label="氧气 (O₂)" value="O2" />
              <el-option label="空气" value="Air" />
              <el-option label="二氧化碳" value="CO2" />
              <el-option label="氢气" value="H2" />
              <el-option label="水/水蒸气" value="H2O" />
            </el-select>
          </div>

          <!-- 混合介质时显示组分类型 + 5 组分 + 合计 + 归一化 -->
          <div class="mode-form-group" v-if="form.cold.medium_type === 'mix'">
            <div class="mode-divider"></div>
            <div class="mode-form-group">
              <span class="mode-form-label" style="width: auto; font-size: 12px;">组分类型：</span>
              <label class="mode-radio-label">
                <input type="radio" v-model="form.cold.mixData.composition_type" value="mole" />
                <span>摩尔</span>
              </label>
              <label class="mode-radio-label">
                <input type="radio" v-model="form.cold.mixData.composition_type" value="mass" />
                <span>质量</span>
              </label>
            </div>
            <div class="mode-divider"></div>
            <div class="mode-mix-row">
              <div class="mode-mix-item" v-for="(value, key) in form.cold.mixData.composition" :key="key">
                <input type="number" v-model.number="form.cold.mixData.composition[key]" :step="key === 'H2O' || key === 'CO2' ? 0.1 : 1" />
                <span>{{ getMediumLabel(key) }}</span>
                <span class="percent">%</span>
              </div>
            </div>
            <div class="mode-mix-footer">
              <span class="mode-total-label">合计：</span>
              <span class="mode-total-value" :style="{ color: totalCold !== 100 ? '#f59e0b' : '#22c55e' }">{{ totalCold.toFixed(1) }}%</span>
              <button class="mode-normalize-btn" @click="normalizeCold" :disabled="totalCold === 0 || Math.abs(totalCold - 100) < 0.01">🔄</button>
            </div>
          </div>
        </div>

        <!-- 第二行：流量、压力、温度 -->
        <div class="mode-form-row">
          <div class="mode-form-group">
            <label class="mode-form-label short">流量</label>
            <el-input v-model.number="form.cold.flow_rate" type="number" class="mode-input-md" />
            <el-select v-model="form.cold.flow_unit" class="mode-select-sm">
              <el-option label="T/h" value="T/h" />
              <el-option label="Nm³/h" value="Nm3/h" />
            </el-select>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">入口压力</label>
            <el-input v-model.number="form.cold.p_in" type="number" step="0.1" class="mode-input-md" />
            <span class="mode-unit-text">MPa.G</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">出口压力</label>
            <el-input v-model.number="form.cold.p_out" type="number" step="0.1" class="mode-input-md" />
            <span class="mode-unit-text">MPa.G</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">入口温度</label>
            <el-input v-model.number="form.cold.t_in" type="number" step="1" class="mode-input-md" />
            <span class="mode-unit-text">°C</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">出口温度</label>
            <el-input v-model.number="form.cold.t_out" type="number" step="1" class="mode-input-md" />
            <span class="mode-unit-text">°C</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 换热器热边卡片 -->
    <el-card class="mode-form-card">
      <template #header><span class="card-title">🔥 换热器热边</span></template>
      <div class="card-body">
        <!-- 单一介质时：显示介质类型 + 介质；混合介质时：显示介质类型 + 组分类型 + 5 组分 + 合计 + 归一化 -->
        <div class="mode-form-row">
          <div class="mode-form-group">
            <label class="mode-form-label">介质类型</label>
            <el-select v-model="form.hot.medium_type" placeholder="选择" @change="onMediumTypeChange('hot')" class="mode-select-md">
              <el-option label="单一介质" value="single" />
              <el-option label="混合介质" value="mix" />
            </el-select>
          </div>

          <!-- 单一介质时显示介质选择 -->
          <div class="mode-form-group" v-if="form.hot.medium_type === 'single'">
            <label class="mode-form-label short">介质</label>
            <el-select v-model="form.hot.medium" @change="onMediumChange('hot')" class="mode-select-md">
              <el-option label="氮气 (N₂)" value="N2" />
              <el-option label="氧气 (O₂)" value="O2" />
              <el-option label="空气" value="Air" />
              <el-option label="二氧化碳" value="CO2" />
              <el-option label="氢气" value="H2" />
              <el-option label="水/水蒸气" value="H2O" />
            </el-select>
          </div>

          <!-- 混合介质时显示组分类型 + 5 组分 + 合计 + 归一化 -->
          <div class="mode-form-group" v-if="form.hot.medium_type === 'mix'">
            <div class="mode-divider"></div>
            <div class="mode-form-group">
              <span class="mode-form-label" style="width: auto; font-size: 12px;">组分类型：</span>
              <label class="mode-radio-label">
                <input type="radio" v-model="form.hot.mixData.composition_type" value="mole" />
                <span>摩尔</span>
              </label>
              <label class="mode-radio-label">
                <input type="radio" v-model="form.hot.mixData.composition_type" value="mass" />
                <span>质量</span>
              </label>
            </div>
            <div class="mode-divider"></div>
            <div class="mode-mix-row">
              <div class="mode-mix-item" v-for="(value, key) in form.hot.mixData.composition" :key="key">
                <input type="number" v-model.number="form.hot.mixData.composition[key]" :step="key === 'H2O' || key === 'CO2' ? 0.1 : 1" />
                <span>{{ getMediumLabel(key) }}</span>
                <span class="percent">%</span>
              </div>
            </div>
            <div class="mode-mix-footer">
              <span class="mode-total-label">合计：</span>
              <span class="mode-total-value" :style="{ color: totalHot !== 100 ? '#f59e0b' : '#22c55e' }">{{ totalHot.toFixed(1) }}%</span>
              <button class="mode-normalize-btn" @click="normalizeHot" :disabled="totalHot === 0 || Math.abs(totalHot - 100) < 0.01">🔄</button>
            </div>
          </div>
        </div>

        <!-- 第二行：流量、压力、温度 -->
        <div class="mode-form-row">
          <div class="mode-form-group">
            <label class="mode-form-label short">流量</label>
            <el-input v-model.number="form.hot.flow_rate" type="number" class="mode-input-md" />
            <el-select v-model="form.hot.flow_unit" class="mode-select-sm">
              <el-option label="T/h" value="T/h" />
              <el-option label="Nm³/h" value="Nm3/h" />
            </el-select>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">入口压力</label>
            <el-input v-model.number="form.hot.p_in" type="number" step="0.1" class="mode-input-md" />
            <span class="mode-unit-text">MPa.G</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">出口压力</label>
            <el-input v-model.number="form.hot.p_out" type="number" step="0.1" class="mode-input-md" />
            <span class="mode-unit-text">MPa.G</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">入口温度</label>
            <el-input v-model.number="form.hot.t_in" type="number" step="1" class="mode-input-md" />
            <span class="mode-unit-text">°C</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 涡轮发电机组卡片 -->
    <el-card class="mode-form-card">
      <template #header><span class="card-title">⚡ 涡轮发电机组</span></template>
      <div class="card-body">
        <div class="mode-form-row">
          <div class="mode-form-group">
            <label class="mode-form-label">出口压力</label>
            <el-input v-model.number="form.turbine.p_out" type="number" step="0.1" class="mode-input-md" />
            <span class="mode-unit-text">MPa.G</span>
          </div>
          <div class="mode-form-group">
            <label class="mode-form-label">绝热效率</label>
            <el-input v-model.number="form.turbine.adiabatic_efficiency" type="number" step="1" class="mode-input-md" />
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

const mediumLabels = {
  N2: 'N₂',
  O2: 'O₂',
  H2: 'H₂',
  CO2: 'CO₂',
  H2O: 'H₂O'
}

const getMediumLabel = (key) => mediumLabels[key] || key

// 计算组分总计
const totalCold = computed(() => {
  return Object.values(form.cold.mixData.composition).reduce((sum, val) => sum + Number(val), 0)
})

const totalHot = computed(() => {
  return Object.values(form.hot.mixData.composition).reduce((sum, val) => sum + Number(val), 0)
})

// 归一化函数
const normalizeCold = () => {
  if (totalCold.value === 0 || Math.abs(totalCold.value - 100) < 0.01) return
  const factor = 100 / totalCold.value
  for (const key in form.cold.mixData.composition) {
    form.cold.mixData.composition[key] = Math.round(form.cold.mixData.composition[key] * factor * 100) / 100
  }
}

const normalizeHot = () => {
  if (totalHot.value === 0 || Math.abs(totalHot.value - 100) < 0.01) return
  const factor = 100 / totalHot.value
  for (const key in form.hot.mixData.composition) {
    form.hot.mixData.composition[key] = Math.round(form.hot.mixData.composition[key] * factor * 100) / 100
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
  if (form.cold.medium_type === 'mix') {
    if (Math.abs(totalCold.value - 100) > 0.01) {
      alert('冷边混合介质组分合计不为 100%，请先点击归一化按钮')
      return
    }
  }
  if (form.hot.medium_type === 'mix') {
    if (Math.abs(totalHot.value - 100) > 0.01) {
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

    // 保存输入数据到 localStorage
    localStorage.setItem('mode1_input', JSON.stringify(inputData))
    localStorage.setItem('lastInputData', JSON.stringify(inputData))
    localStorage.setItem('lastInputData_mode1', JSON.stringify(inputData))

    const res = await api.post('/calculate/mode1', inputData)

    // 保存完整的计算结果
    const fullResultData = {
      ...inputData,
      turbine: {
        ...inputData.turbine,
        ...res.turbine  // 展开 res.turbine 而不是 res
      }
    }
    localStorage.setItem('lastInputData_mode1', JSON.stringify(fullResultData))

    emit('calculate', res)
  } catch (e) {
    console.error('[Mode1] Calculation error:', e)
    const errorMsg = e?.userMessage || e?.message || '网络错误或服务器无响应，请稍后重试。'
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
  const storedData = localStorage.getItem('mode1_input')
  if (storedData) {
    try {
      const parsed = JSON.parse(storedData)
      if (parsed.cold_side) {
        const cold = parsed.cold_side
        form.cold.medium_type = cold.medium_type || 'single'
        form.cold.medium = cold.medium || 'N2'
        form.cold.flow_rate = cold.flow_rate || 1000
        form.cold.flow_unit = cold.flow_unit || 'Nm3/h'
        form.cold.p_in = cold.p_in || 0.5
        form.cold.p_out = cold.p_out || 0.48
        form.cold.t_in = cold.t_in || 20
        form.cold.t_out = cold.t_out || 200
        if (cold.mix_composition) {
          form.cold.mixData = { composition: cold.mix_composition, composition_type: cold.composition_type || 'mole' }
        }
      }
      if (parsed.hot_side) {
        const hot = parsed.hot_side
        form.hot.medium_type = hot.medium_type || 'single'
        form.hot.medium = hot.medium || 'H2O'
        form.hot.flow_rate = hot.flow_rate || 0.5
        form.hot.flow_unit = hot.flow_unit || 'T/h'
        form.hot.p_in = hot.p_in || 0.6
        form.hot.p_out = hot.p_out || 0.55
        form.hot.t_in = hot.t_in || 250
        if (hot.mix_composition) {
          form.hot.mixData = { composition: hot.mix_composition, composition_type: hot.composition_type || 'mole' }
        }
      }
      if (parsed.turbine) {
        form.turbine.p_out = parsed.turbine.p_out || 0.1
        form.turbine.adiabatic_efficiency = parsed.turbine.adiabatic_efficiency || 85
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
