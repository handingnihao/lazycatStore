#!/usr/bin/env python3
import base64
import os

# 简单的1x1像素PNG图标的base64数据（紫色）
# 这是一个最小的有效PNG文件
png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

# 解码base64数据
png_data = base64.b64decode(png_base64)

# 创建图标目录
icons_dir = 'icons'
if not os.path.exists(icons_dir):
    os.makedirs(icons_dir)

# 为每个尺寸创建相同的占位图标
sizes = ['icon16.png', 'icon48.png', 'icon128.png']

for filename in sizes:
    filepath = os.path.join(icons_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(png_data)
    print(f'Created {filename}')

print('Simple placeholder icons created successfully!')
print('Note: These are placeholder icons. You may want to replace them with proper icons later.')