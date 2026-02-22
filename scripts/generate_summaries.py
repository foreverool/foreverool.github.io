import os
import json
import requests
import pathlib

# 配置
API_KEY = os.environ.get('BAILIAN_API_KEY')
if not API_KEY:
    raise ValueError("BAILIAN_API_KEY not set")

# 阿里云百炼的API端点（使用兼容OpenAI的接入点，注意地域要选新加坡才能用免费额度）
# 免费额度仅限新加坡地域，所以使用国际站Endpoint [citation:1][citation:3][citation:9]
BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
# 如果你希望使用国内北京地域（无免费额度），可以将BASE_URL替换为：
# BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# 选择模型，这里使用通义千问系列中的性价比款，也可以用你之前习惯的deepseek-v3 [citation:9]
MODEL_NAME = "qwen-plus" # 也可以试试 "qwen-turbo" 或 "deepseek-v3"

POSTS_DIR = pathlib.Path("content/posts")
DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)
SUMMARIES_FILE = DATA_DIR / "summaries.json"

# 加载已有的摘要（可选）
existing = {}
if SUMMARIES_FILE.exists():
    with open(SUMMARIES_FILE, 'r', encoding='utf-8') as f:
        existing = json.load(f)

summaries = {}

# 遍历所有 Markdown 文件
for md_file in POSTS_DIR.glob("**/*.md"):
    rel_path = str(md_file.relative_to(pathlib.Path("content")))
    content = md_file.read_text(encoding='utf-8')

    # 提取文章正文（去掉前置元数据）
    parts = content.split('---', 2)
    if len(parts) >= 3:
        body = parts[2].strip()
    else:
        body = content.strip()

    if len(body) < 50:
        summaries[rel_path] = "文章内容过短，无法生成摘要。"
        continue

    # 构建提示词
    prompt = f"请为以下文章生成一句简洁的摘要（不超过50字）：\n\n{body[:1000]}"

    # 准备请求头和请求体 [citation:3][citation:9]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个帮助生成文章摘要的助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 150
    }

    try:
        # 发送请求
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # 检查HTTP错误

        # 解析响应
        data = response.json()
        summary = data['choices'][0]['message']['content'].strip()
        summaries[rel_path] = summary
        print(f"✅ Generated summary for {rel_path}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network/HTTP error processing {rel_path}: {e}")
        if response.status_code == 402:
            print("  可能原因：免费额度已用完或账户欠费，请检查控制台。")
        summaries[rel_path] = "摘要生成失败（网络或API错误）。"
    except Exception as e:
        print(f"❌ Unexpected error processing {rel_path}: {e}")
        summaries[rel_path] = "摘要生成失败。"

# 保存摘要文件
with open(SUMMARIES_FILE, 'w', encoding='utf-8') as f:
    json.dump(summaries, f, ensure_ascii=False, indent=2)

print(f"✨ Summaries saved to {SUMMARIES_FILE}")