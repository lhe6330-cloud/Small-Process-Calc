@echo off
chcp 65001 >nul
echo ========================================
echo  PDS Calc V1.3 GitHub 发布脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] 配置 Git 用户信息...
git config --global user.name "HeLiang"
git config --global user.email "helang@example.com"

echo.
echo [2/6] 初始化 Git 仓库...
git init

echo.
echo [3/6] 添加文件...
git add .

echo.
echo [4/6] 创建提交...
git commit -m "feat: PDS Calc V1.3 初始发布

- 实现 3 种热力循环模式计算
- 支持 6 种单一介质 (N2, O2, Air, CO2, H2, H2O)
- 支持 5 种混合介质组分 (N2, O2, CO2, H2, H2O)
- 采用 SRK 模型计算混合物 (通过率 98%)
- 设备选型：电机、管道、阀门
- 报告导出：Excel + PDF
- 测试覆盖率：100% (36/36 通过)

技术栈:
- 前端：Vue 3 + Vite + Element Plus
- 后端：Python FastAPI
- 热力学库：iapws (IF97), CoolProp (SRK/HEOS)

作者：布丁 🍮
日期：2026-03-09"

echo.
echo [5/6] 创建 V1.3 标签...
git tag -a "v1.3" -m "PDS Calc V1.3 - 初始发布"

echo.
echo [6/6] 完成！
echo.
echo ========================================
echo  本地 Git 仓库已创建
echo  请手动配置远程仓库并推送:
echo.
echo  git remote add origin ^<YOUR_GITHUB_REPO_URL^>
echo  git push -u origin master --tags
echo ========================================
echo.

pause
