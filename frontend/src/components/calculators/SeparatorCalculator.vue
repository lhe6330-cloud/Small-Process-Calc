<template>
  <div class="calculator-container">
    <h2 class="tool-title">📐 分离器计算</h2>
    <p class="tool-description">基于 Stokes 沉降定律的重力沉降式气液分离器设计</p>

    <el-card class="tool-form-card">
      <el-form :model="form" label-width="100px" class="tool-form">
        <el-form-item label="数据来源">
          <el-select v-model="form.sourceNode" placeholder="请选择流程节点位置" class="mode-select-md" style="width: 100%">
            <el-option-group label="模式 1 - 先加热再膨胀">
              <el-option label="模式 1 - 冷边进口" value="mode1_cold_inlet" />
              <el-option label="模式 1 - 冷边出口" value="mode1_cold_out" />
              <el-option label="模式 1 - 涡轮出口" value="mode1_turbine_out" />
            </el-option-group>
            <el-option-group label="模式 2 - 先膨胀后回热">
              <el-option label="模式 2 - 涡轮进口" value="mode2_turbine_in" />
              <el-option label="模式 2 - 涡轮出口" value="mode2_turbine_out" />
              <el-option label="模式 2 - 冷边出口" value="mode2_cold_out" />
            </el-option-group>
            <el-option-group label="模式 3 - 直接膨胀">
              <el-option label="模式 3 - 涡轮进口" value="mode3_turbine_in" />
              <el-option label="模式 3 - 涡轮出口" value="mode3_turbine_out" />
            </el-option-group>
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

    <!-- 分离器计算列表 -->
    <div v-for="(sep, index) in separators" :key="sep.id" class="tool-item">
      <el-card class="tool-form-card">
        <template #header>
          <div class="tool-card-header">
            <span class="tool-card-title">📐 分离器计算 #{{ index + 1 }} - {{ sep.sourceNode }}</span>
            <div>
              <el-button size="small" type="primary" @click="calculateSeparator(sep)" :loading="sep.calculating">
                🚀 计算
              </el-button>
              <el-button size="small" type="danger" @click="removeSeparator(index)">删除</el-button>
            </div>
          </div>
        </template>

        <!-- 节点参数显示 -->
        <el-descriptions :column="2" border v-if="sep.nodeParams" class="tool-descriptions">
          <el-descriptions-item label="位置">{{ sep.sourceNode }}</el-descriptions-item>
          <el-descriptions-item label="压力">{{ sep.nodeParams.p }} MPa.G</el-descriptions-item>
          <el-descriptions-item label="温度">{{ sep.nodeParams.t }} °C</el-descriptions-item>
          <el-descriptions-item label="流量">{{ sep.nodeParams.flow_rate }} {{ sep.nodeParams.flow_unit }}</el-descriptions-item>
          <el-descriptions-item label="介质" :span="2">{{ sep.nodeParams.medium || 'N₂' }}</el-descriptions-item>
          <el-descriptions-item label="密度">{{ sep.nodeParams.rho }} kg/m³</el-descriptions-item>
          <el-descriptions-item label="粘度">{{ (sep.nodeParams.mu || 0.000018).toFixed(6) }} Pa·s</el-descriptions-item>
        </el-descriptions>

        <!-- 设计参数 -->
        <el-divider content-position="left" class="tool-divider" v-if="sep.nodeParams">⚙️ 设计参数</el-divider>
        <el-form :model="sep.designParams" label-width="100px" size="small" class="tool-form" v-if="sep.nodeParams">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="设计液滴粒径">
                <el-input v-model.number="sep.designParams.dropletSize" type="number" step="10" size="small" />
                <span style="margin-left: 5px">μm</span>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="长径比 L/D">
                <el-input v-model.number="sep.designParams.lengthRatio" type="number" step="0.5" size="small" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="分离器类型">
                <el-radio-group v-model="sep.designParams.separatorType" size="small">
                  <el-radio label="vertical">立式</el-radio>
                  <el-radio label="horizontal">卧式</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="要求停留时间">
                <el-input v-model.number="sep.designParams.residenceTime" type="number" step="30" size="small" />
                <span style="margin-left: 5px">s</span>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <!-- 计算结果 -->
        <el-divider content-position="left" class="tool-divider" v-if="sep.result">📊 计算结果</el-divider>
        <el-descriptions :column="2" border v-if="sep.result" class="tool-descriptions">
          <el-descriptions-item label="分离器直径">{{ sep.result.diameter }} mm</el-descriptions-item>
          <el-descriptions-item label="分离器高度/长度">{{ sep.result.length }} mm</el-descriptions-item>
          <el-descriptions-item label="气体流速">{{ sep.result.gas_velocity }} m/s</el-descriptions-item>
          <el-descriptions-item label="液滴沉降速度">{{ sep.result.settling_velocity }} m/s</el-descriptions-item>
          <el-descriptions-item label="液体停留时间">{{ sep.result.residence_time }} s</el-descriptions-item>
          <el-descriptions-item label="液封高度">{{ sep.result.liquid_height }} mm</el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="sep.result"
          :title="sep.result.message"
          :type="sep.result.check_passed ? 'success' : 'warning'"
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
  sourceNode: '',
})

const fetching = ref(false)
const separators = ref([])
let separatorIdCounter = 0

// 保存到 localStorage
const saveToLocalStorage = () => {
  localStorage.setItem('separator_calculator_data', JSON.stringify({
    separators: separators.value,
    separatorIdCounter: separatorIdCounter,
  }))
}

// 从 localStorage 加载数据
const loadFromLocalStorage = () => {
  const stored = localStorage.getItem('separator_calculator_data')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      separators.value = parsed.separators || []
      separatorIdCounter = parsed.separatorIdCounter || 0
    } catch (e) {
      console.error('加载分离器计算数据失败', e)
    }
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadFromLocalStorage()
})

// 监听数据变化，自动保存
watch(separators, () => {
  saveToLocalStorage()
}, { deep: true })

// 从 localStorage 获取数据并添加到列表
const fetchDataAndAdd = async () => {
  if (!form.sourceNode) {
    ElMessage.warning('请先选择数据来源')
    return
  }

  // 检查是否已存在该数据来源
  const exists = separators.value.some(s => s.sourceNode === form.sourceNode)
  if (exists) {
    ElMessage.warning('该数据来源已添加到计算列表')
    return
  }

  fetching.value = true

  try {
    const mode = form.sourceNode.split('_')[0]
    const storedData = localStorage.getItem('lastInputData_' + mode)

    if (!storedData) {
      ElMessage.error('未找到历史数据，请先进行模式计算')
      return
    }

    const data = JSON.parse(storedData)
    const params = extractNodeParams(data, form.sourceNode)

    if (!params) {
      ElMessage.error('该位置暂无可用数据')
      return
    }

    // 深拷贝保存数据快照
    const id = ++separatorIdCounter
    separators.value.push({
      id,
      sourceNode: form.sourceNode,
      nodeParams: JSON.parse(JSON.stringify(params)), // 深拷贝快照
      designParams: {
        dropletSize: 100,
        lengthRatio: 3.0,
        separatorType: 'vertical',
        residenceTime: 180,
      },
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

// 提取节点参数
const extractNodeParams = (data, sourceNode) => {
  switch (sourceNode) {
    case 'mode1_cold_inlet':
      return {
        p: data.cold_side?.p_in,
        t: data.cold_side?.t_in,
        flow_rate: data.cold_side?.flow_rate,
        flow_unit: data.cold_side?.flow_unit,
        medium: data.cold_side?.medium,
        medium_type: data.cold_side?.medium_type || 'single',
        rho: 1.2,
        mu: 1.8e-5,
      }
    case 'mode1_cold_out':
      return {
        p: data.cold_side?.p_out,
        t: data.cold_side?.t_out,
        flow_rate: data.cold_side?.flow_rate,
        flow_unit: data.cold_side?.flow_unit,
        medium: data.cold_side?.medium,
        medium_type: data.cold_side?.medium_type || 'single',
        rho: 1.2,
        mu: 1.8e-5,
      }
    case 'mode1_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type || 'single',
        rho: data.turbine?.rho_out,
        mu: 1.8e-5,
      }

    case 'mode2_turbine_in':
      return {
        p: data.turbine_in?.p_in,
        t: data.turbine_in?.t_in,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type || 'single',
        rho: 1.2,
        mu: 1.8e-5,
      }
    case 'mode2_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type || 'single',
        rho: data.turbine?.rho_out,
        mu: 1.8e-5,
      }
    case 'mode2_cold_out':
      return {
        p: data.hx_cold_out?.p_out,
        t: data.hx_cold_out?.t_out,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type || 'single',
        rho: 1.2,
        mu: 1.8e-5,
      }

    case 'mode3_turbine_in':
      return {
        p: data.turbine_in?.p_in,
        t: data.turbine_in?.t_in,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type || 'single',
        rho: 1.2,
        mu: 1.8e-5,
      }
    case 'mode3_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type || 'single',
        rho: data.turbine?.rho_out,
        mu: 1.8e-5,
      }

    default:
      return null
  }
}

// 计算分离器
const calculateSeparator = async (sep) => {
  if (!sep.nodeParams) {
    ElMessage.warning('请先获取节点工况数据')
    return
  }

  sep.calculating = true

  try {
    const response = await fetch('/api/calculate/separator', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: sep.sourceNode.split('_')[0],
        node_id: sep.sourceNode,
        node_params: sep.nodeParams,
        droplet_size: sep.designParams.dropletSize,
        length_ratio: sep.designParams.lengthRatio,
        separator_type: sep.designParams.separatorType,
        residence_time_req: sep.designParams.residenceTime,
      }),
    })

    const data = await response.json()
    if (data.success) {
      sep.result = data
      ElMessage.success('分离器计算完成')
    } else {
      ElMessage.error('计算失败：' + (data.message || '未知错误'))
    }
  } catch (e) {
    ElMessage.error('请求失败：' + e.message)
  } finally {
    sep.calculating = false
  }
}

// 删除分离器
const removeSeparator = (index) => {
  separators.value.splice(index, 1)
  saveToLocalStorage()
  ElMessage.success('已删除')
}

// 重置
const resetForm = () => {
  form.sourceNode = ''
  separators.value = []
  separatorIdCounter = 0
  saveToLocalStorage()
  ElMessage.success('已重置')
}
</script>

<style scoped>
.calculator-container { padding: 15px; }
.tool-title { color: #303133; margin-bottom: 8px; font-size: 20px; }
.tool-description { color: #666; margin-bottom: 15px; font-size: 13px; }
</style>
