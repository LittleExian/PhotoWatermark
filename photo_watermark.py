#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片水印命令行工具
根据PRD文档实现的图片水印程序，支持读取EXIF信息并添加自定义水印
"""

import os
import argparse
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import sys
from pathlib import Path


def get_exif_date(image_path):
    """
    从图片中提取EXIF信息中的拍摄日期
    :param image_path: 图片文件路径
    :return: 格式化的日期字符串(YYYY-MM-DD)或None
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                # EXIF拍摄日期标签ID
                date_tag = 36867  # DateTimeOriginal
                if date_tag in exif_data:
                    date_str = exif_data[date_tag]
                    # 解析日期字符串，格式通常为："YYYY:MM:DD HH:MM:SS"
                    try:
                        date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                        return date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        # 尝试其他可能的日期格式
                        try:
                            date_obj = datetime.strptime(date_str.split(' ')[0], '%Y:%m:%d')
                            return date_obj.strftime('%Y-%m-%d')
                        except:
                            pass
    except Exception as e:
        print(f"读取{image_path}的EXIF信息时出错: {e}")
    return None


def add_watermark_to_image(image_path, output_dir, font_size=16, color='white', position='bottom-right', opacity=80, default_text=None):
    """
    向图片添加水印并保存
    :param image_path: 图片文件路径
    :param output_dir: 输出目录
    :param font_size: 字体大小
    :param color: 字体颜色
    :param position: 水印位置
    :param opacity: 透明度(0-100)
    :param default_text: 无EXIF信息时的默认文本
    :return: 是否成功
    """
    try:
        # 打开图片
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img, 'RGBA')
        width, height = img.size

        # 获取水印文本
        watermark_text = get_exif_date(image_path)
        if not watermark_text:
            if default_text:
                watermark_text = default_text
            else:
                # 如果没有默认文本且没有EXIF日期，则使用当前日期
                watermark_text = datetime.now().strftime('%Y-%m-%d')
                print(f"警告: {image_path} 没有EXIF拍摄日期，使用当前日期作为水印")

        # 加载字体，尝试使用系统字体
        try:
            # 尝试加载Windows系统字体
            font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", font_size)
        except:
            try:
                # 尝试加载Linux系统字体
                font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", font_size)
            except:
                # 如果都失败，使用默认字体
                font = ImageFont.load_default()
                print("警告: 无法加载中文字体，可能导致水印显示不正确")

        # 获取文本尺寸
        text_width, text_height = draw.textsize(watermark_text, font=font)

        # 计算文本位置
        margin = 10  # 边距
        if position == 'top-left':
            text_x, text_y = margin, margin
        elif position == 'top-right':
            text_x, text_y = width - text_width - margin, margin
        elif position == 'bottom-left':
            text_x, text_y = margin, height - text_height - margin
        elif position == 'bottom-right':
            text_x, text_y = width - text_width - margin, height - text_height - margin
        elif position == 'center':
            text_x, text_y = (width - text_width) // 2, (height - text_height) // 2
        else:
            # 默认右下角
            text_x, text_y = width - text_width - margin, height - text_height - margin

        # 创建半透明文字
        # 转换颜色为RGBA
        if isinstance(color, str):
            # 如果是颜色名称，转换为RGBA
            from PIL import ImageColor
            rgb_color = ImageColor.getrgb(color)
            # 添加透明度
            rgba_color = rgb_color + (int(255 * opacity / 100),)
        else:
            rgba_color = color

        # 绘制水印
        draw.text((text_x, text_y), watermark_text, font=font, fill=rgba_color)

        # 创建输出目录（如果不存在）
        os.makedirs(output_dir, exist_ok=True)

        # 保存处理后的图片
        output_path = os.path.join(output_dir, os.path.basename(image_path))
        img.save(output_path)
        print(f"已保存带水印的图片到: {output_path}")
        return True
    except Exception as e:
        print(f"处理{image_path}时出错: {e}")
        return False


def process_path(input_path, font_size=16, color='white', position='bottom-right', opacity=80, default_text=None):
    """
    处理输入路径（单个文件或目录）
    :param input_path: 输入文件或目录路径
    :param font_size: 字体大小
    :param color: 字体颜色
    :param position: 水印位置
    :param opacity: 透明度
    :param default_text: 无EXIF信息时的默认文本
    """
    # 检查输入路径是否存在
    if not os.path.exists(input_path):
        print(f"错误: 路径 '{input_path}' 不存在")
        return

    # 定义支持的图片格式
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']

    # 创建输出目录
    if os.path.isdir(input_path):
        parent_dir = os.path.dirname(input_path) if os.path.dirname(input_path) else '.'
        dir_name = os.path.basename(input_path)
        output_dir = os.path.join(parent_dir, f"{dir_name}_watermark")
    else:
        parent_dir = os.path.dirname(input_path)
        dir_name = os.path.basename(parent_dir)
        output_dir = os.path.join(parent_dir, f"{dir_name}_watermark")

    # 处理文件或目录
    success_count = 0
    total_count = 0

    if os.path.isfile(input_path):
        # 处理单个文件
        file_ext = os.path.splitext(input_path)[1].lower()
        if file_ext in supported_formats:
            total_count = 1
            if add_watermark_to_image(input_path, output_dir, font_size, color, position, opacity, default_text):
                success_count = 1
        else:
            print(f"警告: 文件 '{input_path}' 不是支持的图片格式")
    else:
        # 处理目录中的所有图片
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in supported_formats:
                    total_count += 1
                    file_path = os.path.join(root, file)
                    # 保持相对目录结构
                    rel_path = os.path.relpath(root, input_path)
                    if rel_path == '.':
                        target_output_dir = output_dir
                    else:
                        target_output_dir = os.path.join(output_dir, rel_path)
                    
                    if add_watermark_to_image(file_path, target_output_dir, font_size, color, position, opacity, default_text):
                        success_count += 1

    # 输出处理结果统计
    print(f"\n处理完成！")
    print(f"总文件数: {total_count}")
    print(f"成功处理: {success_count}")
    print(f"失败处理: {total_count - success_count}")


def main():
    """
    主函数，解析命令行参数并执行相应操作
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='图片水印命令行工具')
    parser.add_argument('--path', '-p', required=True, help='图片文件或目录的路径')
    parser.add_argument('--font-size', '-s', type=int, default=16, help='水印字体大小（默认：16）')
    parser.add_argument('--color', '-c', default='white', help='水印字体颜色（默认：白色）')
    parser.add_argument('--position', '-pos', choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'], 
                        default='bottom-right', help='水印位置（默认：右下角）')
    parser.add_argument('--opacity', '-o', type=int, default=80, choices=range(0, 101), 
                        help='水印透明度（0-100，默认：80）')
    parser.add_argument('--default-text', '-d', help='无EXIF信息时的默认水印文本')
    parser.add_argument('--version', '-v', action='store_true', help='显示版本信息')

    # 解析命令行参数
    args = parser.parse_args()

    # 显示版本信息
    if args.version:
        print("图片水印命令行工具 v1.0.0")
        print("根据PRD文档实现，支持读取EXIF信息并添加自定义水印")
        return

    # 执行水印处理
    process_path(args.path, args.font_size, args.color, args.position, args.opacity, args.default_text)


if __name__ == '__main__':
    main()