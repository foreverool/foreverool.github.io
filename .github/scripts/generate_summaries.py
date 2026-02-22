import os
import yaml
import json
import requests
from pathlib import Path

API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY not set")

POSTS_DIR = Path("content/posts")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SUMMARIES_FILE = DATA_DIR / "summaries.json"

# 加载已有的摘要（可选，用于增量更新）
existing = {}
if SUMMARIES_FILE.exists():
    with open(SUMMARIES_FILE, 'r', encoding='utf-8') as f:
        existing = json.load(f)

summaries = {}

# 遍历所有 Markdown 文件
for md_file in POSTS_DIR.glob("**/*.md"):
    # 使用相对路径作为文章标识，例如 "posts/my-article.md"
    rel_path = str(md_file.relative_to(Path("content")))
    
    # 如果已有摘要且文件未修改，可以跳过（可选）
    # 这里简单起见每次都重新生成
    content = md_file.read_text(encoding='utf-8')
    
    # 提取文章正文（去掉前置元数据）
    # 前置元数据通常由 --- 包裹
    parts = content.split('---', 2)
    if len(parts) >= 3:
        body = parts[2].strip()
    else:
        body = content.strip()
    
    # 如果文章太短，跳过或使用简单提示
    if len(body) < 50:
        summaries[rel_path] = "文章内容过短，无法生成摘要。"
        continue
    
    # 调用 DeepSeek API 生成摘要
    prompt = f"请为以下文章生成一句简洁的摘要（不超过50字）：\n\n{body[:800]}"  # 限制输入长度
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个帮助生成文章摘要的助手。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 100
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        summary = data['choices'][0]['message']['content'].strip()
        summaries[rel_path] = summary
        print(f"Generated summary for {rel_path}")
    except Exception as e:
        print(f"Error processing {rel_path}: {e}")
        summaries[rel_path] = "摘要生成失败。"

# 保存摘要文件
with open(SUMMARIES_FILE, 'w', encoding='utf-8') as f:
    json.dump(summaries, f, ensure_ascii=False, indent=2)

print("Summaries saved to", SUMMARIES_FILE)