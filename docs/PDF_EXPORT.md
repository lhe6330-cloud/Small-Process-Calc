# PDF 导出功能说明

## 概述

PDS CALC 现已支持 PDF 格式报告导出，使用 `reportlab` 库生成专业的中文 PDF 文档。

## API 接口

```
POST /api/export/pdf/mode1
Content-Type: application/json
```

### 请求参数

与模式 1 计算接口相同：

```json
{
  "cold_side": {
    "medium_type": "single",
    "medium": "N2",
    "flow_rate": 1000,
    "flow_unit": "Nm3/h",
    "p_in": 0.5,
    "p_out": 0.48,
    "t_in": 20,
    "t_out": 200
  },
  "hot_side": {
    "medium_type": "single",
    "medium": "H2O",
    "flow_rate": 0.5,
    "flow_unit": "T/h",
    "p_in": 0.6,
    "p_out": 0.55,
    "t_in": 250
  },
  "turbine": {
    "p_out": 0.1,
    "adiabatic_efficiency": 85
  }
}
```

### 响应

- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename=report_YYYYMMDD_HHMMSS.pdf`
- **Body**: PDF 文件二进制数据

## PDF 报告内容

### 1. 标题区
- PDS CALC 标志
- 报告类型（模式 1: 先加热再膨胀）
- 计算时间

### 2. 输入参数表
| 参数 | 冷边 | 热边 | 涡轮 |
|------|------|------|------|
| 介质 | N₂ | H₂O | - |
| 流量 | 1000 Nm³/h | 0.5 T/h | - |
| 入口压力 | 0.5 MPa.G | 0.6 MPa.G | - |
| 出口压力 | 0.48 MPa.G | 0.55 MPa.G | 0.1 MPa.G |
| 入口温度 | 20°C | 250°C | 200°C |
| 出口温度 | 200°C | - | - |
| 绝热效率 | - | - | 85% |

### 3. 计算结果表
- 换热功率 (kW)
- 热边出口温度 (°C)
- 涡轮轴功率 (kW)
- 发电功率 (kW)
- 涡轮出口温度 (°C)
- 电机选型 (kW)
- 进口管道 (DN)
- 出口管道 (DN)
- 阀门 (DN)

### 4. 设备选型详情
- 电机：功率规格
- 进口管道：DN + 流速
- 出口管道：DN + 流速
- 阀门：DN + Kv 值

## 技术实现

### 依赖库
```bash
pip install reportlab
```

### 字体支持
- 自动检测系统中文字体（微软雅黑/宋体/黑体）
- 如果未找到中文字体，使用默认 Helvetica（可能无法显示中文）

### 文件结构
```
backend/app/reports/
├── pdf_export.py      # PDF 导出核心模块
└── excel_export.py    # Excel 导出模块
```

## 使用示例

### PowerShell
```powershell
$body = @{
    cold_side = @{
        medium_type = 'single'
        medium = 'N2'
        flow_rate = 1000
        flow_unit = 'Nm3/h'
        p_in = 0.5
        p_out = 0.48
        t_in = 20
        t_out = 200
    }
    hot_side = @{
        medium_type = 'single'
        medium = 'H2O'
        flow_rate = 0.5
        flow_unit = 'T/h'
        p_in = 0.6
        p_out = 0.55
        t_in = 250
    }
    turbine = @{
        p_out = 0.1
        adiabatic_efficiency = 85
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri http://localhost:8000/api/export/pdf/mode1 `
    -Method Post `
    -Body $body `
    -ContentType 'application/json' `
    -OutFile "report.pdf"
```

### Python
```python
import requests

data = {
    "cold_side": {
        "medium_type": "single",
        "medium": "N2",
        "flow_rate": 1000,
        "flow_unit": "Nm3/h",
        "p_in": 0.5,
        "p_out": 0.48,
        "t_in": 20,
        "t_out": 200
    },
    "hot_side": {
        "medium_type": "single",
        "medium": "H2O",
        "flow_rate": 0.5,
        "flow_unit": "T/h",
        "p_in": 0.6,
        "p_out": 0.55,
        "t_in": 250
    },
    "turbine": {
        "p_out": 0.1,
        "adiabatic_efficiency": 85
    }
}

response = requests.post('http://localhost:8000/api/export/pdf/mode1', json=data)
with open('report.pdf', 'wb') as f:
    f.write(response.content)
```

## 前端集成建议

在结果面板添加导出按钮：

```vue
<el-button type="success" @click="exportPDF">
  📄 导出 PDF
</el-button>

<script setup>
const exportPDF = async () => {
  try {
    const response = await fetch('/api/export/pdf/mode1', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputData)
    })
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${new Date().getTime()}.pdf`
    a.click()
  } catch (e) {
    alert('导出失败：' + e.message)
  }
}
</script>
```

## 测试状态

✅ 2026-03-09 - PDF 导出功能测试通过
- 文件大小：~52 KB
- 中文字体：正常显示
- 表格样式：正确渲染
- 数据精度：保留 2 位小数

---

_创建时间：2026-03-09_
