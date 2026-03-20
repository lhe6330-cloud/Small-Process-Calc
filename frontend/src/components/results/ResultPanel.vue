<template>
  <el-card class="result-card" v-if="result">
    <template #header><span class="card-title">📊 计算结果</span></template>
    
    <!-- 错误提示 -->
    <el-alert
      v-if="result.error"
      title="⚠️ 程序计算错误，没有得到解"
      type="error"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    >
      <template #default>
        <p>{{ result.error_message || '请检查输入参数是否合理，或尝试调整参数范围。' }}</p>
      </template>
    </el-alert>
    
    <el-row :gutter="20" v-if="!result.error">
      <!-- 模式 1 和模式 2 才有换热器 -->
      <template v-if="activeMode === 'mode1' || activeMode === 'mode2'">
        <el-col :span="8">
          <el-statistic title="换热功率 (kW)" :value="result.heat_exchanger?.q_power?.toFixed(2) || 0" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="热边出口温度 (°C)" :value="result.heat_exchanger?.t_hot_out?.toFixed(1) || 0" />
        </el-col>
      </template>
      <el-col :span="8">
        <el-statistic title="涡轮轴功率 (kW)" :value="result.turbine?.power_shaft?.toFixed(2) || 0" />
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-statistic title="发电功率 (kW)" :value="result.turbine?.power_electric?.toFixed(2) || 0" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="涡轮出口温度 (°C)" :value="result.turbine?.t_out?.toFixed(1) || 0" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="出口含液率 (%)" :value="result.turbine?.liquid_percent !== null ? result.turbine.liquid_percent.toFixed(1) : '--'" :value-style="result.turbine?.liquid_percent > 5 ? { color: '#ff9800' } : {}" />
      </el-col>
    </el-row>

    <!-- 出口含液率警告 -->
    <el-alert
      v-if="result.turbine?.liquid_warning"
      :title="result.turbine.liquid_warning"
      type="warning"
      :closable="false"
      show-icon
      style="margin-top: 15px"
    />

    <el-row :gutter="20" style="margin-top: 15px;">
      <el-col :span="8">
        <el-statistic title="电机选型 (kW)" :value="result.selection?.motor || 0" />
      </el-col>
    </el-row>

    <el-divider />
    
    <el-row :gutter="20">
      <el-col :span="8">
        <div class="result-item">
          <div class="label">进口管道</div>
          <div class="value">DN{{ result.selection?.pipe_inlet?.recommended_dn }} (v={{ result.selection?.pipe_inlet?.velocity?.toFixed(1) }} m/s)</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="result-item">
          <div class="label">出口管道</div>
          <div class="value">DN{{ result.selection?.pipe_outlet?.recommended_dn }} (v={{ result.selection?.pipe_outlet?.velocity?.toFixed(1) }} m/s)</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="result-item">
          <div class="label">阀门</div>
          <div class="value">
            {{ result.selection?.valve?.valve_type === 'globe' ? '截止阀' : '蝶阀' }} DN{{ result.selection?.valve?.valve_dn }}
          </div>
          <div class="value" style="font-size: 12px; color: #666; margin-top: 4px;">
            Kv={{ result.selection?.valve?.kv_required?.toFixed(1) }} / {{ result.selection?.valve?.kv_rated }}
            开度={{ result.selection?.valve?.valve_opening?.toFixed(1) }}%
            <span :class="getStatusClass(result.selection?.valve?.check_status)">
              {{ getStatusMsg(result.selection?.valve) }}
            </span>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- V2.0 功能入口 -->
    <el-divider />
    
    <div class="v2-actions">
      <el-button type="info" @click="addSeparator" :disabled="separators.length >= 5">
        📐 添加分离器 ({{ separators.length }}/5)
      </el-button>
    </div>
    
    <el-divider />
    
    <div class="export-actions">
      <el-button type="success" @click="exportPDF" :loading="exporting.pdf">
        📄 导出 PDF
      </el-button>
      <el-button type="warning" @click="exportExcel" :loading="exporting.excel">
        📊 导出 Excel
      </el-button>
    </div>
  </el-card>
  
  <!-- 分离器设计区域 -->
  <el-card class="separator-section" v-if="separators.length > 0">
    <template #header>
      <span class="card-title">📐 流程节点分离器设计</span>
    </template>
    
    <div v-for="(sep, index) in separators" :key="sep.id" class="separator-item">
      <el-divider content-position="left">
        分离器 {{ index + 1 }}
        <el-button size="small" type="danger" @click="removeSeparator(index)" style="margin-left: 10px">删除</el-button>
      </el-divider>
      
      <el-form :model="sep" label-width="140px" size="small">
        <el-form-item label="数据来源" required>
          <el-select v-model="sep.nodeId" placeholder="请选择" style="width: 300px">
            <el-option
              v-for="node in availableNodes"
              :key="node.value"
              :label="node.label"
              :value="node.value"
            />
          </el-select>
          <el-button type="primary" size="small" @click="fetchNodeData(sep)" style="margin-left: 10px">
            📥 获取数据
          </el-button>
        </el-form-item>
        
        <!-- 节点工况显示 -->
        <el-card v-if="sep.nodeParams" class="node-params-card">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="位置">{{ sep.nodeId }}</el-descriptions-item>
            <el-descriptions-item label="压力">{{ sep.nodeParams.p }} MPa.G</el-descriptions-item>
            <el-descriptions-item label="温度">{{ sep.nodeParams.t }} °C</el-descriptions-item>
            <el-descriptions-item label="流量">{{ sep.nodeParams.flow_rate }} {{ sep.nodeParams.flow_unit }}</el-descriptions-item>
            <el-descriptions-item label="密度">{{ sep.nodeParams.rho }} kg/m³</el-descriptions-item>
            <el-descriptions-item label="粘度">{{ (sep.nodeParams.mu || 0.000018).toFixed(6) }} Pa·s</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <!-- 设计参数 -->
        <el-row :gutter="20" v-if="sep.nodeParams">
          <el-col :span="8">
            <el-form-item label="液滴粒径">
              <el-input-number v-model="sep.dropletSize" :min="10" :max="500" step="10" size="small" />
              <span style="margin-left: 5px">μm</span>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="长径比 L/D">
              <el-input-number v-model="sep.lengthRatio" :min="2" :max="5" :step="0.5" :precision="1" size="small" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分离器类型">
              <el-radio-group v-model="sep.separatorType" size="small">
                <el-radio label="vertical">立式</el-radio>
                <el-radio label="horizontal">卧式</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item v-if="sep.nodeParams">
          <el-button type="primary" @click="calculateSeparator(sep)" :loading="sep.calculating">
            🚀 开始计算
          </el-button>
        </el-form-item>
        
        <!-- 计算结果 -->
        <el-card v-if="sep.result" class="result-card" shadow="hover">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="分离器直径">{{ sep.result.diameter }} mm</el-descriptions-item>
            <el-descriptions-item label="分离器高度/长度">{{ sep.result.length }} mm</el-descriptions-item>
            <el-descriptions-item label="气体流速">{{ sep.result.gas_velocity }} m/s</el-descriptions-item>
            <el-descriptions-item label="液滴沉降速度">{{ sep.result.settling_velocity }} m/s</el-descriptions-item>
            <el-descriptions-item label="液体停留时间">{{ sep.result.residence_time }} s</el-descriptions-item>
            <el-descriptions-item label="液封高度">{{ sep.result.liquid_height }} mm</el-descriptions-item>
          </el-descriptions>
          <el-alert 
            :title="sep.result.message" 
            :type="sep.result.check_passed ? 'success' : 'warning'"
            :closable="false"
            show-icon
            style="margin-top: 10px"
          />
        </el-card>
      </el-form>
    </div>
  </el-card>
  
  <!-- 涡轮一维设计区域 -->
  <el-card class="turbine-section" v-if="turbine1d.show">
    <template #header>
      <span class="card-title">⚙️ 涡轮一维通流设计</span>
    </template>
    
    <el-form :model="turbine1d" label-width="140px">
      <el-form-item label="数据来源">
        <el-tag>{{ turbine1d.sourceLabel }}</el-tag>
      </el-form-item>
      
      <!-- 涡轮参数（只读） -->
      <el-divider content-position="left">📊 涡轮参数（从 {{ turbine1d.sourceLabel }} 带入）</el-divider>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="流量">
            <el-input :value="turbine1d.params.flow_rate + ' ' + turbine1d.params.flow_unit" disabled size="small" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="介质">
            <el-input :value="turbine1d.params.medium" disabled size="small" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="进口压力">
            <el-input :value="turbine1d.params.p_in + ' MPa.G'" disabled size="small" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="出口压力">
            <el-input :value="turbine1d.params.p_out + ' MPa.G'" disabled size="small" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="进口温度">
            <el-input :value="turbine1d.params.t_in + ' °C'" disabled size="small" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="出口温度">
            <el-input :value="turbine1d.params.t_out + ' °C'" disabled size="small" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="轴功率">
            <el-input :value="turbine1d.params.power_shaft + ' kW'" disabled size="small" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="电功率">
            <el-input :value="(turbine1d.params.power_electric || 0) + ' kW'" disabled size="small" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 设计参数 -->
      <el-divider content-position="left">⚙️ 设计参数（可编辑）</el-divider>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="转速 n" required>
            <el-input-number v-model="turbine1d.design.speedRpm" :min="1000" :max="20000" step="500" size="small" />
            <span style="margin-left: 5px">rpm</span>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="叶片数 Z" required>
            <el-input-number v-model="turbine1d.design.bladeCount" :min="9" :max="21" step="1" size="small" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="速比 u/C₀" required>
            <el-input-number v-model="turbine1d.design.speedRatio" :min="0.6" :max="0.75" :step="0.01" :precision="2" size="small" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="反动度 Ω" required>
            <el-input-number v-model="turbine1d.design.reaction" :min="0" :max="100" step="5" size="small" />
            <span style="margin-left: 5px">%</span>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item>
        <el-button type="primary" @click="calculateTurbine" :loading="turbine1d.calculating">
          🚀 开始计算
        </el-button>
      </el-form-item>
      
      <!-- 计算结果 -->
      <el-card v-if="turbine1d.result" class="result-card" shadow="hover">
        <h4>📐 基本尺寸</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="叶轮外径 D₁">{{ turbine1d.result.dimensions?.D1 }} mm</el-descriptions-item>
          <el-descriptions-item label="叶轮内径 D₂">{{ turbine1d.result.dimensions?.D2 }} mm</el-descriptions-item>
          <el-descriptions-item label="进口叶片高度 b₁">{{ turbine1d.result.dimensions?.b1 }} mm</el-descriptions-item>
          <el-descriptions-item label="出口叶片高度 b₂">{{ turbine1d.result.dimensions?.b2 }} mm</el-descriptions-item>
          <el-descriptions-item label="叶片数 Z" :span="2">{{ turbine1d.result.dimensions?.Z }}</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 15px">🔺 速度三角形 - 进口</h4>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="C₁">{{ turbine1d.result.velocity_triangle_in?.C1 }} m/s</el-descriptions-item>
          <el-descriptions-item label="W₁">{{ turbine1d.result.velocity_triangle_in?.W1 }} m/s</el-descriptions-item>
          <el-descriptions-item label="U₁">{{ turbine1d.result.velocity_triangle_in?.U1 }} m/s</el-descriptions-item>
          <el-descriptions-item label="α₁">{{ turbine1d.result.velocity_triangle_in?.alpha1 }}°</el-descriptions-item>
          <el-descriptions-item label="β₁">{{ turbine1d.result.velocity_triangle_in?.beta1 }}°</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 15px">🔺 速度三角形 - 出口</h4>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="C₂">{{ turbine1d.result.velocity_triangle_out?.C2 }} m/s</el-descriptions-item>
          <el-descriptions-item label="W₂">{{ turbine1d.result.velocity_triangle_out?.W2 }} m/s</el-descriptions-item>
          <el-descriptions-item label="U₂">{{ turbine1d.result.velocity_triangle_out?.U2 }} m/s</el-descriptions-item>
          <el-descriptions-item label="α₂">{{ turbine1d.result.velocity_triangle_out?.alpha2 }}°</el-descriptions-item>
          <el-descriptions-item label="β₂">{{ turbine1d.result.velocity_triangle_out?.beta2 }}°</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 15px">🔥 热力参数</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="级效率 η">{{ turbine1d.result.thermo_params?.eta }}%</el-descriptions-item>
          <el-descriptions-item label="反动度 Ω">{{ turbine1d.result.thermo_params?.omega }}%</el-descriptions-item>
          <el-descriptions-item label="速比 u/C₀">{{ turbine1d.result.thermo_params?.speed_ratio }}</el-descriptions-item>
          <el-descriptions-item label="计算功率">{{ turbine1d.result.performance?.P_calc }} kW</el-descriptions-item>
        </el-descriptions>
        
        <el-alert 
          :title="turbine1d.result.message" 
          type="success"
          :closable="false"
          show-icon
          style="margin-top: 10px"
        />
      </el-card>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps(['result', 'activeMode'])

const exporting = ref({ pdf: false, excel: false })

// 阀门状态样式
const getStatusClass = (status) => {
  if (!status) return ''
  return 'status-' + status
}

// 阀门状态文字
const getStatusMsg = (valve) => {
  if (!valve) return ''
  return valve.status_msg || ''
}

// 多分离器支持
const separators = ref([])
let separatorIdCounter = 0

// 可用节点（按模式过滤）
const availableNodes = computed(() => {
  const mode = props.activeMode
  if (mode === 'mode1') {
    return [
      { label: '模式 1 - 冷边入口', value: 'mode1_cold_inlet' },
      { label: '模式 1 - 换热器出口', value: 'mode1_hx_out' },
      { label: '模式 1 - 涡轮出口', value: 'mode1_turbine_out' },
    ]
  }
  if (mode === 'mode2') {
    return [
      { label: '模式 2 - 涡轮入口', value: 'mode2_turbine_in' },
      { label: '模式 2 - 涡轮出口', value: 'mode2_turbine_out' },
      { label: '模式 2 - 换热器出口', value: 'mode2_hx_out' },
    ]
  }
  if (mode === 'mode3') {
    return [
      { label: '模式 3 - 涡轮入口', value: 'mode3_turbine_in' },
      { label: '模式 3 - 涡轮出口', value: 'mode3_turbine_out' },
    ]
  }
  return []
})

// 涡轮一维设计
const turbine1d = reactive({
  show: true,  // 自动展开
  sourceLabel: computed(() => {
    const mode = props.activeMode
    if (mode === 'mode1') return '模式 1 - 涡轮膨胀机'
    if (mode === 'mode2') return '模式 2 - 涡轮膨胀机'
    if (mode === 'mode3') return '模式 3 - 涡轮膨胀机'
    return ''
  }),
  params: computed(() => {
    const result = props.result || {}
    const turbine = result.turbine || {}
    
    // 介质名称转换
    const mediumMap = {
      'H2O': '水/水蒸气',
      'N2': 'N₂',
      'O2': 'O₂',
      'CO2': 'CO₂',
      'H2': 'H₂',
      'Air': '空气',
    }
    
    // 处理混合介质
    let mediumName = 'N₂'
    if (turbine.medium_type === 'mix' && turbine.mix_composition) {
      // 混合介质：显示组分
      const components = Object.entries(turbine.mix_composition)
        .filter(([_, value]) => value > 0.01)  // 只显示含量>1%的组分
        .map(([key, value]) => {
          const name = mediumMap[key] || key
          // value 可能是 0.7（需要*100）或 70（直接使用），判断一下
          const percent = value > 1 ? value : value * 100
          return `${name}: ${percent.toFixed(1)}%`
        })
      mediumName = `混合介质 (${components.join(', ')})`
    } else {
      // 单一介质
      mediumName = mediumMap[turbine.medium || 'N2'] || turbine.medium || 'N₂'
    }
    
    return {
      flow_rate: turbine.flow_rate || 1000,
      flow_unit: turbine.flow_unit || 'Nm3/h',
      medium: mediumName,
      medium_type: turbine.medium_type || 'single',
      mix_composition: turbine.mix_composition,
      p_in: turbine.p_in || 0.5,
      p_out: turbine.p_out || 0.1,
      t_in: turbine.t_in || 200,
      t_out: turbine.t_out || 85,
      rho_in: turbine.rho_in || 4.5,
      rho_out: turbine.rho_out || 1.2,
      power_shaft: turbine.power_shaft || 0,
      power_electric: turbine.power_electric || 0,
    }
  }),
  design: {
    speedRpm: 3000,
    bladeCount: 13,
    speedRatio: 0.65,
    reaction: 50,
  },
  calculating: false,
  result: null,
})

// 添加分离器
const addSeparator = () => {
  if (separators.value.length >= 5) {
    ElMessage.warning('最多支持 5 个分离器')
    return
  }
  
  separators.value.push({
    id: ++separatorIdCounter,
    nodeId: '',
    nodeParams: null,
    dropletSize: 100,
    lengthRatio: 3.0,
    separatorType: 'vertical',
    calculating: false,
    result: null,
  })
  
  ElMessage.success('已添加分离器 ' + (separators.value.length))
}

// 删除分离器
const removeSeparator = (index) => {
  separators.value.splice(index, 1)
  ElMessage.success('已删除分离器')
}

// 获取节点数据
const fetchNodeData = async (sep) => {
  if (!sep.nodeId) {
    ElMessage.warning('请先选择数据来源')
    return
  }
  
  // 从 localStorage 获取数据
  const mode = props.activeMode
  const storedData = localStorage.getItem('lastInputData_' + mode)
  
  if (storedData) {
    try {
      const data = JSON.parse(storedData)
      const turbine = data.turbine || {}
      
      sep.nodeParams = {
        p: turbine.p_out || 0.1,
        t: turbine.t_out || 100,
        flow_rate: 1000,
        flow_unit: 'Nm3/h',
        rho: turbine.rho_out || 1.2,
        mu: 1.8e-5,
      }
      
      ElMessage.success('数据获取成功')
    } catch (e) {
      ElMessage.error('数据解析失败')
    }
  } else {
    ElMessage.warning('未找到历史数据，请使用默认值')
    sep.nodeParams = {
      p: 0.1,
      t: 100,
      flow_rate: 1000,
      flow_unit: 'Nm3/h',
      rho: 1.2,
      mu: 1.8e-5,
    }
  }
}

// 计算分离器
const calculateSeparator = async (sep) => {
  if (!sep.nodeParams) {
    ElMessage.warning('请先获取节点数据')
    return
  }
  
  sep.calculating = true
  
  try {
    const response = await fetch('http://localhost:8000/api/calculate/separator', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: props.activeMode,
        node_id: sep.nodeId,
        node_params: sep.nodeParams,
        droplet_size: sep.dropletSize,
        length_ratio: sep.lengthRatio,
        separator_type: sep.separatorType,
        residence_time_req: 180,
      }),
    })
    
    const data = await response.json()
    if (data.success) {
      sep.result = data
      ElMessage.success('分离器计算完成')
    } else {
      ElMessage.error('计算失败：' + data.message)
    }
  } catch (e) {
    ElMessage.error('请求失败：' + e.message)
  } finally {
    sep.calculating = false
  }
}

// 计算涡轮
const calculateTurbine = async () => {
  turbine1d.calculating = true
  
  try {
    const response = await fetch('http://localhost:8000/api/calculate/mode5', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: props.activeMode,
        flow_rate: turbine1d.params.flow_rate,
        flow_unit: turbine1d.params.flow_unit,
        p_in: turbine1d.params.p_in,
        p_out: turbine1d.params.p_out,
        t_in: turbine1d.params.t_in,
        t_out: turbine1d.params.t_out,
        rho_in: turbine1d.params.rho_in,
        rho_out: turbine1d.params.rho_out,
        power_shaft: turbine1d.params.power_shaft,
        speed_rpm: turbine1d.design.speedRpm,
        blade_count: turbine1d.design.bladeCount,
        speed_ratio: turbine1d.design.speedRatio,
        reaction: turbine1d.design.reaction,
      }),
    })
    
    const data = await response.json()
    if (data.success) {
      turbine1d.result = data
      ElMessage.success('涡轮一维设计计算完成')
    } else {
      ElMessage.error('计算失败：' + data.message)
    }
  } catch (e) {
    ElMessage.error('请求失败：' + e.message)
  } finally {
    turbine1d.calculating = false
  }
}

// 导出 PDF
const exportPDF = async () => {
  exporting.value.pdf = true

  try {
    const mode = props.activeMode
    // 根据模式读取正确的 localStorage key
    const storageKey = 'lastInputData_' + mode
    const inputData = localStorage.getItem(storageKey)
    const input = inputData ? JSON.parse(inputData) : null

    if (!input) {
      ElMessage.error('未找到输入数据，请先进行计算')
      return
    }

    // 构建完整的请求数据
    const requestData = { ...input }

    // 添加 V2.0 功能数据
    requestData.separators = separators.value.filter(s => s.result).map(s => ({
      node_id: s.nodeId,
      node_params: s.nodeParams,
      design_params: {
        dropletSize: s.dropletSize,
        lengthRatio: s.lengthRatio,
        separatorType: s.separatorType,
      },
      result: s.result,
    }))

    requestData.turbine_1d = turbine1d.result ? {
      design_params: { ...turbine1d.design },
      result: turbine1d.result,
    } : null

    const response = await fetch(`http://localhost:8000/api/export/pdf/${mode}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData),
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error)
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${mode.toUpperCase()}_${new Date().getTime()}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElMessage.success('✅ PDF 导出成功')
  } catch (e) {
    ElMessage.error('❌ PDF 导出失败：' + e.message)
  } finally {
    exporting.value.pdf = false
  }
}

// 导出 Excel
const exportExcel = async () => {
  exporting.value.excel = true

  try {
    const mode = props.activeMode
    // 根据模式读取正确的 localStorage key
    const storageKey = 'lastInputData_' + mode
    const inputData = localStorage.getItem(storageKey)
    const input = inputData ? JSON.parse(inputData) : null

    if (!input) {
      ElMessage.error('未找到输入数据，请先进行计算')
      return
    }

    // 构建完整的请求数据
    const requestData = { ...input }

    // 添加 V2.0 功能数据
    requestData.separators = separators.value.filter(s => s.result).map(s => ({
      node_id: s.nodeId,
      node_params: s.nodeParams,
      design_params: {
        dropletSize: s.dropletSize,
        lengthRatio: s.lengthRatio,
        separatorType: s.separatorType,
      },
      result: s.result,
    }))

    requestData.turbine_1d = turbine1d.result ? {
      design_params: { ...turbine1d.design },
      result: turbine1d.result,
    } : null

    const response = await fetch(`http://localhost:8000/api/export/excel/${mode}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData),
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error)
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${mode.toUpperCase()}_${new Date().getTime()}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElMessage.success('✅ Excel 导出成功')
  } catch (e) {
    ElMessage.error('❌ Excel 导出失败：' + e.message)
  } finally {
    exporting.value.excel = false
  }
}
</script>

<style scoped>
.result-card { margin-bottom: 20px; background: #ffffff; border: 1px solid #dcdfe6; }
.card-title { font-weight: 600; color: #303133; }
.v2-actions, .export-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.separator-section, .turbine-section { margin-top: 20px; background: #ffffff; border: 1px solid #dcdfe6; }
.separator-item { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #e4e7ed; }
.separator-item:last-child { border-bottom: none; }
.node-params-card, .result-card { margin-top: 10px; background: #f5f7fa; }
h4 { color: #303133; margin: 15px 0 10px 0; font-size: 14px; }
.status-ok { color: #67c23a; }
.status-warning { color: #e6a23c; }
.status-fail { color: #f56c6c; }
</style>
