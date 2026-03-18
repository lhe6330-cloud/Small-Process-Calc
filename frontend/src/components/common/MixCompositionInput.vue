<template>
  <div class="mix-composition-input">
    <div class="composition-type">
      <span class="label">百分比类型：</span>
      <label class="radio-label">
        <input 
          type="radio" 
          :checked="localCompositionType === 'mole'" 
          @change="localCompositionType = 'mole'"
          name="compositionType"
        />
        <span>摩尔百分比</span>
      </label>
      <label class="radio-label">
        <input 
          type="radio" 
          :checked="localCompositionType === 'mass'" 
          @change="localCompositionType = 'mass'"
          name="compositionType"
        />
        <span>质量百分比</span>
      </label>
    </div>
    
    <div class="composition-grid">
      <div v-for="(value, key) in localComposition" :key="key" class="composition-item">
        <el-input-number 
          v-model="localComposition[key]" 
          :min="0" 
          :max="100" 
          :precision="2"
          :step="1"
          controls-position="right"
          size="small"
        />
        <span class="medium-label">{{ getMediumLabel(key) }}</span>
        <span class="percent-sign">%</span>
      </div>
    </div>
    
    <div class="composition-footer">
      <div class="total-display" :class="totalClass">
        <span>当前合计：</span>
        <span class="total-value">{{ total.toFixed(2) }}%</span>
      </div>
      <el-button 
        size="small" 
        @click="normalize" 
        :disabled="total === 0 || total === 100"
        type="primary"
        plain
      >
        🔄 归一化
      </el-button>
    </div>
    
    <el-alert 
      v-if="showWarning" 
      type="warning" 
      :closable="false" 
      show-icon
      class="composition-warning"
    >
      组分合计不为 100%，请点击归一化按钮
    </el-alert>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      composition: { N2: 0, O2: 0, H2: 0, CO2: 0, H2O: 0 },
      composition_type: 'mole'
    })
  }
})

const emit = defineEmits(['update:modelValue'])

const mediumLabels = {
  N2: 'N₂',
  O2: 'O₂',
  H2: 'H₂',
  CO2: 'CO₂',
  H2O: 'H₂O'
}

const localComposition = ref({ ...props.modelValue.composition })
const localCompositionType = ref(props.modelValue.composition_type || 'mole')

const total = computed(() => {
  return Object.values(localComposition.value).reduce((sum, val) => sum + Number(val), 0)
})

const totalClass = computed(() => {
  if (Math.abs(total.value - 100) < 0.01) return 'total-ok'
  return 'total-warning'
})

const showWarning = computed(() => {
  const hasInput = Object.values(localComposition.value).some(v => v > 0)
  return hasInput && Math.abs(total.value - 100) > 0.01
})

function getMediumLabel(key) {
  return mediumLabels[key] || key
}

function normalize() {
  if (total.value === 0 || Math.abs(total.value - 100) < 0.01) return
  
  const factor = 100 / total.value
  for (const key in localComposition.value) {
    localComposition.value[key] = Math.round(localComposition.value[key] * factor * 100) / 100
  }
}

watch(() => localComposition.value, (newVal) => {
  emit('update:modelValue', {
    composition: { ...newVal },
    composition_type: localCompositionType.value
  })
}, { deep: true })

watch(() => localCompositionType.value, (newVal) => {
  emit('update:modelValue', {
    composition: { ...localComposition.value },
    composition_type: newVal
  })
})

watch(() => props.modelValue, (newVal) => {
  if (newVal && newVal.composition) {
    localComposition.value = { ...newVal.composition }
  }
  if (newVal && newVal.composition_type) {
    localCompositionType.value = newVal.composition_type
  }
}, { deep: true })
</script>

<style scoped>
.mix-composition-input {
  background: #0F172A;
  border: 1px solid #334155;
  border-radius: 4px;
  padding: 16px;
  margin-top: 12px;
}

.composition-type {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.composition-type .label {
  color: #94A3B8;
  font-size: 13px;
}

.radio-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #F1F5F9;
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.radio-label:hover {
  background-color: rgba(51, 65, 85, 0.5);
}

.radio-label input[type="radio"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
  accent-color: #00D4FF;
}

.radio-label input[type="radio"]:checked {
  accent-color: #00D4FF;
}

.composition-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.composition-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.composition-item :deep(.el-input-number) {
  width: 100px;
}

.medium-label {
  color: #F1F5F9;
  font-size: 13px;
  min-width: 40px;
}

.percent-sign {
  color: #94A3B8;
  font-size: 13px;
}

.composition-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #334155;
}

.total-display {
  font-size: 14px;
}

.total-display .total-value {
  font-weight: bold;
  font-size: 16px;
}

.total-ok .total-value {
  color: #22C55E;
}

.total-warning .total-value {
  color: #F59E0B;
}

.composition-warning {
  margin-top: 12px;
  background: #FEF3C7;
  border-color: #F59E0B;
}

.composition-warning :deep(.el-alert__content) {
  color: #92400E;
}
</style>
