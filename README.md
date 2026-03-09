# PDS CALC - 小型过程系统设计计算软件

🍮 用于小型过程系统（涡轮发电 + 换热）的热力计算与设备选型工具。

## 项目状态

✅ **V1.0 功能完整**

- 前端界面（Vue 3 + Element Plus）
- 后端 API（FastAPI）
- 三种计算模式
- 设备选型（电机、管道、阀门）
- **PDF 报告导出**（支持全部 3 种模式）✨
- **Excel 报告导出**（支持全部 3 种模式）✨
- **前端导出集成**（自动识别模式）✨
- **完整测试覆盖** ✅

## 项目结构

```
Small-Process-Calc/
├── frontend/          # Vue 3 前端 (Vite)
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── components/
│   │   │   ├── modes/       # 三种计算模式表单
│   │   │   └── results/     # 结果展示面板
│   │   └── ...
│   └── package.json
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # API 入口
│   │   └── core/
│   │       ├── calculator.py      # 模式 2/3 计算
│   │       ├── thermodynamics.py  # 物性计算
│   │       ├── turbine.py         # 涡轮计算
│   │       ├── heat_exchanger.py  # 换热器计算
│   │       └── selection.py       # 设备选型
│   └── requirements.txt
└── docs/              # 文档（待补充）
```

## 启动方式

### 后端（端口 8000）

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

或直接运行 `run.bat`

API 文档：http://localhost:8000/docs

### 前端（端口 3000）

```bash
cd frontend
npm run dev
```

访问：http://localhost:3000

## 计算模式

### 模式 1：先加热再膨胀 🔥→⚡
1. 冷边介质在换热器中被加热
2. 加热后的介质进入涡轮膨胀做功
3. 输出：换热功率、涡轮功率、设备选型

### 模式 2：先膨胀后回热 ⚡→🔥
1. 介质先经过涡轮膨胀
2. 膨胀后的介质在换热器中回热
3. 输出：涡轮功率、回热功率、设备选型

### 模式 3：直接膨胀 ⚡
1. 介质直接经过涡轮膨胀
2. 无换热过程
3. 输出：涡轮功率、设备选型

## 核心功能

- **物性计算**：支持 N₂、O₂、Air、CO₂、H₂、H₂O 等介质
- **涡轮计算**：绝热膨胀、效率修正、干度判断
- **换热器计算**：热平衡、对数平均温差
- **设备选型**：
  - 电机功率（标准系列）
  - 管道直径（流速约束）
  - 阀门 Kv 值

## 技术栈

- **前端**：Vue 3 + Vite + Element Plus + Pinia + Vue Router
- **后端**：Python 3.12 + FastAPI + Uvicorn
- **计算核心**：自研热力学算法

## 下一步计划 (V2.0)

- [ ] 模式 4：分离器计算
- [ ] 模式 5：一维设计
- [ ] 用户认证与数据持久化
- [ ] 更多介质类型支持
- [ ] 混合介质计算

## 作者

布丁 🍮 - 贺工的专属超级助手
