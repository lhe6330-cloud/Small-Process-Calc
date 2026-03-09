<template>
  <el-dialog v-model="dialogVisible" title="📐 流程节点分离器设计" width="900px" :close-on-click-modal="false">
    <!-- 步骤 1：选择添加位置 -->
    <el-steps :active="currentStep" finish-status="success" align-center style="margin-bottom: 20px">
      <el-step title="选择位置" />
      <el-step title="节点工况" />
      <el-step title="气液平衡" />
      <el-step title="设计参数" />
    </el-steps>
    
    <!-- 步骤 1：选择位置 -->
    <div v-if="currentStep === 0">
      <h4>步骤 1：选择添加位置</h4>
      <p class="step-desc">选择要添加分离器的流程节点位置</p>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="当前模式">
          <el-tag>{{ modeName }}</el-tag>
        </el-form-item>
        
        <el-form-item label="添加位置" required>
          <el-radio-group v-model="form.nodeId">
            <div v-for="node in nodes" :key="node.id" style="margin: 10px 0">
              <el-radio :label="node.id" border style="padding: 10px 20px; width: 100%">
                <div style="display: flex; align-items: center">
                  <span style="font-weight: 500">{{ node.name }}</span>
                  <el-tag size="small" style="margin-left: 10px">{{ node.position }}</el-tag>
                </div>
              </el-radio>
            </div>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <div style="text-align: right; margin-top: 20px">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="nextStep" :disabled="!form.nodeId">下一步</el-button>
      </div>
    </div>
    
    <!-- 步骤 2：节点工况 -->
    <div v-if="currentStep === 1">
      <h4>步骤 2：节点工况（自动带入，只读）</h4>
      <p class="step-desc">从 {{ selectedNode?.name }} 带入的工况参数</p>
      
      <el-card>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="位置">{{ selectedNode?.name }}</el-descriptions-item>
          <el-descriptions-item label="压力">{{ nodeParams.p }} MPa.G</el-descriptions-item>
          <el-descriptions-item label="温度">{{ nodeParams.t }} °C</el-descriptions-item>
          <el-descriptions-item label="流量">{{ nodeParams.flow_rate }} {{ nodeParams.flow_unit }}</el-descriptions-item>
          <el-descriptions-item label="介质" :span="2">{{ mediumDisplay }}</el-descriptions-item>
          <el-descriptions-item label="密度">{{ nodeParams.rho }} kg/m³</el-descriptions-item>
          <el-descriptions-item label="粘度">{{ (nodeParams.mu || 0.000018).toFixed(6) }} Pa·s</el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <div style="text-align: right; margin-top: 20px">
        <el-button @click="currentStep--">上一步</el-button>
        <el-button type="primary" @click="nextStep">下一步</el-button>
      </div>
    </div>
    
    <!-- 步骤 3：气液平衡 -->
    <div v-if="currentStep === 2">
      <h4>步骤 3：气液平衡计算（自动）</h4>
      <p class="step-desc">{{ hasWater ? '含 H₂O 工况，自动计算冷凝液量' : '不含 H₂O，无冷凝液' }}</p>
      
      <el-card v-if="vleLoading" style="text-align: center; padding: 40px">
        <el-skeleton :rows="3" animated />
      </el-card>
      
      <el-card v-else-if="vleResult">
        <el-alert 
          :title="vleResult.skip ? '不含 H₂O，跳过气液平衡计算' : '气液平衡计算完成'"
          :type="vleResult.skip ? 'info' : 'success'"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />
        
        <el-descriptions :column="2" border v-if="!vleResult.skip">
          <el-descriptions-item label="气相分率（干度）">{{ (vleResult.vapor_frac * 100).toFixed(1) }} %</el-descriptions-item>
          <el-descriptions-item label="液相分率（含液率）">{{ (vleResult.liquid_frac * 100).toFixed(1) }} %</el-descriptions-item>
          <el-descriptions-item label="冷凝液流量">{{ vleResult.liquid_flow }} T/h</el-descriptions-item>
          <el-descriptions-item label="气相流量">{{ vleResult.vapor_flow }} T/h</el-descriptions-item>
          <el-descriptions-item label="液相密度">{{ vleResult.rho_liquid }} kg/m³</el-descriptions-item>
          <el-descriptions-item label="气相密度">{{ vleResult.rho_vapor }} kg/m³</el-descriptions-item>
          <el-descriptions-item label="气相粘度" :span="2">{{ (vleResult.mu_vapor || 0).toFixed(6) }} Pa·s</el-descriptions-item>
        </el-descriptions>
        
        <el-descriptions :column="2" border v-else>
          <el-descriptions-item label="工况">纯气相，无冷凝液</el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <div style="text-align: right; margin-top: 20px">
        <el-button @click="currentStep--">上一步</el-button>
        <el-button type="primary" @click="nextStep">下一步</el-button>
      </div>
    </div>
    
    <!-- 步骤 4：设计参数 -->
    <div v-if="currentStep === 3">
      <h4>步骤 4：设计参数（用户输入）</h4>
      <p class="step-desc">输入分离器设计参数</p>
      
      <el-form :model="form" label-width="140px">
        <el-form-item label="设计液滴粒径" required>
          <el-input-number v-model="form.dropletSize" :min="10" :max="500" step="10" />
          <span style="margin-left: 10px">μm</span>
          <p class="form-tip">推荐值：50-200 μm，越小分离效果越好但设备越大</p>
        </el-form-item>
        
        <el-form-item label="长径比 L/D" required>
          <el-input-number v-model="form.lengthRatio" :min="2" :max="5" step="0.5" />
          <p class="form-tip">推荐值：2-5，常用 3-4</p>
        </el-form-item>
        
        <el-form-item label="分离器类型" required>
          <el-radio-group v-model="form.separatorType">
            <el-radio label="vertical">立式</el-radio>
            <el-radio label="horizontal">卧式</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="液体停留时间" required>
          <el-input-number v-model="form.residenceTimeReq" :min="60" :max="600" step="30" />
          <span style="margin-left: 10px">s</span>
          <p class="form-tip">推荐值：180-300 s</p>
        </el-form-item>
      </el-form>
      
      <div style="text-align: right; margin-top: 20px">
        <el-button @click="currentStep--">上一步</el-button>
        <el-button type="primary" @click="calculateSeparator" :loading="calculating">计算</el-button>
      </div>
    </div>
    
    <!-- 计算结果 -->
    <div v-if="calcResult" style="margin-top: 20px">
      <el-divider />
      <h4>计算结果</h4>
      
      <el-alert 
        :title="calcResult.check_passed ? '✅ 满足停留时间要求' : '⚠️ 停留时间不足，建议增大分离器尺寸'"
        :type="calcResult.check_passed ? 'success' : 'warning'"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />
      
      <el-card>
        <el-descriptions :column="2" border title="分离器尺寸">
          <el-descriptions-item label="分离器直径">{{ calcResult.diameter }} mm</el-descriptions-item>
          <el-descriptions-item label="分离器{{ form.separatorType === 'vertical' ? '高度' : '长度' }}">{{ calcResult.length }} mm</el-descriptions-item>
          <el-descriptions-item label="液封高度">{{ calcResult.liquid_height }} mm</el-descriptions-item>
        </el-descriptions>
        
        <el-descriptions :column="2" border title="性能参数" style="margin-top: 15px">
          <el-descriptions-item label="气体流速">{{ calcResult.gas_velocity }} m/s</el-descriptions-item>
          <el-descriptions-item label="液滴沉降速度">{{ calcResult.settling_velocity }} m/s</el-descriptions-item>
          <el-descriptions-item label="液体停留时间" :span="2">{{ calcResult.residence_time }} s</el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <div style="text-align: right; margin-top: 20px">
        <el-button @click="calcResult = null">重新计算</el-button>
        <el-button type="success" @click="confirmAdd">确认添加</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps(['modelValue', 'sourceMode', 'nodeParams'])
const emit = defineEmits(['update:modelValue', 'add-separator'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const currentStep = ref(0)
const calculating = ref(false)
const vleLoading = ref(false)
const vleResult = ref(null)
const calcResult = ref(null)

const form = ref({
  nodeId: '',
  dropletSize: 100,
  lengthRatio: 3.0,
  separatorType: 'vertical',
  residenceTimeReq: 180,
})

// 模式节点定义
const NODES = {
  mode1: [
    { id: 'hx_in', name: '换热器入口', position: 'before_hx' },
    { id: 'hx_out', name: '换热器出口', position: 'after_hx' },
    { id: 'turbine_in', name: '涡轮入口', position: 'before_turbine' },
    { id: 'turbine_out', name: '涡轮出口', position: 'after_turbine' },
    { id: 'outlet', name: '总出口', position: 'end' },
  ],
  mode2: [
    { id: 'turbine_in', name: '涡轮入口', position: 'before_turbine' },
    { id: 'turbine_out', name: '涡轮出口', position: 'after_turbine' },
    { id: 'hx_in', name: '换热器入口', position: 'before_hx' },
    { id: 'hx_out', name: '换热器出口', position: 'after_hx' },
    { id: 'outlet', name: '总出口', position: 'end' },
  ],
  mode3: [
    { id: 'turbine_in', name: '涡轮入口', position: 'before_turbine' },
    { id: 'turbine_out', name: '涡轮出口', position: 'after_turbine' },
    { id: 'outlet', name: '总出口', position: 'end' },
  ],
}

const MODE_NAMES = {
  mode1: '模式 1：先加热再膨胀',
  mode2: '模式 2：先膨胀后回热',
  mode3: '模式 3：直接膨胀',
}

const nodes = computed(() => NODES[props.sourceMode] || [])
const modeName = computed(() => MODE_NAMES[props.sourceMode] || props.sourceMode)
const selectedNode = computed(() => nodes.value.find(n => n.id === form.value.nodeId))

const nodeParams = ref({
  p: 0.5,
  t: 200,
  flow_rate: 1000,
  flow_unit: 'Nm3/h',
  rho: 1.25,
  mu: 1.8e-5,
  medium: 'N2',
  composition: { N2: 1.0 },
})

// 监听 nodeParams 变化
watch(() => props.nodeParams, (newParams) => {
  if (newParams) {
    nodeParams.value = { ...nodeParams.value, ...newParams }
  }
}, { immediate: true })

const mediumDisplay = computed(() => {
  const comp = nodeParams.value.composition || {}
  const parts = Object.entries(comp)
    .filter(([_, v]) => v > 0.01)
    .map(([k, v]) => `${k}(${(v * 100).toFixed(0)}%)`)
  return parts.join(' + ') || nodeParams.value.medium || '-'
})

const hasWater = computed(() => {
  const comp = nodeParams.value.composition || {}
  return comp.H2O && comp.H2O > 0.001
})

const nextStep = async () => {
  if (currentStep.value === 1) {
    // 进入步骤 3 前，执行 VLE 计算
    vleLoading.value = true
    try {
      const response = await fetch('/api/vle/calc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          p: nodeParams.value.p,
          t: nodeParams.value.t,
          composition: nodeParams.value.composition || { N2: 1.0 },
          total_flow: nodeParams.value.flow_rate,
          flow_unit: nodeParams.value.flow_unit,
        }),
      })
      vleResult.value = await response.json()
    } catch (e) {
      console.error('VLE calc failed:', e)
      vleResult.value = { skip: true, message: '计算失败' }
    } finally {
      vleLoading.value = false
    }
  }
  currentStep.value++
}

const calculateSeparator = async () => {
  calculating.value = true
  try {
    const response = await fetch('/api/calculate/separator', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: props.sourceMode,
        node_id: form.value.nodeId,
        node_params: nodeParams.value,
        vle_result: vleResult.value,
        droplet_size: form.value.dropletSize,
        length_ratio: form.value.lengthRatio,
        separator_type: form.value.separatorType,
        residence_time_req: form.value.residenceTimeReq,
      }),
    })
    calcResult.value = await response.json()
  } catch (e) {
    console.error('Separator calc failed:', e)
    alert('计算失败：' + e.message)
  } finally {
    calculating.value = false
  }
}

const confirmAdd = () => {
  emit('add-separator', {
    nodeId: form.value.nodeId,
    nodeParams: nodeParams.value,
    vleResult: vleResult.value,
    designResult: calcResult.value,
    designParams: {
      dropletSize: form.value.dropletSize,
      lengthRatio: form.value.lengthRatio,
      separatorType: form.value.separatorType,
      residenceTimeReq: form.value.residenceTimeReq,
    },
  })
  dialogVisible.value = false
  currentStep.value = 0
  calcResult.value = null
}

// 重置
watch(() => dialogVisible.value, (val) => {
  if (!val) {
    currentStep.value = 0
    calcResult.value = null
    vleResult.value = null
  }
})
</script>

<style scoped>
.step-desc {
  color: #666;
  margin-bottom: 20px;
}
.form-tip {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}
</style>
