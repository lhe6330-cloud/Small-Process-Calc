<template>
  <div class="calculator-container">
    <h2 class="tool-title">🔧 阀门计算</h2>
    <p class="tool-description">基于 IEC 60534 标准的阀门选型计算</p>

    <el-card class="tool-form-card">
      <el-form :model="form" label-width="100px" class="tool-form">
        <el-form-item label="数据来源">
          <el-select v-model="form.sourceNode" placeholder="请选择流程节点位置" class="mode-select-md" style="width: 100%">
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
          <el-button type="primary" @click="fetchDataAndAdd" :loading="fetching" class="tool-btn">
            📥 获取数据并添加
          </el-button>
          <el-button @click="resetForm" class="tool-btn">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 阀门计算列表 -->
    <div v-for="(valve, index) in valves" :key="valve.id" class="tool-item">
      <el-card class="tool-form-card">
        <template #header>
          <div class="tool-card-header">
            <span class="tool-card-title">🔧 阀门计算 #{{ index + 1 }} - {{ valve.sourceNode }}</span>
            <div>
              <el-button size="small" type="primary" @click="calculateValve(valve)" :loading="valve.calculating">
                🚀 计算
              </el-button>
              <el-button size="small" type="danger" @click="removeValve(index)">删除</el-button>
            </div>
          </div>
        </template>

        <!-- 节点参数显示 -->
        <el-descriptions :column="2" border v-if="valve.nodeParams" class="tool-descriptions">
          <el-descriptions-item label="位置">{{ valve.sourceNode }}</el-descriptions-item>
          <el-descriptions-item label="压力">{{ valve.nodeParams.p }} MPa.G</el-descriptions-item>
          <el-descriptions-item label="温度">{{ valve.nodeParams.t }} °C</el-descriptions-item>
          <el-descriptions-item label="流量">{{ valve.nodeParams.flow_rate }} {{ valve.nodeParams.flow_unit }}</el-descriptions-item>
          <el-descriptions-item label="介质" :span="2">{{ valve.nodeParams.medium || 'N₂' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 阀门参数 -->
        <el-divider content-position="left" class="tool-divider" v-if="valve.nodeParams">⚙️ 阀门参数</el-divider>
        <el-form :model="valve.designParams" label-width="100px" size="small" class="tool-form" v-if="valve.nodeParams">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="介质状态">
                <el-select v-model="valve.designParams.mediumState" size="small">
                  <el-option label="气体" value="gas" />
                  <el-option label="液态" value="liquid" />
                  <el-option label="蒸汽" value="steam" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="阀门压差">
                <el-input v-model.number="valve.designParams.deltaP" type="number" step="5" size="small" />
                <span style="margin-left: 5px">kPa</span>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="阀门类型">
                <el-select v-model="valve.designParams.valveType" size="small" @change="updateValveDnOptions(valve)">
                  <el-option label="蝶阀" value="butterfly" />
                  <el-option label="截止阀" value="globe" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="通径选择">
                <el-select v-model="valve.designParams.specifiedDn" size="small" placeholder="自动选择">
                  <el-option label="自动" value="" />
                  <el-option v-for="dn in valve.designParams.valveDnOptions" :key="dn" :label="'DN' + dn" :value="dn" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <!-- 计算结果 -->
        <el-divider content-position="left" class="tool-divider" v-if="valve.result">📊 计算结果</el-divider>
        <el-descriptions :column="2" border v-if="valve.result" class="tool-descriptions">
          <el-descriptions-item label="阀门通径">DN{{ valve.result.valve_dn }}</el-descriptions-item>
          <el-descriptions-item label="阀门类型">{{ valve.result.valve_type === 'globe' ? '截止阀' : '蝶阀' }}</el-descriptions-item>
          <el-descriptions-item label="所需 Kv">{{ valve.result.kv_required?.toFixed(1) }}</el-descriptions-item>
          <el-descriptions-item label="额定 Kv">{{ valve.result.kv_rated }}</el-descriptions-item>
          <el-descriptions-item label="预计开度">{{ valve.result.valve_opening?.toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="FL 系数">{{ valve.result.fl_coefficient }}</el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="valve.result"
          :title="valve.result.status_msg"
          :type="valve.result.check_status === 'ok' ? 'success' : valve.result.check_status === 'warning' ? 'warning' : 'error'"
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
const valves = ref([])
let valveIdCounter = 0

// 通径选项常量
const BUTTERFLY_DN = [150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000]
const GLOBE_DN = [15, 20, 25, 32, 45, 50, 65, 80, 100, 125]

// 获取通径选项
const getValveDnOptions = (valveType) => {
  return valveType === 'butterfly' ? BUTTERFLY_DN : GLOBE_DN
}

// 保存到 localStorage
const saveToLocalStorage = () => {
  localStorage.setItem('valve_calculator_data', JSON.stringify({
    valves: valves.value,
    valveIdCounter: valveIdCounter,
  }))
}

// 从 localStorage 加载数据并初始化通径选项
const loadFromLocalStorage = () => {
  const stored = localStorage.getItem('valve_calculator_data')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      valves.value = parsed.valves || []
      // 初始化每个阀门的通径选项
      valves.value.forEach(valve => {
        if (!valve.designParams) {
          valve.designParams = {
            deltaP: 30,
            valveType: 'butterfly',
            mediumState: 'gas',
            specifiedDn: '',
          }
        }
        // 确保通径选项存在
        valve.designParams.valveDnOptions = getValveDnOptions(valve.designParams.valveType)
      })
      valveIdCounter = parsed.valveIdCounter || 0
    } catch (e) {
      console.error('加载阀门计算数据失败', e)
    }
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadFromLocalStorage()
})

// 监听数据变化，自动保存
watch(valves, () => {
  saveToLocalStorage()
}, { deep: true })

// 从 localStorage 获取数据并添加到列表
const fetchDataAndAdd = async () => {
  if (!form.sourceNode) {
    ElMessage.warning('请先选择数据来源')
    return
  }

  // 检查是否已存在该数据来源
  const exists = valves.value.some(v => v.sourceNode === form.sourceNode)
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
    const id = ++valveIdCounter

    // 根据介质和温度自动判断介质状态
    let defaultMediumState = 'gas'
    if (params.medium === 'H2O') {
      if (params.t && params.t >= 100) {
        defaultMediumState = 'steam'
      } else {
        defaultMediumState = 'liquid'
      }
    }

    valves.value.push({
      id,
      sourceNode: form.sourceNode,
      nodeParams: JSON.parse(JSON.stringify(params)), // 深拷贝快照
      designParams: {
        deltaP: 30,
        valveType: 'butterfly',
        mediumState: defaultMediumState,  // 新增：介质状态默认值
        specifiedDn: '',  // 空表示自动选择
        valveDnOptions: getValveDnOptions('butterfly'),  // 初始化通径选项
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
        mix_composition: data.cold_side?.mix_composition || null,
      }
    case 'mode1_cold_out':
      return {
        p: data.cold_side?.p_out,
        t: data.cold_side?.t_out,
        flow_rate: data.cold_side?.flow_rate,
        flow_unit: data.cold_side?.flow_unit,
        medium: data.cold_side?.medium,
        medium_type: data.cold_side?.medium_type || 'single',
        mix_composition: data.cold_side?.mix_composition || null,
      }
    case 'mode1_hot_inlet':
      return {
        p: data.hot_side?.p_in,
        t: data.hot_side?.t_in,
        flow_rate: data.hot_side?.flow_rate,
        flow_unit: data.hot_side?.flow_unit,
        medium: data.hot_side?.medium,
        medium_type: data.hot_side?.medium_type || 'single',
        mix_composition: data.hot_side?.mix_composition || null,
      }
    case 'mode1_hot_out':
      return {
        p: data.hot_side?.p_out,
        t: data.hot_side?.t_out || data.hot_side?.t_in,
        flow_rate: data.hot_side?.flow_rate,
        flow_unit: data.hot_side?.flow_unit,
        medium: data.hot_side?.medium,
        medium_type: data.hot_side?.medium_type || 'single',
        mix_composition: data.hot_side?.mix_composition || null,
      }
    case 'mode1_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type || 'single',
        mix_composition: data.turbine?.mix_composition || null,
        rho: data.turbine?.rho_out,
      }

    case 'mode2_turbine_in':
      return {
        p: data.turbine_in?.p_in,
        t: data.turbine_in?.t_in,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type || 'single',
        mix_composition: data.turbine_in?.mix_composition || null,
      }
    case 'mode2_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type || 'single',
        mix_composition: data.turbine?.mix_composition || null,
        rho: data.turbine?.rho_out,
      }
    case 'mode2_cold_out':
      return {
        p: data.hx_cold_out?.p_out,
        t: data.hx_cold_out?.t_out,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type || 'single',
        mix_composition: data.turbine_in?.mix_composition || null,
      }
    case 'mode2_hot_inlet':
      return {
        p: data.hx_hot?.p_in,
        t: data.hx_hot?.t_in,
        flow_rate: data.hx_hot?.flow_rate,
        flow_unit: data.hx_hot?.flow_unit,
        medium: data.hx_hot?.medium,
        medium_type: data.hx_hot?.medium_type || 'single',
        mix_composition: data.hx_hot?.mix_composition || null,
      }
    case 'mode2_hot_out':
      return {
        p: data.hx_hot?.p_out,
        t: data.hx_hot?.t_in,
        flow_rate: data.hx_hot?.flow_rate,
        flow_unit: data.hx_hot?.flow_unit,
        medium: data.hx_hot?.medium,
        medium_type: data.hx_hot?.medium_type || 'single',
        mix_composition: data.hx_hot?.mix_composition || null,
      }

    case 'mode3_turbine_in':
      return {
        p: data.turbine_in?.p_in,
        t: data.turbine_in?.t_in,
        flow_rate: data.turbine_in?.flow_rate,
        flow_unit: data.turbine_in?.flow_unit,
        medium: data.turbine_in?.medium,
        medium_type: data.turbine_in?.medium_type || 'single',
        mix_composition: data.turbine_in?.mix_composition || null,
      }
    case 'mode3_turbine_out':
      return {
        p: data.turbine?.p_out,
        t: data.turbine?.t_out,
        flow_rate: data.turbine?.flow_rate,
        flow_unit: data.turbine?.flow_unit,
        medium: data.turbine?.medium,
        medium_type: data.turbine?.medium_type || 'single',
        mix_composition: data.turbine?.mix_composition || null,
        rho: data.turbine?.rho_out,
      }

    default:
      return null
  }
}

// 计算阀门
const calculateValve = async (valve) => {
  if (!valve.nodeParams) {
    ElMessage.warning('请先获取节点工况数据')
    return
  }

  valve.calculating = true

  try {
    // 需要先计算管道得到 DN
    const pipePayload = {
      flow_rate: valve.nodeParams.flow_rate,
      flow_unit: valve.nodeParams.flow_unit,
      p_gauge: valve.nodeParams.p,
      t: valve.nodeParams.t,
      medium_type: valve.nodeParams.medium_type,
      medium: valve.nodeParams.medium || null,
      mix_composition: valve.nodeParams.mix_composition || null,
    }
    console.log('发送管道计算请求 (阀门内):', pipePayload)
    const pipeResponse = await fetch('/api/calculate/pipe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(pipePayload),
    })
    console.log('管道 API 响应状态:', pipeResponse.status)

    const pipeData = await pipeResponse.json()
    console.log('管道 API 响应 (阀门内):', pipeData)

    if (!pipeData.recommended_dn && !pipeData.success) {
      let errorMsg = '管道计算失败'
      if (pipeData.detail) {
        errorMsg = typeof pipeData.detail === 'string' ? pipeData.detail : JSON.stringify(pipeData.detail)
      } else if (pipeData.message) {
        errorMsg = pipeData.message
      }
      throw new Error(errorMsg)
    }

    // 调用阀门计算 API
    const valvePayload = {
      flow_rate: valve.nodeParams.flow_rate,
      flow_unit: valve.nodeParams.flow_unit,
      p_gauge: valve.nodeParams.p,  // 新增：必填字段
      t: valve.nodeParams.t,
      medium_type: valve.nodeParams.medium_type,
      medium: valve.nodeParams.medium || null,
      mix_composition: valve.nodeParams.mix_composition || null,
      medium_state: valve.designParams.mediumState,  // 新增：用户选择的介质状态
      rho: pipeData.rho || 1.2,
      pipe_dn: pipeData.recommended_dn || 100,
      delta_p_kpa: valve.designParams.deltaP,
      valve_type: valve.designParams.valveType,
      p_in_abs: valve.nodeParams.p + 0.101325,
      p_out_abs: valve.nodeParams.p + 0.101325 - valve.designParams.deltaP / 1000,
      specified_dn: valve.designParams.specifiedDn || null,  // 新增：用户指定通径
    }
    console.log('发送阀门计算请求:', valvePayload)
    const response = await fetch('/api/calculate/valve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(valvePayload),
    })

    const data = await response.json()
    console.log('阀门 API 响应:', data)

    if (data.success || data.valve_dn) {
      valve.result = data
      ElMessage.success('阀门计算完成')
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
    console.error('阀门计算异常:', e)
    ElMessage.error('请求失败：' + e.message)
  } finally {
    valve.calculating = false
  }
}

// 删除阀门
const removeValve = (index) => {
  valves.value.splice(index, 1)
  saveToLocalStorage()
  ElMessage.success('已删除')
}

// 重置
const resetForm = () => {
  form.sourceNode = ''
  valves.value = []
  valveIdCounter = 0
  saveToLocalStorage()
  ElMessage.success('已重置')
}

// 更新阀门通径选项
const updateValveDnOptions = (valve) => {
  // 使用 Object.assign 确保响应式更新
  Object.assign(valve.designParams, {
    valveDnOptions: getValveDnOptions(valve.designParams.valveType),
    specifiedDn: '',  // 清空已选择的通径
  })
}
</script>

<style scoped>
.calculator-container { padding: 15px; }
.tool-title { color: #303133; margin-bottom: 8px; font-size: 20px; }
.tool-description { color: #666; margin-bottom: 15px; font-size: 13px; }
</style>
