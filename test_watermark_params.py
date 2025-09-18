#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试脚本：测试不同水印参数设置（字体大小、颜色、位置）
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import subprocess
import shutil


def create_test_image(output_path, width=600, height=400, background_color='lightgray'):
    """
    创建测试图片
    :param output_path: 输出图片路径
    :param width: 图片宽度
    :param height: 图片高度
    :param background_color: 背景颜色
    """
    # 创建图片
    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)
    
    # 尝试加载系统字体
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 20)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 20)
        except:
            font = ImageFont.load_default()
    
    # 添加测试文本
    draw.text((width//4, height//2 - 20), "水印测试图片", font=font, fill='black')
    
    # 保存图片
    img.save(output_path)
    print(f"已创建测试图片: {output_path}")
    
    # 如果安装了piexif库，添加EXIF日期信息
    try:
        import piexif
        # 创建EXIF字典
        exif_dict = {}
        # 设置拍摄日期为2023-10-15
        date_str = "2023:10:15 14:30:25"
        exif_dict['Exif'] = {}
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str.encode('utf-8')
        # 转换为字节并保存
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, output_path)
        print(f"已添加EXIF日期信息: {date_str}")
    except ImportError:
        print("警告: 未安装piexif库，无法添加EXIF信息")
    except Exception as e:
        print(f"添加EXIF信息时出错: {e}")
    
    return output_path


def run_watermark_with_params(image_path, params, output_dir):
    """
    使用指定参数运行水印工具
    :param image_path: 图片路径
    :param params: 水印参数字典
    :param output_dir: 输出目录
    :return: 处理后的图片路径
    """
    # 构造命令行参数
    cmd = [sys.executable, "photo_watermark.py", "--path", image_path]
    
    # 添加参数
    if 'font_size' in params:
        cmd.extend(["--font-size", str(params['font_size'])])
    if 'color' in params:
        cmd.extend(["--color", params['color']])
    if 'position' in params:
        cmd.extend(["--position", params['position']])
    if 'opacity' in params:
        cmd.extend(["--opacity", str(params['opacity'])])
    
    # 添加输出目录参数（如果支持）
    # 注意：我们的主程序目前没有--output参数，使用默认输出目录
    
    print(f"\n运行水印工具：{cmd}")
    print(f"参数: {params}")
    
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
            # 获取输出文件名
            base_name = os.path.basename(image_path)
            # 主程序会在图片所在目录创建_watermark子目录
            output_path = os.path.join(os.path.dirname(image_path), f"{os.path.basename(os.path.dirname(image_path))}_watermark", base_name)
            return output_path
        else:
            print(f"水印工具运行失败，退出码: {result.returncode}")
            return None
    except Exception as e:
        print(f"执行水印工具时出错: {e}")
        return None


def create_test_combinations():
    """
    创建要测试的参数组合
    :return: 参数组合列表
    """
    # 基本参数组合
    combinations = [
        # 测试不同字体大小
        {"name": "大字体", "font_size": 32, "color": "black", "position": "bottom-right"},
        {"name": "中字体", "font_size": 24, "color": "black", "position": "bottom-right"},
        {"name": "小字体", "font_size": 16, "color": "black", "position": "bottom-right"},
        
        # 测试不同颜色
        {"name": "红色水印", "font_size": 24, "color": "red", "position": "bottom-right"},
        {"name": "蓝色水印", "font_size": 24, "color": "blue", "position": "bottom-right"},
        {"name": "绿色水印", "font_size": 24, "color": "green", "position": "bottom-right"},
        
        # 测试不同位置
        {"name": "左上角", "font_size": 24, "color": "black", "position": "top-left"},
        {"name": "右上角", "font_size": 24, "color": "black", "position": "top-right"},
        {"name": "左下角", "font_size": 24, "color": "black", "position": "bottom-left"},
        {"name": "右下角", "font_size": 24, "color": "black", "position": "bottom-right"},
        {"name": "居中", "font_size": 24, "color": "black", "position": "center"},
        
        # 综合测试
        {"name": "大红色居中", "font_size": 32, "color": "red", "position": "center"},
        {"name": "小蓝色左上角", "font_size": 16, "color": "blue", "position": "top-left"},
    ]
    
    return combinations


def main():
    """
    主函数
    """
    print("===== 水印参数综合测试 =====")
    
    # 测试根目录
    test_root = "watermark_params_test"
    
    # 清空之前的测试结果
    if os.path.exists(test_root):
        shutil.rmtree(test_root)
    os.makedirs(test_root, exist_ok=True)
    
    # 创建要测试的参数组合
    test_combinations = create_test_combinations()
    
    # 为每种组合运行测试
    success_count = 0
    total_count = len(test_combinations)
    
    for i, combo in enumerate(test_combinations):
        print(f"\n=== 测试 {i+1}/{total_count}: {combo['name']} ===")
        
        # 创建测试子目录
        test_dir = os.path.join(test_root, f"test_{i+1}_{combo['name'].replace(' ', '_')}")
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建测试图片
        test_image = os.path.join(test_dir, "test_image.jpg")
        create_test_image(test_image)
        
        # 运行水印工具
        result_image = run_watermark_with_params(test_image, combo, test_dir)
        
        # 检查结果
        if result_image and os.path.exists(result_image):
            print(f"测试成功！结果保存在: {result_image}")
            success_count += 1
        else:
            print(f"测试失败！")
    
    # 输出测试总结
    print(f"\n===== 测试总结 =====")
    print(f"总测试数: {total_count}")
    print(f"成功测试: {success_count}")
    print(f"失败测试: {total_count - success_count}")
    print(f"\n所有测试结果保存在: {test_root}")
    print("请手动检查各个测试目录中的水印效果。")


if __name__ == "__main__":
    main()