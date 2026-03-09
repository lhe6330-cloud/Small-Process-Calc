# GitHub Releases 创建说明

由于 gh CLI 未安装，请手动在 GitHub 网页上创建 Releases：

## 步骤

1. 访问 https://github.com/lhe6330-cloud/Small-Process-Calc/releases
2. 点击 **"Draft a new release"**
3. 选择 Tag version: **v1.3.0**
4. Release title: **PDS Calc V1.3.0**
5. 描述内容：

```markdown
## PDS Calc V1.3.0 - 初始发布

### 核心功能
- **模式 1**：先加热再膨胀（涡轮 + 换热器）
- **模式 2**：先膨胀后回热
- **模式 3**：直接膨胀
- **设备选型**：电机/管道/阀门
- **报告导出**：PDF/Excel

### 技术栈
- 后端：FastAPI + CoolProp
- 前端：Vue 3 + Element Plus

### 安装运行
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

cd ../frontend
npm install
npm run dev
```
```

6. 点击 **"Publish release"**
7. 重复上述步骤创建 **v2.0.0** Release

---

## V2.0.0 Release 描述

```markdown
## PDS Calc V2.0.0 - 分离器设计 + 涡轮一维通流设计

### 新功能
- **气液平衡计算 (VLE)** - 含 H₂O 工况 PT 闪蒸计算
- **流程节点分离器设计** - 基于 Stokes 定律的重力沉降式分离器
- **模式 5：涡轮一维通流设计** - 径流式涡轮速度三角形计算（15 项参数）
- **V1.3 → V2.0 数据联动** - 无缝集成
- **PDF/Excel 报告导出** - 模式 4/5 支持

### 测试报告
- ✅ 29/29 测试用例通过 (100%)
- ✅ 所有性能指标满足要求

### 技术栈
- 后端：FastAPI + CoolProp (VLE 闪蒸)
- 前端：Vue 3 + Element Plus

### 安装运行
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

cd ../frontend
npm install
npm run dev
```

### 文档
- PRD: PRD-V2.0.md
- 测试方案：TEST-PLAN-V2.0.md
- 测试报告：TEST-REPORT-V2.0.md
```

---

## 已完成

- ✅ Git Tag v1.3.0 已创建并推送
- ✅ Git Tag v2.0.0 已创建并推送
- ⬜ Releases 需手动创建（上述步骤）

## 查看版本

- Tags: https://github.com/lhe6330-cloud/Small-Process-Calc/tags
- Releases: https://github.com/lhe6330-cloud/Small-Process-Calc/releases
