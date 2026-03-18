<template>
  <div class="mode4-container">
    <h2>📐 流程节点分离器设计</h2>
    <p class="description">基于 Stokes 沉降定律的重力沉降式气液分离器设计</p>
    
    <el-card class="form-card">
      <el-form :model="form" label-width="140px">
        <el-form-item label="数据来源" required>
          <el-select v-model="form.sourceNode" placeholder="请选择流程节点位置" style="width: 100%">
            <el-option-group label="模式 1 - 先加热再膨胀">
              <el-option label="模式 1 - 冷边入口" value="mode1_cold_inlet" />
              <el-option label="模式 1 - 换热器入口" value="mode1_hx_in" />
              <el-option label="模式 1 - 换热器出口" value="mode1_hx_out" />
              <el-option label="模式 1 - 涡轮入口" value="mode1_turbine_in" />
              <el-option label="模式 1 - 涡轮出口" value="mode1_turbine_out" />
              <el-option label="模式 1 - 总出口" value="mode1_outlet" />
            </el-option-group>
            <el-option-group label="模式 2 - 先膨胀后回热">
              <el-option label="模式 2 - 冷边入口" value="mode2_cold_inlet" />
              <el-option label="模式 2 - 涡轮入口" value="mode2_turbine_in" />
              <el-option label="模式 2 - 涡轮出口" value="mode2_turbine_out" />
              <el-option label="模式 2 - 换热器入口" value="mode2_hx_in" />
              <el-option label="模式 2 - 换热器出口" value="mode2_hx_out" />
              <el-option label="模式 2 - 总出口" value="mode2_outlet" />
            </el-option-group>
            <el-option-group label="模式 3 - 直接膨胀">
              <el-option label="模式 3 - 冷边入口" value="mode3_cold_inlet" />
              <el-option label="模式 3 - 涡轮入口" value="mode3_turbine_in" />
              <el-option label="模式 3 - 涡轮出口" value="mode3_turbine_out" />
              <el-option label="模式 3 - 总出口" value="mode3_outlet" />
            </el-option-group>
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="fetchData" :loading="fetching">
            📥 获取数据
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 节点工况显示 -->
    <el-card class="data-card" v-if="nodeParams">
      <template #header>
        <span class="card-title">📊 节点工况参数</span>
        <el-tag type="success">已加载</el-tag>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="位置">{{ form.sourceNode }}</el-descriptions-item>
        <el-descriptions-item label="压力">{{ nodeParams.p }} MPa.G</el-descriptions-item>
        <el-descriptions-item label="温度">{{ nodeParams.t }} °C</el-descriptions-item>
        <el-descriptions-item label="流量">{{ nodeParams.flow_rate }} {{ nodeParams.flow_unit }}</el-descriptions-item>
        <el-descriptions-item label="介质" :span="2">{{ nodeParams.medium || 'N₂' }}</el-descriptions-item>
        <el-descriptions-item label="密度">{{ nodeParams.rho }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="粘度">{{ (nodeParams.mu || 0.000018).toFixed(6) }} Pa·s</el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <!-- 设计参数 -->
    <el-card class="design-card" v-if="nodeParams">
      <template #header>
        <span class="card-title">⚙️ 设计参数</span>
      </template>
      
      <el-form :model="designParams" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设计液滴粒径">
              <el-input-number v-model="designParams.dropletSize" :min="10" :max="500" step="10" />
              <span style="margin-left: 10px">μm</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="长径比 L/D">
              <el-input-number v-model="designParams.lengthRatio" :min="2" :max="5" :step="0.5" :precision="1" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分离器类型">
              <el-radio-group v-model="designParams.separatorType">
                <el-radio label="vertical">立式</el-radio>
                <el-radio label="horizontal">卧式</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="要求停留时间">
              <el-input-number v-model="designParams.residenceTime" :min="60" :max="600" step="30" />
              <span style="margin-left: 10px">s</span>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button type="primary" @click="calculateSeparator" :loading="calculating">
            🚀 开始计算
          </el-button>
          <el-button @click="exportPDF" :loading="exporting">📄 导出 PDF</el-button>
          <el-button @click="exportExcel" :loading="exporting">📊 导出 Excel</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 计算结果 -->
    <el-card class="result-card" v-if="separatorResult">
      <template #header>
        <span class="card-title">📊 计算结果</span>
        <el-tag :type="separatorResult.check_passed ? 'success' : 'warning'">
          {{ separatorResult.check_passed ? '✅ 满足要求' : '⚠️ 需调整参数' }}
        </el-tag>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="分离器直径">{{ separatorResult.diameter }} mm</el-descriptions-item>
        <el-descriptions-item label="分离器高度/长度">{{ separatorResult.length }} mm</el-descriptions-item>
        <el-descriptions-item label="气体流速">{{ separatorResult.gas_velocity }} m/s</el-descriptions-item>
        <el-descriptions-item label="液滴沉降速度">{{ separatorResult.settling_velocity }} m/s</el-descriptions-item>
        <el-descriptions-item label="液体停留时间">{{ separatorResult.residence_time }} s</el-descriptions-item>
        <el-descriptions-item label="液封高度">{{ separatorResult.liquid_height }} mm</el-descriptions-item>
      </el-descriptions>
      
      <el-alert 
        :title="separatorResult.message" 
        :type="separatorResult.check_passed ? 'success' : 'warning'"
        :closable="false"
        show-icon
        style="margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const form = reactive({
  sourceNode: '',
})

const fetching = ref(false)
const calculating = ref(false)
const exporting = ref(false)
const nodeParams = ref(null)
const separatorResult = ref(null)

const designParams = reactive({
  dropletSize: 100,
  lengthRatio: 3.0,
  separatorType: 'vertical',
  residenceTime: 180,
})

// 模拟数据（实际应从 localStorage 或 API 获取）
const mockResults = {
  mode1_cold_inlet: { p: 0.5, t: 20, flow_rate: 1000, flow_unit: 'Nm3/h', medium: 'N₂', rho: 4.5, mu: 1.8e-5 },
  mode1_hx_out: { p: 0.48, t: 200, flow_rate: 1000, flow_unit: 'Nm3/h', medium: 'N₂', rho: 1.25, mu: 2.5e-5 },
  mode1_turbine_out: { p: 0.1, t: 85, flow_rate: 1000, flow_unit: 'Nm3/h', medium: 'N₂', rho: 1.2, mu: 1.8e-5 },
  mode2_turbine_out: { p: 0.1, t: 100, flow_rate: 1000, flow_unit: 'Nm3/h', medium: 'N₂', rho: 1.2, mu: 1.8e-5 },
  mode3_turbine_out: { p: 0.1, t: 90, flow_rate: 1000, flow_unit: 'Nm3/h', medium: 'N₂', rho: 1.2, mu: 1.8e-5 },
}

const fetchData = async () => {
  if (!form.sourceNode) {
    ElMessage.warning('请先选择数据来源')
    return
  }
  
  fetching.value = true
  
  try {
    // 尝试从 localStorage 获取真实数据
    const storedData = localStorage.getItem('lastInputData_' + form.sourceNode.split('_')[0])
    const result = JSON.parse(storedData)
    
    if (result && result.turbine) {
      // 从真实计算结果中提取
      nodeParams.value = {
        p: result.turbine.p_out || 0.1,
        t: result.turbine.t_out || 100,
        flow_rate: result.turbine.flow_rate || 1000,
        flow_unit: 'Nm3/h',
        medium: 'N₂',
        rho: result.turbine.rho_out || 1.2,
        mu: 1.8e-5,
      }
      ElMessage.success('数据获取成功')
    } else if (mockResults[form.sourceNode]) {
      // 使用模拟数据
      nodeParams.value = mockResults[form.sourceNode]
      ElMessage.success('数据获取成功（模拟数据）')
    } else {
      // 数据为空
      ElMessage.error('您选择了错误的位置，该位置暂无可用数据')
      nodeParams.value = null
    }
  } catch (e) {
    // 使用模拟数据作为 fallback
    if (mockResults[form.sourceNode]) {
      nodeParams.value = mockResults[form.sourceNode]
      ElMessage.warning('未找到历史数据，已加载模拟数据')
    } else {
      ElMessage.error('您选择了错误的位置，该位置暂无可用数据')
      nodeParams.value = null
    }
  } finally {
    fetching.value = false
  }
}

const calculateSeparator = async () => {
  if (!nodeParams.value) {
    ElMessage.warning('请先获取节点工况数据')
    return
  }
  
  calculating.value = true
  
  try {
    const response = await fetch('http://localhost:8000/api/calculate/separator', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: form.sourceNode.split('_')[0],
        node_id: form.sourceNode,
        node_params: nodeParams.value,
        droplet_size: designParams.dropletSize,
        length_ratio: designParams.lengthRatio,
        separator_type: designParams.separatorType,
        residence_time_req: designParams.residenceTime,
      }),
    })
    
    const data = await response.json()
    if (data.success) {
      separatorResult.value = data
      ElMessage.success('分离器计算完成')
    } else {
      ElMessage.error('计算失败：' + data.message)
    }
  } catch (e) {
    ElMessage.error('请求失败：' + e.message)
  } finally {
    calculating.value = false
  }
}

const resetForm = () => {
  form.sourceNode = ''
  nodeParams.value = null
  separatorResult.value = null
}

const exportPDF = () => {
  ElMessage.info('PDF 导出功能开发中...')
}

const exportExcel = () => {
  ElMessage.info('Excel 导出功能开发中...')
}
</script>

<style scoped>
.mode4-container { padding: 20px; }
h2 { color: #00D4FF; margin-bottom: 10px; }
.description { color: #94A3B8; margin-bottom: 20px; }
.form-card, .data-card, .design-card, .result-card { margin-bottom: 20px; }
.card-title { font-weight: 600; color: #F1F5F9; }
</style>
