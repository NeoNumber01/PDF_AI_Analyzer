"""
PDF 转图片模块

使用 PyMuPDF (fitz) 将 PDF 文件的每一页转换为 PNG 图片
无需安装 Poppler 等外部依赖
"""
import os
import sys
from pathlib import Path
from typing import List

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz  # PyMuPDF
from PIL import Image
import io

import config


def convert_pdf_to_images(pdf_path: str, output_dir: str = None) -> List[str]:
    """
    将 PDF 每一页转换为 PNG 图片
    
    Args:
        pdf_path: PDF 文件路径
        output_dir: 图片输出目录（默认使用配置中的 OUTPUT_DIR）
    
    Returns:
        按页码排序的图片路径列表
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
    
    # 使用默认输出目录
    if output_dir is None:
        output_dir = config.OUTPUT_DIR
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 为这个 PDF 创建子目录
    pdf_name = pdf_path.stem
    pdf_output_dir = output_dir / pdf_name
    pdf_output_dir.mkdir(exist_ok=True)
    
    print(f"正在将 PDF 转换为图片: {pdf_path}")
    print(f"输出目录: {pdf_output_dir}")
    
    # 使用 PyMuPDF 打开 PDF
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        raise RuntimeError(f"无法打开 PDF 文件: {e}")
    
    image_paths = []
    total_pages = len(doc)
    
    # DPI 转换为缩放因子 (默认 PDF 是 72 DPI)
    zoom = config.PDF_DPI / 72
    matrix = fitz.Matrix(zoom, zoom)
    
    for page_num in range(total_pages):
        page = doc[page_num]
        
        # 渲染页面为图片
        pix = page.get_pixmap(matrix=matrix)
        
        # 保存为 PNG
        image_path = pdf_output_dir / f"page_{page_num + 1:03d}.png"
        pix.save(str(image_path))
        
        image_paths.append(str(image_path))
        print(f"  已转换第 {page_num + 1}/{total_pages} 页")
    
    doc.close()
    
    print(f"转换完成! 共 {len(image_paths)} 页")
    return image_paths


def main():
    """命令行测试入口"""
    if len(sys.argv) < 2:
        print("用法: python pdf_converter.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    images = convert_pdf_to_images(pdf_path)
    
    print("\n生成的图片：")
    for img in images:
        print(f"  {img}")


if __name__ == "__main__":
    main()
