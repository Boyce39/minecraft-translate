import re
import time
from deep_translator import GoogleTranslator

input_file = 'en_us.snbt'
output_file = 'zh_tw.snbt'

def smart_translate(text):
    for i in range(3):
        try:
            return GoogleTranslator(source='auto', target='zh-TW').translate(text)
        except Exception as e:
            if i < 2:
                time.sleep(1)
            else:
                print(f"\n翻譯失敗：{text}｜錯誤訊息：{e}")
                return text
    return text

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
total = sum(len(re.findall(r'"([^"]+)"', line)) for line in lines)
count = 0  # <-- 改用 global

def array_trans(m):
    global count
    s = m.group(1)
    if not re.search(r'[A-Za-z]', s):
        return f'"{s}"'
    zh = smart_translate(s)
    count += 1
    percent = (count / total) * 100
    print(f"\r[{count}/{total}][{percent:.1f}%] {zh}{' ' * 20}", end='')
    time.sleep(0.05)
    return f'"{zh}"'

def single_trans(m):
    global count
    s = m.group(1)
    if not re.search(r'[A-Za-z]', s):
        return f'"{s}"'
    zh = smart_translate(s)
    count += 1
    percent = (count / total) * 100
    print(f"\r[{count}/{total}][{percent:.1f}%] {zh}{' ' * 20}", end='')
    time.sleep(0.05)
    return f'"{zh}"'

for line in lines:
    # 陣列內容
    if re.search(r':\s*\[', line):
        line = re.sub(r'"([^"]+)"', array_trans, line)
    # 單一 value
    elif re.search(r':\s*"', line):
        line = re.sub(r':\s*"([^"]+)"', lambda m: ': "' + single_trans(m) + '"', line)
    output_lines.append(line)

with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("\nSNBT/語言包翻譯完成，已產生 zh_tw.snbt。")
