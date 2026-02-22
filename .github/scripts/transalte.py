import os
import glob
from openai import OpenAI

# 初始化客户端
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 查找所有以 .zh.md 结尾的文件
files = glob.glob("content/**/*.zh.md", recursive=True)

for file_path in files:
    en_file_path = file_path.replace(".zh.md", ".en.md")
    
    # 如果英文版已经存在，跳过（除非你想每次都重翻）
    if os.path.exists(en_file_path):
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"正在翻译: {file_path}")
    
    # 调用 GPT 翻译
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a professional technical translator. Translate the following Markdown content to English. Keep Front Matter keys unchanged. Retain code blocks."},
            {"role": "user", "content": content}
        ]
    )

    translated_text = response.choices[0].message.content

    # 写入新的 .en.md 文件
    with open(en_file_path, "w", encoding="utf-8") as f:
        f.write(translated_text)