"""
Script tiện ích chuyển đổi PDF sang Markdown bằng MarkItDown.
Hỗ trợ:
- Chuyển đổi 1 file PDF bất kỳ.
- Chuyển đổi toàn bộ file PDF trong 1 thư mục.
- Chạy trực tiếp từ dòng lệnh hoặc chạy tương tác (nhập đường dẫn khi được hỏi).
"""

import os
import sys
import argparse
from pathlib import Path

# Đảm bảo console Windows in được tiếng Việt UTF-8 không bị lỗi charmap
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from markitdown import MarkItDown


def convert_single_pdf(md: MarkItDown, pdf_path: Path, output_path: Path = None):
    if not pdf_path.exists():
        print(f"[X] Lỗi: Không tìm thấy file '{pdf_path}'")
        return False

    if output_path is None:
        output_path = pdf_path.with_suffix(".md")

    print(f"[*] Đang chuyển đổi: {pdf_path.name} -> {output_path.name} ...")
    try:
        result = md.convert(str(pdf_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)
        print(f"[OK] Hoàn tất! File đã lưu tại: {output_path.resolve()}")
        return True
    except Exception as e:
        print(f"[X] Lỗi khi chuyển đổi file '{pdf_path.name}': {e}")
        return False


def convert_folder(md: MarkItDown, folder_path: Path, output_folder: Path = None):
    if not folder_path.is_dir():
        print(f"[X] Lỗi: Thư mục không hợp lệ: '{folder_path}'")
        return

    if output_folder is None:
        output_folder = folder_path / "markdown_outputs"

    output_folder.mkdir(parents=True, exist_ok=True)
    pdf_files = list(folder_path.glob("*.pdf"))

    if not pdf_files:
        print(f"[!] Không tìm thấy file PDF nào trong thư mục: {folder_path}")
        return

    print(f"[*] Tìm thấy {len(pdf_files)} file PDF. Bắt đầu chuyển đổi...")
    success_count = 0
    for pdf_file in pdf_files:
        out_file = output_folder / f"{pdf_file.stem}.md"
        if convert_single_pdf(md, pdf_file, out_file):
            success_count += 1

    print(f"\n[OK] Đã hoàn thành {success_count}/{len(pdf_files)} file.")
    print(f"[OK] Thư mục kết quả: {output_folder.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Chuyển đổi PDF sang Markdown bằng MarkItDown")
    parser.add_argument("path", nargs="?", help="Đường dẫn đến file PDF hoặc thư mục chứa PDF")
    parser.add_argument("-o", "--output", help="Đường dẫn file .md đầu ra hoặc thư mục đầu ra")
    parser.add_argument("--ocr", action="store_true", help="Bật plugin OCR (yêu cầu cấu hình LLM)")
    
    args = parser.parse_args()

    # Khởi tạo MarkItDown
    enable_plugins = args.ocr
    md = MarkItDown(enable_plugins=enable_plugins)

    target_path_str = args.path
    if not target_path_str:
        print("=== CÔNG CỤ CHUYỂN ĐỔI PDF SANG MARKDOWN ===")
        target_path_str = input("Nhập đường dẫn file PDF hoặc thư mục chứa PDF: ").strip().strip('"').strip("'")

    if not target_path_str:
        print("[!] Bạn chưa nhập đường dẫn. Thoát chương trình.")
        sys.exit(0)

    target_path = Path(target_path_str)
    output_path = Path(args.output) if args.output else None

    if target_path.is_file():
        convert_single_pdf(md, target_path, output_path)
    elif target_path.is_dir():
        convert_folder(md, target_path, output_path)
    else:
        print(f"[X] Không tìm thấy đường dẫn: {target_path}")


if __name__ == "__main__":
    main()
