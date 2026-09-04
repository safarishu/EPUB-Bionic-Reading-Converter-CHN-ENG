import sys
import subprocess
import os
import shlex
import re

REQUIRED_PACKAGES = {
    'regex': 'regex',
    'bs4': 'beautifulsoup4',
    'lxml': 'lxml',
    'tqdm': 'tqdm'
}

def auto_install_dependencies():
    missing = []
    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        missing_str = " ".join(missing)
        print("=" * 45)
        print("⚠️  检测到运行当前脚本缺少以下依赖库：")
        for pkg in missing:
            print(f"  - {pkg}")
        print("=" * 45)
        
        choice = input("\n是否立即安装所需依赖？(y/n): ").strip().lower()
        
        if choice == 'y':
            print("\n🔧 正在安装依赖，请稍候...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
                print("✅ 所有依赖已成功安装！\n")
            except Exception as e:
                print(f"\n❌ 自动安装失败: {e}")
                print(f"请尝试在终端手动运行以下命令安装：\n  pip3 install {missing_str}")
                input("\n按回车键退出...")
                sys.exit(1)
        else:
            print("\n已取消安装。缺失依赖无法继续执行脚本。")
            print(f"如需手动安装，请在终端运行：\n  pip3 install {missing_str}")
            input("\n按回车键退出...")
            sys.exit(0)

auto_install_dependencies()

import zipfile
import math
import regex
from bs4 import BeautifulSoup
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def process_text(text, intensity, opacity):
    word_pattern = regex.compile(r'\b[\p{L}\p{M}]+\b', regex.UNICODE)
    
    def bionic_word(word):
        length = len(word)
        if length == 0:
            return word
        
        if intensity == '1':
            if length <= 4: fix_len = 1
            elif length <= 7: fix_len = 2
            else: fix_len = 3
        elif intensity == '3':
            fix_len = math.ceil(length / 2)
        else:
            if length <= 3: fix_len = 1
            elif length <= 6: fix_len = 2
            elif length <= 9: fix_len = 3
            else: fix_len = 4
            
        bold_part = f"<b>{word[:fix_len]}</b>"
        
        if fix_len < length:
            if opacity == 100:
                fade_part = word[fix_len:]
            else:
                fade_style = f'style="opacity: {opacity / 100.0};"'
                fade_part = f'<span {fade_style}>{word[fix_len:]}</span>'
            return f"{bold_part}{fade_part}"
        else:
            return bold_part

    return word_pattern.sub(lambda m: bionic_word(m.group(0)), text)

def process_html_content(content, intensity, opacity):
    soup = BeautifulSoup(content, 'lxml')
    skip_tags = {'script', 'style', 'pre', 'code'}
    
    for element in soup.find_all(text=True):
        if element.parent.name not in skip_tags and element.strip():
            new_text = process_text(element.string, intensity, opacity)
            new_element = BeautifulSoup(new_text, 'html.parser')
            element.replace_with(new_element)
            
    return str(soup)

def process_epub(input_path, output_path, intensity, opacity):
    with zipfile.ZipFile(input_path, 'r') as zip_ref:
        file_list = zip_ref.infolist()
        total_files = len(file_list)
        
        with zipfile.ZipFile(output_path, 'w') as zip_out:
            with tqdm(total=total_files, desc="处理进度", unit="文件") as pbar:
                for file_info in file_list:
                    with zip_ref.open(file_info) as file:
                        content = file.read()
                        
                        if file_info.filename.endswith(('.html', '.xhtml', '.htm')):
                            content = process_html_content(content, intensity, opacity)
                        elif file_info.filename.endswith('content.opf'):
                            pass
                        
                        zip_out.writestr(file_info, content)
                    pbar.update(1)

def get_clean_path(path_str):
    path_str = path_str.strip()
    if not path_str:
        return ""

    path_str = os.path.expanduser(path_str)

    if sys.platform != "win32":
        try:
            parts = shlex.split(path_str)
            if parts:
                cleaned = parts[0]
            else:
                cleaned = path_str.strip('\'"')
        except Exception:
            cleaned = path_str.strip('\'"')
            cleaned = re.sub(r'\\(.)', r'\1', cleaned)
    else:
        cleaned = path_str.strip('\'" ')

    return os.path.abspath(cleaned)

def main():
    print("="*45)
    print(" 📖 EPUB 仿生阅读 (Bionic Reading) 转换器 ")
    print("Forked from dobrosketchkun's bionic-reading-epub-converter on GitHub")
    print("="*45)
    
    print("\n[1] 请选择加粗强度:")
    print("  1 - 低 (轻微引导，加粗极少字母)")
    print("  2 - 中 (默认强度，均衡加粗)")
    print("  3 - 高 (强引导，加粗前 50% 字母)")
    intensity = input("请输入 1/2/3 (直接回车默认 2): ").strip()
    if intensity not in ['1', '2', '3']:
        intensity = '2'

    print("\n[2] 请设置非加粗部分的透明度 (0-100):")
    print("  0 为完全透明，100 为完全不透明。")
    opacity_input = input("请输入数值 (直接回车默认 100): ").strip()
    try:
        opacity = int(opacity_input) if opacity_input else 100
        opacity = max(0, min(100, opacity))
    except ValueError:
        print("输入无效，将使用默认值 100。")
        opacity = 100

    print("\n[3] 请拖入需要转换的 EPUB 文件，或输入绝对路径:")
    input_path = input("文件路径: ")
    input_path = get_clean_path(input_path)

    if not os.path.exists(input_path) or not input_path.lower().endswith('.epub'):
        print(f"\n❌ 错误: 找不到文件或不是 EPUB 格式 -> {input_path}")
        input("\n按回车键退出...")
        return

    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    output_path = os.path.join(dir_name, f"bionic_{base_name}")

    if os.path.exists(output_path):
        print(f"\n⚠️ 警告: 输出文件 '{output_path}' 已存在，将被覆盖。")

    print("\n开始转换...")
    try:
        process_epub(input_path, output_path, intensity, opacity)
        print(f"\n✅ 转换完成！\n文件已保存至: {output_path}")
    except Exception as e:
        print(f"\n❌ 处理过程中发生错误: {str(e)}")
        
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
