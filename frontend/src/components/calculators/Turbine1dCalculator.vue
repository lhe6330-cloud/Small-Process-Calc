<template>
  <div class="calculator-container">
    <h2 class="tool-title">⚙️ 涡轮一维设计</h2>
    <p class="tool-description">径流式（向心）涡轮的一维通流设计计算</p>

    <el-card class="tool-form-card">
      <el-form :model="form" label-width="100px" class="tool-form">
        <el-form-item label="数据来源">
          <el-select v-model="form.sourceTurbine" placeholder="请选择涡轮来源" class="mode-select-md" style="width: 100%">
            <el-option label="模式 1 - 涡轮膨胀机" value="mode1_turbine" />
            <el-option label="模式 2 - 涡轮膨胀机" value="mode2_turbine" />
            <el-option label="模式 3 - 涡轮膨胀机" value="mode3_turbine" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="fetchDataAndAdd" :loading="fetching" class="tool-btn">
            📥 获取数据并添加
          </el-button>
          <el-button @click="resetForm" class="tool-btn">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 涡轮计算列表 -->
    <div v-for="(turb, index) in turbines" :key="turb.id" class="tool-item">
      <el-card class="tool-form-card">
        <template #header>
          <div class="tool-card-header">
            <span class="tool-card-title">⚙️ 涡轮一维设计 #{{ index + 1 }} - {{ turb.sourceTurbine }}</span>
            <div>
              <el-button size="small" type="primary" @click="calculateTurbine(turb)" :loading="turb.calculating">
                🚀 计算
              </el-button>
              <el-button size="small" type="danger" @click="removeTurbine(index)">删除</el-button>
            </div>
          </div>
        </template>

        <!-- 涡轮参数显示 -->
        <el-descriptions :column="3" border v-if="turb.turbineParams" class="tool-descriptions">
          <el-descriptions-item label="流量">{{ turb.turbineParams.flow_rate }} {{ turb.turbineParams.flow_unit }}</el-descriptions-item>
          <el-descriptions-item label="介质">{{ turb.turbineParams.medium }}</el-descriptions-item>
          <el-descriptions-item label="进口压力">{{ turb.turbineParams.p_in }} MPa.G</el-descriptions-item>
          <el-descriptions-item label="出口压力">{{ turb.turbineParams.p_out }} MPa.G</el-descriptions-item>
          <el-descriptions-item label="进口温度">{{ turb.turbineParams.t_in }} °C</el-descriptions-item>
          <el-descriptions-item label="出口温度">{{ turb.turbineParams.t_out }} °C</el-descriptions-item>
          <el-descriptions-item label="进口密度">{{ turb.turbineParams.rho_in }} kg/m³</el-descriptions-item>
          <el-descriptions-item label="出口密度">{{ turb.turbineParams.rho_out }} kg/m³</el-descriptions-item>
          <el-descriptions-item label="轴功率" :span="2">{{ turb.turbineParams.power_shaft }} kW</el-descriptions-item>
        </el-descriptions>

        <!-- 设计参数 -->
        <el-divider content-position="left" class="tool-divider" v-if="turb.turbineParams">⚙️ 设计参数</el-divider>
        <el-form :model="turb.designParams" label-width="100px" size="small" class="tool-form" v-if="turb.turbineParams">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="* 转速 n">
                <el-input v-model.number="turb.designParams.speedRpm" type="number" step="500" size="small" />
                <span style="margin-left: 5px">rpm</span>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="* 叶片数 Z">
                <el-input v-model.number="turb.designParams.bladeCount" type="number" step="1" size="small" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="* 速比 u/C₀">
                <el-input v-model.number="turb.designParams.speedRatio" type="number" step="0.01" size="small" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="* 反动度 Ω">
                <el-input v-model.number="turb.designParams.reaction" type="number" step="5" size="small" />
                <span style="margin-left: 5px">%</span>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <!-- 计算结果 -->
        <el-divider content-position="left" class="tool-divider" v-if="turb.result">📊 计算结果</el-divider>
        <div v-if="turb.result">
          <h4 class="tool-subtitle">📐 基本尺寸</h4>
          <el-descriptions :column="2" border size="small" class="tool-descriptions" v-if="turb.result.dimensions">
            <el-descriptions-item label="叶轮外径 D₁">{{ turb.result.dimensions?.D1 }} mm</el-descriptions-item>
            <el-descriptions-item label="叶轮内径 D₂">{{ turb.result.dimensions?.D2 }} mm</el-descriptions-item>
            <el-descriptions-item label="进口叶片高度 b₁">{{ turb.result.dimensions?.b1 }} mm</el-descriptions-item>
            <el-descriptions-item label="出口叶片高度 b₂">{{ turb.result.dimensions?.b2 }} mm</el-descriptions-item>
            <el-descriptions-item label="叶片数 Z" :span="2">{{ turb.result.dimensions?.Z }}</el-descriptions-item>
          </el-descriptions>

          <h4 class="tool-subtitle" style="margin-top: 15px">🔺 速度三角形 - 进口</h4>
          <el-descriptions :column="3" border size="small" class="tool-descriptions" v-if="turb.result.velocity_triangle_in">
            <el-descriptions-item label="C₁">{{ turb.result.velocity_triangle_in?.C1 }} m/s</el-descriptions-item>
            <el-descriptions-item label="W₁">{{ turb.result.velocity_triangle_in?.W1 }} m/s</el-descriptions-item>
            <el-descriptions-item label="U₁">{{ turb.result.velocity_triangle_in?.U1 }} m/s</el-descriptions-item>
            <el-descriptions-item label="α₁">{{ turb.result.velocity_triangle_in?.alpha1 }}°</el-descriptions-item>
            <el-descriptions-item label="β₁">{{ turb.result.velocity_triangle_in?.beta1 }}°</el-descriptions-item>
          </el-descriptions>

          <h4 class="tool-subtitle" style="margin-top: 15px">🔺 速度三角形 - 出口</h4>
          <el-descriptions :column="3" border size="small" class="tool-descriptions" v-if="turb.result.velocity_triangle_out">
            <el-descriptions-item label="C₂">{{ turb.result.velocity_triangle_out?.C2 }} m/s</el-descriptions-item>
            <el-descriptions-item label="W₂">{{ turb.result.velocity_triangle_out?.W2 }} m/s</el-descriptions-item>
            <el-descriptions-item label="U₂">{{ turb.result.velocity_triangle_out?.U2 }} m/s</el-descriptions-item>
            <el-descriptions-item label="α₂">{{ turb.result.velocity_triangle_out?.alpha2 }}°</el-descriptions-item>
            <el-descriptions-item label="β₂">{{ turb.result.velocity_triangle_out?.beta2 }}°</el-descriptions-item>
          </el-descriptions>

          <h4 class="tool-subtitle" style="margin-top: 15px">🔥 热力参数</h4>
          <el-descriptions :column="2" border size="small" class="tool-descriptions" v-if="turb.result.thermo_params">
            <el-descriptions-item label="级效率 η">{{ turb.result.thermo_params?.eta }}%</el-descriptions-item>
            <el-descriptions-item label="反动度 Ω">{{ turb.result.thermo_params?.omega }}%</el-descriptions-item>
            <el-descriptions-item label="速比 u/C₀">{{ turb.result.thermo_params?.speed_ratio }}</el-descriptions-item>
            <el-descriptions-item label="计算功率">{{ turb.result.performance?.P_calc }} kW</el-descriptions-item>
          </el-descriptions>
        </div>

        <el-alert
          v-if="turb.result"
          :title="getTurbineMessage(turb.result)"
          type="success"
          :closable="false"
          show-icon
          style="margin-top: 15px"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

const form = reactive({
  sourceTurbine: '',
})

const defaultDesignParams = {
  speedRpm: 3000,
  bladeCount: 13,
  speedRatio: 0.65,
  reaction: 50,
}

const fetching = ref(false)
const turbines = ref([])
let turbineIdCounter = 0

// 保存到 localStorage
const saveToLocalStorage = () => {
  localStorage.setItem('turbine_calculator_data', JSON.stringify({
    turbines: turbines.value,
    turbineIdCounter: turbineIdCounter,
  }))
}

// 从 localStorage 加载数据
const loadFromLocalStorage = () => {
  const stored = localStorage.getItem('turbine_calculator_data')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      turbines.value = parsed.turbines || []
      turbineIdCounter = parsed.turbineIdCounter || 0
    } catch (e) {
      console.error('加载涡轮计算数据失败', e)
    }
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadFromLocalStorage()
})

// 监听数据变化，自动保存
watch(turbines, () => {
  saveToLocalStorage()
}, { deep: true })

// 从 localStorage 获取数据并添加到列表
const fetchDataAndAdd = async () => {
  if (!form.sourceTurbine) {
    ElMessage.warning('请先选择数据来源')
    return
  }

  // 检查是否已存在该数据来源
  const exists = turbines.value.some(t => t.sourceTurbine === form.sourceTurbine)
  if (exists) {
    ElMessage.warning('该数据来源已添加到计算列表')
    return
  }

  fetching.value = true

  try {
    const mode = form.sourceTurbine.split('_')[0]
    const storedData = localStorage.getItem('lastInputData_' + mode)

    if (!storedData) {
      ElMessage.error('未找到历史数据，请先进行模式计算')
      return
    }

    const data = JSON.parse(storedData)
    const params = extractTurbineParams(data, form.sourceTurbine)

    if (!params) {
      ElMessage.error('该位置暂无可用数据')
      return
    }

    // 深拷贝保存数据快照
    const id = ++turbineIdCounter
    turbines.value.push({
      id,
      sourceTurbine: form.sourceTurbine,
      turbineParams: JSON.parse(JSON.stringify(params)), // 深拷贝快照
      designParams: JSON.parse(JSON.stringify(defaultDesignParams)), // 深拷贝默认设计参数
      result: null,
      calculating: false,
    })

    ElMessage.success('已添加到计算列表')
  } catch (e) {
    ElMessage.error('数据读取失败：' + e.message)
  } finally {
    fetching.value = false
  }
}

// 提取涡轮参数
const extractTurbineParams = (data, sourceTurbine) => {
  // 模式 1 和模式 2 从 turbine 字段读取
  // 模式 3 从 turbine_in 和 turbine_params 读取

  let turbine = null
  let turbineIn = null
  let turbineParams = null

  if (data.turbine) {
    turbine = data.turbine
  }
  if (data.turbine_in) {
    turbineIn = data.turbine_in
  }
  if (data.turbine_params) {
    turbineParams = data.turbine_params
  }

  // 如果没有涡轮数据，返回 null
  if (!turbine && !turbineIn) {
    return null
  }

  // 介质名称转换
  const mediumMap = {
    'H2O': '水/水蒸气',
    'N2': 'N₂',
    'O2': 'O₂',
    'CO2': 'CO₂',
    'H2': 'H₂',
    'Air': '空气',
  }

  // 获取介质名称
  let mediumName = 'N₂'
  const mediumType = turbine?.medium_type || turbineIn?.medium_type || 'single'

  if (mediumType === 'mix' && (turbine?.mix_composition || turbineIn?.mix_composition)) {
    const mixComp = turbine?.mix_composition || turbineIn?.mix_composition
    const components = Object.entries(mixComp)
      .filter(([_, value]) => value > 0.01)
      .map(([key, value]) => {
        const name = mediumMap[key] || key
        const percent = value > 1 ? value : value * 100
        return `${name}: ${percent.toFixed(1)}%`
      })
    mediumName = `混合介质 (${components.join(', ')})`
  } else {
    const medium = turbine?.medium || turbineIn?.medium || 'N2'
    mediumName = mediumMap[medium] || medium || 'N₂'
  }

  return {
    flow_rate: turbine?.flow_rate || turbineIn?.flow_rate || 1000,
    flow_unit: turbine?.flow_unit || turbineIn?.flow_unit || 'Nm3/h',
    medium: mediumName,
    medium_type: mediumType,
    mix_composition: turbine?.mix_composition || turbineIn?.mix_composition,
    p_in: turbine?.p_in || turbineIn?.p_in || 0.5,
    p_out: turbine?.p_out || turbineParams?.p_out || 0.1,
    t_in: turbine?.t_in || turbineIn?.t_in || 200,
    t_out: turbine?.t_out || 100,
    rho_in: turbine?.rho_in || 4.5,
    rho_out: turbine?.rho_out || 1.2,
    power_shaft: turbine?.power_shaft || 0,
    power_electric: turbine?.power_electric || 0,
  }
}

// 计算涡轮
const calculateTurbine = async (turb) => {
  if (!turb.turbineParams) {
    ElMessage.warning('请先获取涡轮参数')
    return
  }

  turb.calculating = true

  try {
    const response = await fetch('http://localhost:8000/api/calculate/mode5', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: turb.sourceTurbine.split('_')[0],
        flow_rate: turb.turbineParams.flow_rate,
        flow_unit: turb.turbineParams.flow_unit,
        p_in: turb.turbineParams.p_in,
        p_out: turb.turbineParams.p_out,
        t_in: turb.turbineParams.t_in,
        t_out: turb.turbineParams.t_out,
        rho_in: turb.turbineParams.rho_in,
        rho_out: turb.turbineParams.rho_out,
        power_shaft: turb.turbineParams.power_shaft,
        speed_rpm: turb.designParams.speedRpm,
        blade_count: turb.designParams.bladeCount,
        speed_ratio: turb.designParams.speedRatio,
        reaction: turb.designParams.reaction,
      }),
    })

    const data = await response.json()
    if (data.success) {
      turb.result = data
      ElMessage.success('涡轮一维设计计算完成')
    } else {
      // 修复错误信息显示问题
      let errorMsg = '未知错误'
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          errorMsg = data.detail.map(d => d?.msg || JSON.stringify(d)).join('; ')
        } else if (typeof data.detail === 'object') {
          errorMsg = JSON.stringify(data.detail)
        } else {
          errorMsg = data.detail
        }
      } else if (data.message) {
        errorMsg = data.message
      }
      ElMessage.error('计算失败：' + errorMsg)
    }
  } catch (e) {
    ElMessage.error('请求失败：' + e.message)
  } finally {
    turb.calculating = false
  }
}

// 获取涡轮计算结果消息
const getTurbineMessage = (result) => {
  if (result?.message) {
    return result.message
  }
  return '涡轮一维设计计算完成'
}

// 删除涡轮
const removeTurbine = (index) => {
  turbines.value.splice(index, 1)
  saveToLocalStorage()
  ElMessage.success('已删除')
}

// 重置
const resetForm = () => {
  form.sourceTurbine = ''
  turbines.value = []
  turbineIdCounter = 0
  saveToLocalStorage()
  ElMessage.success('已重置')
}
</script>

<style scoped>
.calculator-container { padding: 15px; }
.tool-title { color: #303133; margin-bottom: 8px; font-size: 20px; }
.tool-description { color: #666; margin-bottom: 15px; font-size: 13px; }
.tool-subtitle { color: #303133; margin: 15px 0 10px 0; font-size: 14px; }

/* ========== 移动端响应式样式 ========== */
@media screen and (max-width: 768px) {
  .calculator-container {
    padding: 10px;
  }

  .tool-title {
    font-size: 18px;
    margin-bottom: 6px;
  }

  .tool-description {
    font-size: 12px;
    margin-bottom: 12px;
  }

  .tool-subtitle {
    font-size: 13px;
    margin: 12px 0 8px 0;
  }

  :deep(.tool-descriptions) {
    font-size: 12px;
  }

  :deep(.el-descriptions__label),
  :deep(.el-descriptions__content) {
    font-size: 11px;
    padding: 8px 10px;
  }
}

/* ========== 小屏幕手机适配 (max-width: 480px) ========== */
@media screen and (max-width: 480px) {
  .calculator-container {
    padding: 8px;
  }

  .tool-title {
    font-size: 16px;
    margin-bottom: 5px;
  }

  .tool-description {
    font-size: 11px;
    margin-bottom: 10px;
  }

  .tool-subtitle {
    font-size: 12px;
    margin: 10px 0 6px 0;
  }

  /* 卡片头部垂直布局 */
  .tool-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .tool-card-header > div {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }

  /* Descriptions 改为 1 列 */
  :deep(.el-descriptions--default) {
    --el-descriptions-items-fill: 1;
  }

  :deep(.el-descriptions__label),
  :deep(.el-descriptions__content) {
    font-size: 10px;
    padding: 6px 8px;
  }

  /* 表单布局优化 - 移动端改为垂直布局 */
  /* el-col :span="8" 改为全宽 */
  :deep(.el-row) .el-col-8 {
    width: 100%;
    max-width: 100%;
    flex: 0 0 100%;
  }

  /* 表单标签和输入框垂直排列 */
  :deep(.el-form-item) {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 12px;
  }

  :deep(.el-form-item__label) {
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 5px;
    font-size: 12px;
  }

  :deep(.el-form-item__content) {
    width: 100%;
    margin-left: 0 !important;
  }

  :deep(.el-input-number),
  :deep(.el-select) {
    width: 100%;
  }

  /* 按钮缩小 */
  .tool-btn {
    padding: 6px 12px;
    font-size: 12px;
    height: 30px;
  }
}
</style>
