#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：生成包含EXIF拍摄日期信息的图片并添加水印
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import subprocess


def create_image_with_exif(output_path, width=800, height=600, date_str=None):
    """
    创建一个带有EXIF拍摄日期信息的测试图片
    :param output_path: 输出图片路径
    :param width: 图片宽度
    :param height: 图片高度
    :param date_str: 自定义拍摄日期字符串，格式为"YYYY:MM:DD HH:MM:SS"
    """
    # 创建一个非白色背景的图片
    img = Image.new('RGB', (width, height), color='lightgray')
    draw = ImageDraw.Draw(img)
    
    # 在图片上添加一些内容
    try:
        # 尝试加载系统字体
        font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 24)
        except:
            font = ImageFont.load_default()
    
    # 添加一些测试文本
    draw.text((width//4, height//2), "测试图片", font=font, fill='black')
    
    # 准备EXIF数据
    exif_data = {}
    # EXIF拍摄日期标签ID
    date_tag = 36867  # DateTimeOriginal
    
    if date_str:
        exif_date = date_str
    else:
        # 使用当前日期
        exif_date = datetime.now().strftime('%Y:%m:%d %H:%M:%S')
    
    exif_data[date_tag] = exif_date
    
    # 保存图片并写入EXIF数据
    # 注意：PIL的save方法需要特定格式的EXIF字典
    # 这里我们使用更简单的方式，先保存图片，然后用piexif库添加EXIF信息
    img.save(output_path)
    
    # 尝试使用piexif库添加EXIF信息
    try:
        import piexif
        # 加载现有EXIF数据
        exif_dict = piexif.load(output_path)
        # 设置拍摄日期
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_date.encode('utf-8')
        # 转换为字节并保存
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, output_path)
        print(f"已成功创建包含EXIF信息的图片: {output_path}")
        print(f"EXIF拍摄日期: {exif_date}")
        return True
    except ImportError:
        print("警告: 未安装piexif库，无法添加EXIF信息")
        print("请运行: pip install piexif")
        return False
    except Exception as e:
        print(f"添加EXIF信息时出错: {e}")
        return False


def run_watermark_tool(image_path):
    """
    运行水印工具处理图片
    :param image_path: 图片路径
    """
    print(f"\n运行水印工具处理图片: {image_path}")
    
    # 构造命令行参数，使用黑色水印以便在灰色背景上更清晰可见
    cmd = [sys.executable, "photo_watermark.py", "--path", image_path, "--color", "black"]
    
    try:
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 打印输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"错误输出: {result.stderr}")
        
        # 检查执行状态
        if result.returncode == 0:
            print("水印工具运行成功！")
            return True
        else:
            print(f"水印工具运行失败，退出码: {result.returncode}")
            return False
    except Exception as e:
        print(f"执行水印工具时出错: {e}")
        return False


def verify_watermark(output_dir, original_date):
    """
    验证水印是否正确添加
    :param output_dir: 输出目录
    :param original_date: 原始EXIF日期
    """
    print(f"\n验证水印结果...")
    
    # 检查输出目录是否存在
    if not os.path.exists(output_dir):
        print(f"错误: 输出目录 {output_dir} 不存在")
        return False
    
    # 获取输出目录中的文件
    files = os.listdir(output_dir)
    if not files:
        print("错误: 输出目录中没有找到文件")
        return False
    
    print(f"在 {output_dir} 中找到 {len(files)} 个文件")
    print("建议手动检查这些文件中的水印是否包含正确的日期信息")
    
    # 提取日期部分（假设日期格式为 YYYY:MM:DD 或 YYYY-MM-DD）
    date_part = original_date.split(' ')[0].replace(':', '-')
    print(f"预期水印中应包含日期: {date_part}")
    
    return True


def main():
    """
    主函数
    """
    print("===== 测试：生成带EXIF信息的图片并添加水印 =====")
    
    # 创建测试图片目录
    test_dir = "test_with_exif"
    os.makedirs(test_dir, exist_ok=True)
    
    # 定义测试图片路径
    test_image_path = os.path.join(test_dir, "test_exif.jpg")
    
    # 定义自定义拍摄日期（可选）
    # 可以修改这里使用不同的日期进行测试
    custom_date = "2023:10:15 14:30:25"
    
    # 创建带EXIF信息的图片
    if not create_image_with_exif(test_image_path, date_str=custom_date):
        print("创建图片失败，测试无法继续")
        return
    
    # 运行水印工具
    if not run_watermark_tool(test_image_path):
        print("水印工具运行失败")
        return
    
    # 验证结果
    # 输出目录在test_with_exif目录下
    output_dir = os.path.join(test_dir, f"{test_dir}_watermark")
    verify_watermark(output_dir, custom_date)
    
    print("\n===== 测试完成 =====")


if __name__ == "__main__":
    main()