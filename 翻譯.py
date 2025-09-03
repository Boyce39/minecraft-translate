import json
import time
from deep_translator import GoogleTranslator

input_file = 'en_us.json'
output_file = 'zh_tw.json'

# 讀取原始 JSON
with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read().strip()
    if text.startswith('{') and text.endswith('}'):
        data = json.loads(text)
    else:
        raise ValueError("格式錯誤")

new_data = {}
total = len(data)
processed = 0

for key, value in data.items():
    processed += 1
    display_value = value if isinstance(value, str) else str(value)
    if len(display_value) > 30:
        display_value = display_value[:27] + "..."

    percent = (processed / total) * 100
    print(f"\r翻譯進度：{processed}/{total}（{percent:.1f}%）｜目前：{key} : {display_value}", end='')

    if not isinstance(value, str) or value.strip() == "" or value.strip() in ["{", "}"]:
        new_data[key] = value
        continue

    # 自動重試翻譯
    for i in range(3):
        try:
            zh = GoogleTranslator(source='auto', target='zh-TW').translate(value)
            new_data[key] = zh
            break
        except Exception as e:
            if i < 2:
                time.sleep(1)  # 等一下再重試
            else:
                print(f"\n翻譯失敗（key: {key}）：{e}")
                new_data[key] = value
    time.sleep(0.05)  # 輕微延遲防止被鎖

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

print("\n翻譯完成")
