import os, json, requests
from pathlib import Path

API_KEY = os.environ['API_KEY']
posts_dir = Path('_posts')
summaries = {}

for post in posts_dir.glob('*.md'):
    content = post.read_text(encoding='utf-8')
    # 简单提取前500字符作为输入
    prompt = f"请用一句话概括以下文章：\n{content[:500]}"
    
    response = requests.post(
        'https://api.deepseek.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={
            'model': 'deepseek-chat',
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )
    summary = response.json()['choices'][0]['message']['content']
    summaries[post.stem] = summary

# 保存为 JSON
Path('assets/summaries.json').write_text(json.dumps(summaries, ensure_ascii=False), encoding='utf-8')