# PhotoWatermark

图片水印命令行工具，用于批量为图片添加基于拍摄日期的水印，并支持自定义水印样式和位置。

## 功能特性

- 📷 **读取EXIF信息**：自动提取图片的拍摄日期
- 🎨 **自定义水印**：支持设置字体大小、颜色、位置和透明度
- 📁 **批量处理**：支持处理单个文件或整个目录
- 💾 **自动保存**：保存到原目录名_watermark的子目录
- 🔧 **灵活配置**：丰富的命令行参数，满足不同需求

## 安装指南

### 前提条件
- Python 3.6或更高版本
- pip包管理器

### 安装步骤

1. 克隆或下载本仓库

2. 安装依赖包
   
   ```bash
   pip install -r requirements.txt
   ```

## 使用说明

### 基本用法

```bash
# 处理单个图片文件
python photo_watermark.py --path "C:\Users\User\Photos\example.jpg"

# 处理整个目录
python photo_watermark.py --path "C:\Users\User\Photos\Vacation"
```

### 高级用法

```bash
# 自定义水印样式（字体大小、颜色、位置、透明度）
python photo_watermark.py --path "C:\Users\User\Photos" --font-size 24 --color "red" --position "center" --opacity 50

# 使用默认文本（当图片无EXIF信息时）
python photo_watermark.py --path "C:\Users\User\Photos" --default-text "My Photo"

# 查看版本信息
python photo_watermark.py --version

# 查看帮助信息
python photo_watermark.py --help
```

### 命令行参数详解

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--path` | `-p` | 图片文件或目录的路径 | **必填** |
| `--font-size` | `-s` | 水印字体大小 | 16 |
| `--color` | `-c` | 水印字体颜色（支持标准颜色名称或HEX值） | white |
| `--position` | `-pos` | 水印位置（top-left, top-right, bottom-left, bottom-right, center） | bottom-right |
| `--opacity` | `-o` | 水印透明度（0-100） | 80 |
| `--default-text` | `-d` | 无EXIF信息时的默认水印文本 | 当前日期 |
| `--version` | `-v` | 显示版本信息 | - |
| `--help` | `-h` | 显示帮助信息 | - |

## 示例

### 示例1：基本水印
为单个图片添加默认水印（右下角，白色，16号字体，80%透明度）

```bash
python photo_watermark.py -p "example.jpg"
```

### 示例2：自定义水印
为整个目录的图片添加红色、居中、大号字体的水印

```bash
python photo_watermark.py -p "photos_folder" -s 36 -c "red" -pos "center" -o 60
```

## 注意事项

1. 程序会尝试加载系统中的中文字体（SimHei或WenQuanYi Micro Hei），如果无法加载，可能会导致中文显示异常
2. 支持的图片格式：JPEG、PNG、BMP、TIFF、GIF等
3. 对于没有EXIF拍摄日期信息的图片，默认使用当前日期作为水印
4. 输出文件会保存在原目录同级的`原目录名_watermark`子目录中
5. 处理大量图片时可能需要较长时间，请耐心等待

## 开发说明

### 项目结构

- `photo_watermark.py`：主程序文件，包含所有功能实现
- `requirements.txt`：项目依赖包列表
- `PhotoWatermark_PRD.md`：产品需求文档
- `README.md`：项目说明文档
- `LICENSE`：许可证文件

### 依赖包
- [Pillow](https://python-pillow.org/)：Python图像处理库

## 许可证

本项目采用MIT许可证，详情请查看[LICENSE](LICENSE)文件。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持读取EXIF日期信息
- 支持自定义水印样式和位置
- 支持批量处理文件和目录