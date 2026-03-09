# GitHub 发布操作指南

## 当前状态
✅ 本地 Git 仓库已创建
✅ 代码已提交 (commit)
✅ V1.3 标签已创建

## 待完成步骤

### 1. 在 GitHub 创建仓库

请贺工在浏览器中访问：**https://github.com/new**

**仓库配置：**
- **仓库名：** `Small-Process-Calc` (推荐) 或 `pds-calc`
- **可见性：** Public (公开) 或 Private (私有) - 建议先选 Public
- **初始化选项：** 
  - ❌ 不要勾选 "Add a README file"
  - ❌ 不要勾选 ".gitignore"
  - ❌ 不要选择许可证

### 2. 获取仓库 URL

创建完成后，GitHub 会显示类似：
```
git remote add origin https://github.com/YOUR_USERNAME/Small-Process-Calc.git
```

**复制这个 URL** (例如：`https://github.com/heliang/Small-Process-Calc.git`)

### 3. 推送代码到 GitHub

在项目中打开 PowerShell，运行：

```powershell
cd C:\Users\Administrator\openclaw-workspace\Small-Process-Calc

# 配置远程仓库 (替换为你的实际 URL)
git remote add origin https://github.com/YOUR_USERNAME/Small-Process-Calc.git

# 推送到 GitHub
git push -u origin master --tags
```

### 4. 验证

推送成功后，刷新 GitHub 仓库页面，应该能看到：
- ✅ 所有源代码文件
- ✅ Tags 中有 `v1.3`
- ✅ README.md 文档

---

## 如果遇到问题

### 问题 1：远程仓库已存在
```
fatal: remote origin already exists.
```
**解决：**
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/Small-Process-Calc.git
```

### 问题 2：认证失败
**解决：** 使用 GitHub Personal Access Token 代替密码
1. 访问：https://github.com/settings/tokens
2. 创建新 Token (勾选 repo 权限)
3. 推送时使用 Token 作为密码

### 问题 3：分支名不匹配
```
error: src refspec master does not match any
```
**解决：**
```powershell
git branch -M main
git push -u origin main --tags
```

---

## 完成后的仓库结构

```
Small-Process-Calc/
├── README.md              # 项目说明
├── PRD-产品需求文档.md     # 需求文档
├── TEST-PLAN.md          # 测试方案
├── TEST-REPORT.md        # 测试报告
├── SRK-FIX-REPORT.md     # 修复报告
├── run_tests.py          # 测试脚本
├── .gitignore            # Git 忽略文件
│
├── backend/              # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── core/         # 计算核心 (SRK 模型)
│   │   ├── api/
│   │   ├── models/
│   │   └── reports/
│   └── requirements.txt
│
└── frontend/             # Vue 3 前端
    ├── src/
    │   ├── App.vue
    │   ├── components/
    │   └── main.js
    └── package.json
```

---

**创建时间：** 2026-03-09  
**版本：** V1.3  
**作者：** 贺工 & 布丁 🍮
