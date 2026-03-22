<template>
  <div class="calculator-container">
    <h2>📐 管道计算</h2>
    <p class="description">基于设计流速的管道通径计算</p>

    <el-card class="form-card">
      <el-form :model="form" label-width="140px">
        <el-form-item label="数据来源" required>
          <el-select v-model="form.sourceNode" placeholder="请选择流程节点位置" style="width: 100%">
            <el-option-group label="模式 1 - 先加热再膨胀">
              <el-option label="模式 1 - 冷边进口" value="mode1_cold_inlet" />
              <el-option label="模式 1 - 冷边出口" value="mode1_cold_out" />
              <el-option label="模式 1 - 热边进口" value="mode1_hot_inlet" />
              <el-option label="模式 1 - 热边出口" value="mode1_hot_out" />
              <el-option label="模式 1 - 涡轮出口" value="mode1_turbine_out" />
            </el-option-group>
            <el-option-group label="模式 2 - 先膨胀后回热">
              <el-option label="模式 2 - 涡轮进口" value="mode2_turbine_in" />
              <el-option label="模式 2 - 涡轮出口" value="mode2_turbine_out" />
              <el-option label="模式 2 - 冷边出口" value="mode2_cold_out" />
              <el-option label="模式 2 - 热边进口" value="mode2_hot_inlet" />
              <el-option label="模式 2 - 热边出口" value="mode2_hot_out" />
            </el-option-group>
            <el-option-group label="模式 3 - 直接膨胀">
              <el-option label="模式 3 - 涡轮进口" value="mode3_turbine_in" />
              <el-option label="模式 3 - 涡轮出口" value="mode3_turbine_out" />
            </el-option-group>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="fetchDataAndAdd" :loading="fetching">
            📥 获取数据并添加
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 管道计算列表 -->
    <div v-for="(pipe, index) in pipes" :key="pipe.id" class="pipe-item">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">📐 管道计算 #{{ index + 1 }} - {{ pipe.sourceNode }}</span>
            <div>
              <el-button size="small" type="primary" @click="calculatePipe(pipe)" :loading="pipe.calculating">
                🚀 计算
              </el-button>
              <el-button size="small" type="danger" @click="removePipe(index)">删除</el-button>
            </div>
          </div>
        </template>

        <!-- 节点参数显示 -->
        <el-descriptions :column="2" border v-if="pipe.nodeParams">
          <el-descriptions-item label="位置">{{ pipe.sourceNode }}</el-descriptions-item>
          <el-descriptions-item label="压力">{{ pipe.nodeParams.p }} MPa.G</el-descriptions-item>
          <el-descriptions-item label="温度">{{ pipe.nodeParams.t }} °C</el-descriptions-item>
          <el-descriptions-item label="流量">{{ pipe.nodeParams.flow_rate }} {{ pipe.nodeParams.flow_unit }}</el-descriptions-item>
          <el-descriptions-item label="介质" :span="2">{{ pipe.nodeParams.medium || 'N₂' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 设计参数 -->
        <el-divider content-position="left">⚙️ 设计参数</el-divider>
        <el-form :model="pipe.designParams" label-width="120px" size="small" v-if="pipe.nodeParams">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="介质状态">
                <el-select v-model="pipe.designParams.mediumState" size="small">
                  <el-option label="气体" value="gas" />
                  <el-option label="液态" value="liquid" />
                  <el-option label="蒸汽" value="steam" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <!-- 计算结果 -->
        <el-descriptions :column="2" border v-if="pipe.result">
          <el-descriptions-item label="推荐通径">DN{{ pipe.result.recommended_dn }}</el-descriptions-item>
          <el-descriptions-item label="流速">{{ pipe.result.velocity?.toFixed(1) }} m/s</el-descriptions-item>
          <el-descriptions-item label="计算通径">{{ pipe.result.calculated_dn?.toFixed(1) }} mm</el-descriptions-item>
        </el-descriptions>

        <el-descriptions :column="2" border v-if="pipe.result?.lower_dn">
          <el-descriptions-item label="小一号通径">
            DN{{ pipe.result.lower_dn }} (v={{ pipe.result.lower_velocity?.toFixed(1) }} m/s)
          </el-descriptions-item>
          <el-descriptions-item label="大一号通径">
            DN{{ pipe.result.upper_dn }} (v={{ pipe.result.upper_velocity?.toFixed(1) }} m/s)
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="pipe.result"
          :title="getStatusMessage(pipe.result)"
          :type="pipe.result.velocity > 30 ? 'warning' : 'success'"
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
const pipes = ref([])
let pipeIdCounter = 0

// 保存到 localStorage
const saveToLocalStorage = () => {
  localStorage.setItem('pipe_calculator_data', JSON.stringify({
    pipes: pipes.value,
    pipeIdCounter: pipeIdCounter,
  }))
}

// 从 localStorage 加载数据
const loadFromLocalStorage = () => {
  const stored = localStorage.getItem('pipe_calculator_data')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      pipes.value = parsed.pipes || []
      pipeIdCounter = parsed.pipeIdCounter || 0
    } catch (e) {
      console.error('加载管道计算数据失败', e)
    }
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadFromLocalStorage()
})

// 监听数据变化，自动保存
watch(pipes, () => {
  saveToLocalStorage()
}, { deep: true })

// 从 localStorage 获取数据并添加到列表
const fetchDataAndAdd = async () => {
  if (!form.sourceNode) {
    ElMessage.warning('请先选择数据来源')
    return
  }

  // 检查是否已存在该数据来源
  const exists = pipes.value.some(p => p.sourceNode === form.sourceNode)
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
    const id = ++pipeIdCounter

    // 根据介质和温度自动判断介质状态
    let defaultMediumState = 'gas'
    if (params.medium === 'H2O') {
      if (params.t && params.t >= 100) {
        defaultMediumState = 'steam'
      } else {
        defaultMediumState = 'liquid'
      }
    }

    pipes.value.push({
      id,
      sourceNode: form.sourceNode,
      nodeParams: JSON.parse(JSON.stringify(params)), // 深拷贝快照
      designParams: {
        mediumState: defaultMediumState,  // 新增：介质状态默认值
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
        medium_type: data.cold_side?.medium_type,
        mix_composition: data.cold_side?.mix_composition,
      }
    case 'mode1_cold_out':
      return {
        p: data.cold_side?.p_out,
        t: data.cold_side?.t_out,
        flow_rate: data.cold_side?.flow_rate,
        flow_unit: data.cold_side?.flow_unit,
        medium: data.cold_side?.medium,
        medium_type: data.cold_side?.medium_type,
        mix_composition: data.cold_side?.mix_composition,
      }
    case 'mode1_hot_inlet':
      return {
        p: data.hot_side?.p_in,
        t: data.hot_side?.t_in,
        flow_rate: data.hot_side?.flow_rate,
        flow_unit: data.hot_side?.flow_unit,
        medium: data.hot_side?.medium,
        medium_type: data.hot_side?.medium_type,
        mix_composition: data.hot_side?.mix_composition,
      }
    case 'mode1_hot_out':
      return {
        p: data.hot_side?.p_out,
        t: data.hot_side?.t_out || data.hot_side?.t_in,
        flow_rate: data.hot_side?.flow_rate,
        flow_unit: data.hot_side?.flow_unit,
        medium: data.hot_side?.medium,
        medium_type: data.hot_side?.medium_type,
        mix_composition: data.hot_side?.mix_composition,
      }
    case 'mode1_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type,
        mix_composition: data.turbine?.mix_composition,
        rho: data.turbine?.rho_out,
      }

    case 'mode2_turbine_in':
      return {
        p: data.turbine_in?.p_in,
        t: data.turbine_in?.t_in,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type,
        mix_composition: data.turbine_in?.mix_composition,
      }
    case 'mode2_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type,
        mix_composition: data.turbine?.mix_composition,
        rho: data.turbine?.rho_out,
      }
    case 'mode2_cold_out':
      return {
        p: data.hx_cold_out?.p_out,
        t: data.hx_cold_out?.t_out,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type,
      }
    case 'mode2_hot_inlet':
      return {
        p: data.hx_hot?.p_in,
        t: data.hx_hot?.t_in,
        flow_rate: data.hx_hot?.flow_rate,
        flow_unit: data.hx_hot?.flow_unit,
        medium: data.hx_hot?.medium,
        medium_type: data.hx_hot?.medium_type,
        mix_composition: data.hx_hot?.mix_composition,
      }
    case 'mode2_hot_out':
      return {
        p: data.hx_hot?.p_out,
        t: data.hx_hot?.t_in,
        flow_rate: data.hx_hot?.flow_rate,
        flow_unit: data.hx_hot?.flow_unit,
        medium: data.hx_hot?.medium,
        medium_type: data.hx_hot?.medium_type,
        mix_composition: data.hx_hot?.mix_composition,
      }

    case 'mode3_turbine_in':
      return {
        p: data.turbine_in?.p_in,
        t: data.turbine_in?.t_in,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type,
        mix_composition: data.turbine_in?.mix_composition,
      }
    case 'mode3_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type,
        mix_composition: data.turbine?.mix_composition,
        rho: data.turbine?.rho_out,
      }

    default:
      return null
  }
}

// 计算管道
const calculatePipe = async (pipe) => {
  if (!pipe.nodeParams) {
    ElMessage.warning('请先获取节点工况数据')
    return
  }

  pipe.calculating = true

  try {
    const payload = {
      flow_rate: pipe.nodeParams.flow_rate,
      flow_unit: pipe.nodeParams.flow_unit,
      p_gauge: pipe.nodeParams.p,
      t: pipe.nodeParams.t,
      medium_type: pipe.nodeParams.medium_type,
      medium: pipe.nodeParams.medium || null,
      mix_composition: pipe.nodeParams.mix_composition || null,
      medium_state: pipe.designParams?.mediumState || 'gas',  // 新增：用户选择的介质状态
    }
    console.log('发送管道计算请求:', payload)
    const response = await fetch('/api/calculate/pipe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    console.log('管道计算响应状态:', response.status)

    const data = await response.json()
    console.log('管道 API 响应:', data)

    if (data.success || data.recommended_dn) {
      pipe.result = data
      ElMessage.success('管道计算完成')
    } else {
      let errorMsg = '未知错误'
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          errorMsg = data.detail.map(d => d?.msg || JSON.stringify(d)).join('; ')
        } else {
          errorMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
        }
      } else if (data.message) {
        errorMsg = data.message
      } else if (data.error) {
        errorMsg = data.error
      }
      ElMessage.error('计算失败：' + errorMsg)
    }
  } catch (e) {
    console.error('管道计算异常:', e)
    ElMessage.error('请求失败：' + e.message)
  } finally {
    pipe.calculating = false
  }
}

// 删除管道
const removePipe = (index) => {
  pipes.value.splice(index, 1)
  saveToLocalStorage()
  ElMessage.success('已删除')
}

// 重置
const resetForm = () => {
  form.sourceNode = ''
  pipes.value = []
  pipeIdCounter = 0
  saveToLocalStorage()
  ElMessage.success('已重置')
}

// 状态消息
const getStatusMessage = (result) => {
  const v = result.velocity
  if (v > 30) {
    return `⚠️ 流速 ${v.toFixed(1)} m/s，超过 30 m/s 建议值`
  } else if (v > 25) {
    return `✅ 流速 ${v.toFixed(1)} m/s，在合理范围内`
  } else {
    return `✅ 流速 ${v.toFixed(1)} m/s，经济流速`
  }
}
</script>

<style scoped>
.calculator-container { padding: 20px; }
h2 { color: #303133; margin-bottom: 10px; }
.description { color: #666; margin-bottom: 20px; }
.form-card, .result-card { margin-bottom: 20px; background: #ffffff; border: 1px solid #dcdfe6; }
.card-title { font-weight: 600; color: #303133; }
.card-header { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.pipe-item { margin-bottom: 20px; }
</style>
