#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

# 创建图标
def create_icon(size):
    # 创建一个带透明背景的新图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变背景（简化版）
    for i in range(size):
        alpha = int(255 * (1 - i / size * 0.3))
        color = (102, 126, 234, alpha)  # 紫色渐变
        draw.rectangle([0, i, size, i+1], fill=color)
    
    # 绘制一个星星符号
    center_x = size // 2
    center_y = size // 2
    star_size = size // 3
    
    # 星星的五个点
    points = []
    for i in range(5):
        angle = -90 + i * 144  # 五角星的角度
        x = center_x + star_size * 0.9 * (1 if i % 2 == 0 else 0.4) * \
            (1 if angle % 360 < 180 else -1) * abs(angle % 180 - 90) / 90
        y = center_y + star_size * 0.9 * (1 if i % 2 == 0 else 0.4) * \
            (-1 if angle % 360 < 90 or angle % 360 > 270 else 1) * abs((angle + 90) % 180 - 90) / 90
        points.append((int(x), int(y)))
    
    # 简单的星形
    draw.polygon([
        (center_x, center_y - star_size),  # 顶部
        (center_x + star_size * 0.3, center_y - star_size * 0.3),
        (center_x + star_size, center_y),  # 右侧
        (center_x + star_size * 0.3, center_y + star_size * 0.3),
        (center_x, center_y + star_size),  # 底部
        (center_x - star_size * 0.3, center_y + star_size * 0.3),
        (center_x - star_size, center_y),  # 左侧
        (center_x - star_size * 0.3, center_y - star_size * 0.3),
    ], fill=(255, 255, 255, 255))
    
    return img

# 生成不同尺寸的图标
sizes = {
    'icon16.png': 16,
    'icon48.png': 48,
    'icon128.png': 128
}

icons_dir = 'icons'
if not os.path.exists(icons_dir):
    os.makedirs(icons_dir)

for filename, size in sizes.items():
    icon = create_icon(size)
    icon.save(os.path.join(icons_dir, filename))
    print(f'Generated {filename}')

print('Icons generated successfully!')