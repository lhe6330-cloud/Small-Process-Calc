import os
import glob
import sys

# 设置 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')

base = 'C:/Users/Administrator/openclaw-workspace/Small-Process-Calc'

# 读取 MD 文件并写入到临时文件
print("读取 MD 文档...")
for f in glob.glob(os.path.join(base, '*.md')):
    fname = os.path.basename(f)
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()
            out_file = f'{base}/temp_{fname.replace(".md", "")}.txt'
            with open(out_file, 'w', encoding='utf-8') as out:
                out.write(content)
            print(f"✓ {fname} -> temp_{fname.replace('.md', '')}.txt")
    except Exception as e:
        print(f"✗ {fname}: {e}")

# 读取 Python 文件
print("\n读取 Python 脚本...")
for f in glob.glob(os.path.join(base, '*.py')):
    fname = os.path.basename(f)
    if fname == 'check_progress.py':
        continue
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()
            out_file = f'{base}/temp_{fname.replace(".py", "")}.txt'
            with open(out_file, 'w', encoding='utf-8') as out:
                out.write(content)
            print(f"✓ {fname} -> temp_{fname.replace('.py', '')}.txt")
    except Exception as e:
        print(f"✗ {fname}: {e}")

print("\n完成！请读取 temp_*.txt 文件查看内容")
