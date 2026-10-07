"""產生網站圖示：favicon、apple-touch-icon、PWA 圖示（含 maskable）：藍底、奶油色愛心、「照」字。

用法：python tools/make_icons.py
需要：pip install pillow；字型使用 Windows 微軟正黑體粗體
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "icons"
FONT = "C:/Windows/Fonts/msjhbd.ttc"
TEAL = (45, 106, 138)
CREAM = (246, 244, 239)
S = 1024  # 先畫大圖再縮小，邊緣較平滑


def draw(full_bleed: bool) -> Image.Image:
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if full_bleed:
        d.rectangle([0, 0, S, S], fill=TEAL)
        scale, cx, cy = 0.72, S / 2, S / 2  # maskable：主體留在安全區內
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=TEAL)
        scale, cx, cy = 0.9, S / 2, S / 2

    def p(x, y):  # 以 0–1 座標定位，並依 scale 縮放到中心
        return (cx + (x - 0.5) * S * scale, cy + (y - 0.5) * S * scale)

    # 愛心（照顧）＋「照」字
    d.ellipse([p(0.10, 0.10), p(0.54, 0.54)], fill=CREAM)
    d.ellipse([p(0.46, 0.10), p(0.90, 0.54)], fill=CREAM)
    d.polygon([p(0.115, 0.40), p(0.885, 0.40), p(0.5, 0.92)], fill=CREAM)
    font = ImageFont.truetype(FONT, int(S * scale * 0.40), index=0)
    x, y = p(0.5, 0.47)
    d.text((x, y), "照", font=font, fill=TEAL, anchor="mm")
    return img


def main():
    OUT.mkdir(exist_ok=True)
    rounded, bleed = draw(False), draw(True)
    for size in (16, 32, 48):
        rounded.resize((size, size), Image.LANCZOS).save(OUT / f"favicon-{size}.png")
    rounded.resize((48, 48), Image.LANCZOS).save(
        ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    for size in (192, 512):
        rounded.resize((size, size), Image.LANCZOS).save(OUT / f"icon-{size}.png")
        bleed.resize((size, size), Image.LANCZOS).save(OUT / f"maskable-{size}.png")
    # iOS 主畫面圖示不支援透明，用滿版底色
    bleed.convert("RGB").resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
    print("icons written to", OUT)


if __name__ == "__main__":
    main()
