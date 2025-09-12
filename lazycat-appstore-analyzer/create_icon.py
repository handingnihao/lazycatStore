#!/usr/bin/env python3
"""
生成应用图标
使用PIL创建一个简单的PNG图标
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建512x512的图像
    size = (512, 512)
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变背景
    for i in range(512):
        color_r = int(74 + (126 - 74) * (i / 512))  # 从蓝到绿
        color_g = int(144 + (211 - 144) * (i / 512))
        color_b = int(226 + (33 - 226) * (i / 512))
        draw.rectangle([0, i, 512, i+1], fill=(color_r, color_g, color_b))
    
    # 绘制柱状图
    bar_width = 60
    bar_heights = [150, 200, 180, 240, 280]
    bar_x_positions = [80, 160, 240, 320, 400]
    
    for i, (x, h) in enumerate(zip(bar_x_positions, bar_heights)):
        y = 350 - h
        draw.rectangle([x - bar_width//2, y, x + bar_width//2, 350], 
                      fill='white', outline='white', width=2)
    
    # 绘制折线图点
    points = [(80, 350 - 150 - 20), (160, 350 - 200 - 20), 
              (240, 350 - 180 - 20), (320, 350 - 240 - 20), 
              (400, 350 - 280 - 20)]
    
    # 连接线
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill='white', width=3)
    
    # 绘制数据点
    for x, y in points:
        draw.ellipse([x-8, y-8, x+8, y+8], fill='white', outline='white')
    
    # 添加文字
    try:
        # 尝试使用系统字体
        from PIL import ImageFont
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        # 使用默认字体
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 绘制文字
    text1 = "AppStore"
    text2 = "Analyzer"
    
    # 获取文字边界框以居中
    bbox1 = draw.textbbox((0, 0), text1, font=font_large)
    bbox2 = draw.textbbox((0, 0), text2, font=font_small)
    
    text1_width = bbox1[2] - bbox1[0]
    text2_width = bbox2[2] - bbox2[0]
    
    draw.text(((512 - text1_width) // 2, 380), text1, fill='white', font=font_large)
    draw.text(((512 - text2_width) // 2, 430), text2, fill='white', font=font_small)
    
    # 保存图标
    img.save('lzc-icon.png', 'PNG')
    print("✅ 图标已生成: lzc-icon.png")
    
except ImportError:
    print("⚠️ 需要安装Pillow库来生成图标")
    print("请运行: pip install Pillow")
    
    # 创建一个简单的占位图标
    import base64
    
    # 1x1像素的蓝色PNG图片（base64编码）
    placeholder_png = base64.b64decode(
        b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    )
    
    with open('lzc-icon.png', 'wb') as f:
        f.write(placeholder_png)
    print("⚠️ 已创建占位图标: lzc-icon.png")