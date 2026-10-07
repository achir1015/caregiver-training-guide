"""用 Windows 內建繁中 OCR 把掃描 PDF 每頁轉成帶座標的文字行，存 ocr.json（不進版控）。

用法：python tools/ocr.py
需要：pip install pymupdf winocr pillow（Windows 10/11，需安裝繁體中文 OCR 語言）
"""
import json
import sys
from pathlib import Path

import pymupdf
import winocr
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "照顧服務員訓練指引.pdf"
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "ocr.json")  # 可指定輸出檔名


GAP = 40  # 2 倍解析度下約 1.7 個中文字寬


def pack(seg):
    x0 = min(b["x"] for b in seg)
    y0 = min(b["y"] for b in seg)
    x1 = max(b["x"] + b["width"] for b in seg)
    y1 = max(b["y"] + b["height"] for b in seg)
    return [round(x0), round(y0), round(x1), round(y1), " ".join(b["text"] for b in seg)]


def main():
    doc = pymupdf.open(PDF)
    done = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for i in range(doc.page_count):
        key = str(i + 1)
        if key in done:
            continue
        pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(2, 2))
        img = Image.frombytes("RGB", (pix.w, pix.h), pix.samples)
        r = winocr.recognize_pil_sync(img, "zh-Hant-TW")
        lines = []
        for line in r["lines"]:
            # 同一行中字距過大（雙欄表格被併成一行）時切開
            seg = []
            for w in line["words"]:
                b = w["bounding_rect"]
                if seg and b["x"] - (seg[-1]["x"] + seg[-1]["width"]) > GAP:
                    lines.append(pack(seg))
                    seg = []
                seg.append({**b, "text": w["text"]})
            if seg:
                lines.append(pack(seg))
        done[key] = {"w": pix.w, "h": pix.h, "lines": lines}
        if (i + 1) % 20 == 0:
            OUT.write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8")
            print(f"{i + 1}/{doc.page_count}", file=sys.stderr, flush=True)
    OUT.write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8")
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
