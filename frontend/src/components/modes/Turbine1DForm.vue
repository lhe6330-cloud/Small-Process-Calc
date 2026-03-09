<template>
  <el-dialog v-model="dialogVisible" title="⚙️ 涡轮一维通流设计" width="950px" :close-on-click-modal="false">
    <!-- 数据来源选择 -->
    <el-alert 
      title="数据来源"
      description="从模式 1/2/3 的计算结果自动带入涡轮参数"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    />
    
    <el-form :model="form" label-width="140px">
      <el-divider content-position="left">📥 涡轮参数（从 V1.3 带入，只读）</el-divider>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="流量">
            <el-input :value="turbineData.flow_rate + ' ' + turbineData.flow_unit" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="介质">
            <el-input :value="mediumDisplay" disabled />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="进口压力">
            <el-input :value="turbineData.p_in + ' MPa.G'" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="出口压力">
            <el-input :value="turbineData.p_out + ' MPa.G'" disabled />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="进口温度">
            <el-input :value="turbineData.t_in + ' °C'" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="出口温度">
            <el-input :value="turbineData.t_out + ' °C'" disabled />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="进口密度">
            <el-input :value="turbineData.rho_in + ' kg/m³'" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="出口密度">
            <el-input :value="turbineData.rho_out + ' kg/m³'" disabled />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="轴功率">
            <el-input :value="turbineData.power_shaft + ' kW'" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="电功率">
            <el-input :value="turbineData.power_electric + ' kW'" disabled />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-divider content-position="left">⚙️ 设计参数（可编辑）</el-divider>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="转速 n" required>
            <el-input-number v-model="form.speedRpm" :min="1000" :max="20000" step="500" />
            <span style="margin-left: 10px">rpm</span>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="叶片数 Z" required>
            <el-input-number v-model="form.bladeCount" :min="9" :max="21" step="1" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="速比 u/C₀" required>
            <el-input-number v-model="form.speedRatio" :min="0.6" :max="0.75" step="0.01" :precision="2" />
            <p class="form-tip">推荐范围：0.6-0.75</p>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="反动度 Ω" required>
            <el-input-number v-model="form.reaction" :min="0" :max="100" step="5" />
            <span style="margin-left: 10px">%</span>
            <p class="form-tip">推荐范围：0-100%</p>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    
    <div style="text-align: center; margin: 20px 0">
      <el-button type="primary" size="large" @click="calculate" :loading="calculating">
        🚀 开始计算
      </el-button>
      <el-button @click="reset">重置</el-button>
    </div>
    
    <!-- 计算结果 -->
    <div v-if="calcResult && calcResult.success">
      <el-divider />
      
      <el-alert 
        :title="calcResult.performance.match ? '✅ 功率验证通过' : '⚠️ 功率偏差较大，请检查参数'"
        :type="calcResult.performance.match ? 'success' : 'warning'"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span style="font-weight: 600">📐 基本尺寸</span>
            </template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="叶轮外径 D₁">{{ calcResult.dimensions.D1 }} mm</el-descriptions-item>
              <el-descriptions-item label="叶轮内径 D₂">{{ calcResult.dimensions.D2 }} mm</el-descriptions-item>
              <el-descriptions-item label="进口叶片高度 b₁">{{ calcResult.dimensions.b1 }} mm</el-descriptions-item>
              <el-descriptions-item label="出口叶片高度 b₂">{{ calcResult.dimensions.b2 }} mm</el-descriptions-item>
              <el-descriptions-item label="叶片数 Z">{{ calcResult.dimensions.Z }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <span style="font-weight: 600">🔥 热力参数</span>
            </template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="级效率 η">{{ calcResult.thermo_params.eta }} %</el-descriptions-item>
              <el-descriptions-item label="反动度 Ω">{{ calcResult.thermo_params.omega }} %</el-descriptions-item>
              <el-descriptions-item label="速比 u/C₀">{{ calcResult.thermo_params.speed_ratio }}</el-descriptions-item>
              <el-descriptions-item label="等熵速度 C₀">{{ calcResult.thermo_params.C0 }} m/s</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span style="font-weight: 600">📊 速度三角形 - 进口</span>
            </template>
            <div class="velocity-triangle">
              <div class="vt-row">
                <span class="vt-label">绝对速度 C₁</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_in.C1 }} m/s</span>
              </div>
              <div class="vt-row">
                <span class="vt-label">相对速度 W₁</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_in.W1 }} m/s</span>
              </div>
              <div class="vt-row">
                <span class="vt-label">圆周速度 U₁</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_in.U1 }} m/s</span>
              </div>
              <div class="vt-row">
                <span class="vt-label">绝对气流角 α₁</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_in.alpha1 }} °</span>
              </div>
              <div class="vt-row">
                <span class="vt-label">相对气流角 β₁</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_in.beta1 }} °</span>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <span style="font-weight: 600">📊 速度三角形 - 出口</span>
            </template>
            <div class="velocity-triangle">
              <div class="vt-row">
                <span class="vt-label">绝对速度 C₂</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_out.C2 }} m/s</span>
              </div>
              <div class="vt-row">
                <span class="vt-label">相对速度 W₂</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_out.W2 }} m/s</span>
              </div>
              <div class="vt-row">
                <span class="vt-label">圆周速度 U₂</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_out.U2 }} m/s</span>
              </div>
              <div class="vt-row">
                <span class="vt-label">绝对气流角 α₂</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_out.alpha2 }} °</span>
              </div>
              <div class="vt-row">
                <span class="vt-label">相对气流角 β₂</span>
                <span class="vt-value">{{ calcResult.velocity_triangle_out.beta2 }} °</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card style="margin-top: 20px">
        <template #header>
          <span style="font-weight: 600">✅ 性能验证</span>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="计算功率">{{ calcResult.performance.P_calc }} kW</el-descriptions-item>
          <el-descriptions-item label="输入功率">{{ calcResult.performance.P_input }} kW</el-descriptions-item>
          <el-descriptions-item label="压降">{{ calcResult.performance.delta_p }} MPa</el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <div style="text-align: right; margin-top: 20px">
        <el-button @click="calcResult = null">重新计算</el-button>
        <el-button type="success" @click="exportResult">📄 导出报告</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps(['modelValue', 'turbineData'])
const emit = defineEmits(['update:modelValue', 'calculate'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const calculating = ref(false)
const calcResult = ref(null)

const form = ref({
  speedRpm: 3000,
  bladeCount: 13,
  speedRatio: 0.65,
  reaction: 50,
})

const mediumDisplay = computed(() => {
  const data = props.turbineData || {}
  if (data.composition) {
    const parts = Object.entries(data.composition)
      .filter(([_, v]) => v > 0.01)
      .map(([k, v]) => `${k}(${(v * 100).toFixed(0)}%)`)
    return parts.join(' + ') || data.medium || '-'
  }
  return data.medium || '-'
})

const calculate = async () => {
  calculating.value = true
  try {
    const data = props.turbineData || {}
    const response = await fetch('/api/calculate/mode5', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_mode: 'mode1',
        flow_rate: data.flow_rate || 1000,
        flow_unit: data.flow_unit || 'Nm3/h',
        p_in: data.p_in || 0.5,
        p_out: data.p_out || 0.1,
        t_in: data.t_in || 200,
        t_out: data.t_out || 85,
        rho_in: data.rho_in || 4.5,
        rho_out: data.rho_out || 1.2,
        power_shaft: data.power_shaft || 45.2,
        speed_rpm: form.value.speedRpm,
        blade_count: form.value.bladeCount,
        speed_ratio: form.value.speedRatio,
        reaction: form.value.reaction,
      }),
    })
    calcResult.value = await response.json()
    emit('calculate', calcResult.value)
  } catch (e) {
    console.error('Turbine 1D calc failed:', e)
    alert('计算失败：' + e.message)
  } finally {
    calculating.value = false
  }
}

const reset = () => {
  form.value = {
    speedRpm: 3000,
    bladeCount: 13,
    speedRatio: 0.65,
    reaction: 50,
  }
  calcResult.value = null
}

const exportResult = () => {
  // TODO: 导出 PDF/Excel
  alert('导出功能开发中...')
}

watch(() => dialogVisible.value, (val) => {
  if (!val) {
    calcResult.value = null
  }
})
</script>

<style scoped>
.form-tip {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}
.velocity-triangle {
  padding: 10px 0;
}
.vt-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 15px;
  border-bottom: 1px solid #eee;
}
.vt-row:last-child {
  border-bottom: none;
}
.vt-label {
  color: #666;
}
.vt-value {
  font-weight: 600;
  color: #333;
}
</style>
