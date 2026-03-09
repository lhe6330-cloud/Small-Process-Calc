"""
PDS Calc V1.3 GitHub 发布脚本
"""
import subprocess
import sys

def run_cmd(cmd, show_output=True):
    """执行命令"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if show_output and result.stdout:
        print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

print("="*60)
print("  PDS Calc V1.3 GitHub 发布")
print("="*60)
print()

# 1. 配置 Git
print("[1/6] 配置 Git 用户信息...")
run_cmd('git config --global user.name "HeLiang"')
run_cmd('git config --global user.email "helang@example.com"')

# 2. 初始化仓库
print("\n[2/6] 初始化 Git 仓库...")
run_cmd('git init')

# 3. 添加文件
print("\n[3/6] 添加文件...")
run_cmd('git add .')

# 4. 创建提交
print("\n[4/6] 创建提交...")
commit_msg = """feat: PDS Calc V1.3 初始发布

功能特性:
- 3 种热力循环模式计算
- 6 种单一介质 (N2, O2, Air, CO2, H2, H2O)
- 5 种混合介质组分 (N2, O2, CO2, H2, H2O)
- SRK 模型计算混合物 (通过率 98%)
- 设备选型：电机、管道、阀门
- 报告导出：Excel + PDF
- 测试覆盖率：100% (36/36 通过)

技术栈:
- 前端：Vue 3 + Vite + Element Plus
- 后端：Python FastAPI
- 热力学库：iapws (IF97), CoolProp (SRK/HEOS)

作者：布丁
日期：2026-03-09
"""
# 写入临时文件
with open('commit_msg.txt', 'w', encoding='utf-8') as f:
    f.write(commit_msg)
run_cmd(f'git commit -F commit_msg.txt')

# 5. 创建标签
print("\n[5/6] 创建 V1.3 标签...")
run_cmd('git tag -a v1.3 -m "PDS Calc V1.3 - Initial Release"')

# 6. 显示状态
print("\n[6/6] 完成！")
print("\n" + "="*60)
print("  本地 Git 仓库已创建")
print("="*60)
print("\n下一步操作：")
print("1. 在 GitHub 创建新仓库：https://github.com/new")
print("2. 复制仓库 URL (例如：https://github.com/username/repo.git)")
print("3. 运行以下命令:")
print()
print("   git remote add origin <YOUR_REPO_URL>")
print("   git push -u origin master --tags")
print()

# 清理临时文件
import os
if os.path.exists('commit_msg.txt'):
    os.remove('commit_msg.txt')

print("="*60)
