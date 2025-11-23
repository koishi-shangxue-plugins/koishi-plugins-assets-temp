#!/usr/bin/env python3
"""
字体精简工具
将字体文件精简为只包含常用汉字和基本字符，以满足 CDN 20MB 限制
"""

from fontTools.ttLib import TTFont
from fontTools import subset
import sys
import os


def get_common_chinese_chars():
    """
    获取常用汉字集合
    包括：
    - GB2312 一级汉字（3755个）
    - GB2312 二级汉字（3008个）
    - 基本拉丁字母、数字、标点符号
    - 常用日文假名
    """
    chars = set()

    # 基本 ASCII 字符 (0x20-0x7E)
    chars.update(range(0x20, 0x7F))

    # 常用标点符号和符号
    chars.update(range(0x2000, 0x206F))  # 通用标点
    chars.update(range(0x3000, 0x303F))  # CJK 符号和标点
    chars.update(range(0xFF00, 0xFFEF))  # 半角及全角形式

    # GB2312 一级汉字 (0x4E00-0x9FA5 范围内的常用字)
    # 这里使用 GB2312 的范围
    chars.update(range(0x4E00, 0x9FA6))  # CJK 统一表意文字基本区

    # 日文平假名和片假名（用于日文游戏）
    chars.update(range(0x3040, 0x309F))  # 平假名
    chars.update(range(0x30A0, 0x30FF))  # 片假名

    return chars


def subset_font_aggressive(source_font_path, output_font_path):
    """
    激进精简字体，只保留常用字符
    
    Args:
        source_font_path: 需要精简的字体文件路径
        output_font_path: 输出的精简字体文件路径
    """
    print(f"正在读取源字体: {source_font_path}")
    source_font = TTFont(source_font_path)

    # 获取源字体的字符集
    source_chars = set()
    for table in source_font['cmap'].tables:
        source_chars.update(table.cmap.keys())
    print(f"源字体包含 {len(source_chars)} 个字符")

    # 获取常用字符集
    common_chars = get_common_chinese_chars()
    print(f"常用字符集包含 {len(common_chars)} 个字符")

    # 计算需要保留的字符（常用字符与源字体的交集）
    chars_to_keep = common_chars & source_chars
    print(f"\n将保留 {len(chars_to_keep)} 个字符")
    print(f"将移除 {len(source_chars) - len(chars_to_keep)} 个字符")

    # 使用 fonttools 的 subsetter 进行精简
    options = subset.Options()
    options.drop_tables = ['DSIG']  # 移除数字签名表
    options.desubroutinize = True  # 简化字体结构
    options.hinting = False  # 移除 hinting 信息
    options.legacy_kern = False  # 移除旧式字距调整
    options.layout_features = ['*']  # 保留所有布局特性

    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=chars_to_keep)
    subsetter.subset(source_font)

    print(f"\n正在保存精简后的字体到: {output_font_path}")
    source_font.save(output_font_path)
    source_font.close()

    # 显示文件大小对比
    original_size = os.path.getsize(source_font_path) / (1024 * 1024)
    new_size = os.path.getsize(output_font_path) / (1024 * 1024)
    print(f"\n原始文件大小: {original_size:.2f} MB")
    print(f"精简后大小: {new_size:.2f} MB")
    print(f"压缩率: {(1 - new_size/original_size) * 100:.1f}%")

    if new_size <= 20:
        print(f"\n✓ 成功！文件大小 {new_size:.2f} MB，符合 CDN 限制（≤20MB）")
    else:
        print(f"\n✗ 警告：文件大小 {new_size:.2f} MB，仍超过 CDN 限制（20MB）")
        print(f"建议：可以进一步减少字符集范围")


if __name__ == "__main__":
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 处理两个字体文件
    fonts_to_process = [
        ("SourceHanSerifSC.otf", "SourceHanSerifSC-subset.otf"),
        ("SourceHanSansSC-Bold.otf", "SourceHanSansSC-Bold-subset.otf")
    ]

    for source_name, output_name in fonts_to_process:
        source_font = os.path.join(script_dir, source_name)
        output_font = os.path.join(script_dir, output_name)

        print("=" * 70)
        print(f"处理字体: {source_name}")
        print("=" * 70)

        try:
            subset_font_aggressive(source_font, output_font)
            print("\n处理完成！\n")
        except FileNotFoundError:
            print(f"\n错误：找不到字体文件: {source_font}")
            continue
        except Exception as e:
            print(f"\n错误：{e}")
            import traceback
            traceback.print_exc()
            continue

    print("=" * 70)
    print("所有字体处理完成！")
    print("=" * 70)
