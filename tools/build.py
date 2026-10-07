"""把 ocr.json（tools/ocr.py 產生）整理成依章節排列的閱讀資料。

用法：python tools/build.py
產出（皆含書籍內容，已列入 .gitignore，不上傳公開 repo）：
  data.js                         本機開啟 index.html 時讀取
  download/照顧服務員訓練指引-資料.json   給網站「匯入資料」用（手機／平板）
  download/照顧服務員訓練指引.html        單檔版（資料內嵌，可離線開啟）
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OCR = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "ocr.json")
PDF_NAME = "照顧服務員訓練指引.pdf"
TITLE = "照顧服務員訓練指引"

# 目錄（書內頁碼）：(章, [(節, 起始頁), ...])；章的第一個值是章起始頁
TOC = [
    ("第1章 緒論", 1, [
        ("第一節 照顧服務員名稱由來", 3),
        ("第二節 照顧服務團隊及照顧服務員的角色功能", 4),
        ("第三節 照顧服務員的工作場所", 8),
        ("第四節 照顧服務員的服務對象與內容", 10),
        ("第五節 照顧服務員應具備的條件與特質", 14),
        ("第六節 照顧服務員的態度與形象", 17),
        ("第七節 照顧服務員的工作倫理守則", 18),
    ]),
    ("第2章 照顧服務相關法律、政策與資源", 25, [
        ("第一節 照顧服務相關法律", 27),
        ("第二節 照顧服務相關政策與資源", 33),
    ]),
    ("第3章 認識身心障礙者及其需求與服務", 43, [
        ("第一節 認識身心障礙者及相關政策", 45),
        ("第二節 各類身心障礙者之特質與服務需求", 50),
        ("第三節 正向行為支持與行為危機處理原則", 59),
    ]),
    ("第4章 認識失智症及其需求與服務", 69, [
        ("第一節 認識失智症", 71),
        ("第二節 失智症患者之日常生活照顧", 75),
        ("第三節 與失智症患者之互動與溝通技巧", 79),
        ("第四節 促進失智症患者參與生活與活動安排之原則", 81),
    ]),
    ("第5章 認識家庭照顧者與服務技巧", 87, [
        ("第一節 家庭主要照顧者的壓力", 89),
        ("第二節 協助家庭照顧者調適", 92),
        ("第三節 與家屬溝通的技巧與態度", 96),
    ]),
    ("第6章 原住民族文化安全導論", 103, [
        ("第一節 原住民所面臨之社會及健康不均等現象", 105),
        ("第二節 認識文化敏感度及其於照顧中之重要性", 106),
        ("第三節 原住民族照顧過程之文化安全概念與因素", 109),
        ("第四節 文化適切性之照顧模式、倫理困境與議題", 111),
        ("第五節 文化照顧知能、態度及技能", 115),
    ]),
    ("第7章 心理健康與壓力調適", 119, [
        ("第一節 服務對象的心理特質與需求", 121),
        ("第二節 認識憂鬱症", 125),
        ("第三節 自殺的徵兆與預防", 128),
        ("第四節 照顧服務員壓力自我覺察與調適", 131),
    ]),
    ("第8章 人際關係與溝通技巧", 137, [
        ("第一節 溝通的重要性", 139),
        ("第二節 影響溝通的因素", 141),
        ("第三節 如何增進溝通的能力", 146),
        ("第四節 特殊溝通情境的處理", 150),
        ("第五節 建立與被照顧者良好的溝通技巧", 153),
    ]),
    ("第9章 身體結構與功能", 165, [
        ("第一節 身體的組成", 167),
        ("第二節 身體各系統之構造與功能", 169),
    ]),
    ("第10章 基本生命徵象", 195, [
        ("第一節 體溫", 197),
        ("第二節 脈搏", 202),
        ("第三節 呼吸", 205),
        ("第四節 血壓", 207),
        ("第五節 血糖", 211),
    ]),
    ("第11章 基本生理需求", 227, [
        ("第一節 知覺之需要", 230),
        ("第二節 活動之需要", 233),
        ("第三節 休息與睡眠之需要", 235),
        ("第四節 身體清潔與舒適之需要", 237),
        ("第五節 基本營養之需要與協助進食", 238),
        ("第六節 腸道排泄之需要", 246),
        ("第七節 泌尿道排泄之需要", 249),
        ("第八節 呼吸之需要", 253),
    ]),
    ("第12章 身體活動與運動輔具", 269, [
        ("第一節 身體姿勢與適當擺位", 271),
        ("第二節 運動障礙與被動運動", 273),
        ("第三節 輔具之使用", 282),
        ("第四節 按摩法", 291),
        ("第五節 制動合併症的簡易處理原則", 295),
        ("第六節 長照機構中常見的休閒活動", 299),
        ("第七節 居家安全環境與居家安全看視", 302),
    ]),
    ("第13章 身體清潔與舒適", 333, [
        ("第一節 個人衛生", 335),
        ("第二節 個人衛生照顧活動項目", 336),
    ]),
    ("第14章 營養膳食與備餐原則", 383, [
        ("第一節 營養介紹", 385),
        ("第二節 各類營養素的功能與來源", 389),
        ("第三節 影響食物攝取與營養狀態的因素", 394),
        ("第四節 服務對象的營養需求", 395),
        ("第五節 各種特殊飲食的認識", 402),
    ]),
    ("第15章 家務處理", 415, [
        ("第一節 家務處理的功能及目標", 417),
        ("第二節 家務處理的基本原則", 418),
        ("第三節 家務處理工作內容及準則", 419),
        ("第四節 家務工作的安全", 424),
    ]),
    ("第16章 疾病徵兆之認識及老人常見疾病之照顧", 429, [
        ("第一節 身體正常與異常徵象的觀察與記錄", 431),
        ("第二節 冷熱效應之應用", 455),
        ("第三節 感染之預防", 461),
        ("第四節 老人生病徵兆與照顧原則", 466),
        ("第五節 標本收集與記錄", 468),
    ]),
    ("第17章 意外災害的緊急處理", 491, [
        ("第一節 意外災害的定義", 493),
        ("第二節 緊急災害的預防、逃生要領及災後影響", 494),
        ("第三節 日常安全維護與緊急災害時病人的疏散", 509),
        ("第四節 常見意外的預防與處理", 518),
        ("第五節 機構緊急災害應變計畫", 527),
    ]),
    ("第18章 急救與急症之處理", 533, [
        ("第一節 急救概論", 535),
        ("第二節 創傷的處理", 541),
        ("第三節 敷料、繃帶與包紮", 552),
        ("第四節 肌肉、關節、骨骼之損傷", 562),
        ("第五節 心肺復甦術", 569),
        ("第六節 異物哽塞的處理", 580),
        ("第七節 癲癇的處理", 583),
    ]),
    ("第19章 居家用藥安全", 593, [
        ("第一節 藥物的種類", 595),
        ("第二節 了解藥物儲存安全", 600),
        ("第三節 認識藥袋說明", 602),
        ("第四節 給藥方式及學習正確協助服藥", 604),
    ]),
    ("第20章 臨終關懷及安寧照顧", 609, [
        ("第一節 臨終關懷的精神與內容", 612),
        ("第二節 照顧瀕死服務對象的壓力與調適", 615),
        ("第三節 安寧照顧的發展與實踐", 618),
        ("第四節 臨終服務對象及其家屬的心理調適過程", 621),
        ("第五節 遺體護理與喪葬", 624),
        ("第六節 警政及衛政之通報", 628),
    ]),
    ("第21章 就業市場、人力培訓與求職技巧", 633, [
        ("第一節 就業市場趨勢分析", 635),
        ("第二節 照顧服務員人力培訓與就業相關政策", 639),
        ("第三節 求職技巧", 642),
    ]),
    ("第22章 性別平等", 647, [
        ("第一節 照顧服務員與性別平等", 649),
        ("第二節 性別平等相關法規", 652),
        ("第三節 職場性騷擾", 655),
    ]),
    ("附錄", 661, [
        ("附錄一 照顧服務員訓練實施計畫", 662),
        ("附錄二 老人福利法", 673),
        ("附錄三 身心障礙者權益保障法", 679),
        ("附錄四 醫院自擬的病人活動能力評估表", 694),
        ("附錄五 個人理想體重", 695),
        ("附錄六 限制熱量飲食選擇表", 696),
        ("附錄七 流質／半流質飲食選擇表", 697),
        ("附錄八 管灌飲食選擇表", 698),
        ("附錄九 高纖維飲食選擇表", 700),
        ("附錄十 糖尿病飲食選擇表", 701),
        ("附錄十一 高血壓飲食選擇表", 702),
        ("附錄十二 高脂血症飲食選擇表", 703),
        ("附錄十三 痛風飲食選擇表", 704),
        ("附錄十四 慢性腎臟病飲食選擇表", 705),
    ]),
]

# 技術目錄：(編號, 名稱, 頁)
SKILLS = [
    ("10-1", "以耳溫槍測量耳溫", 213), ("10-2", "測量橈動脈脈搏", 216), ("10-3", "測量呼吸", 217),
    ("10-4", "使用電子血壓計測量血壓", 218), ("10-5", "測量血糖", 220),
    ("11-1", "協助抽吸及氧氣使用", 256), ("11-2", "鼻胃管灌食法", 259), ("11-3", "鼻胃管護理", 262),
    ("11-4", "胃造口管灌食法及護理", 264),
    ("12-1", "仰臥", 306), ("12-2", "側臥", 308), ("12-3", "半坐臥式", 310), ("12-4", "俯臥", 311),
    ("12-5", "翻身", 312), ("12-6", "協助服務對象移至床頭", 314), ("12-7", "協助服務對象移至床邊", 316),
    ("12-8", "協助服務對象坐在床緣", 318), ("12-9", "協助服務對象下床", 320),
    ("12-10", "協助服務對象坐入椅子（或輪椅）", 322), ("12-11", "協助服務對象自椅子（或輪椅）返回病床", 324),
    ("12-12", "協助服務對象由床上移到推床", 326), ("12-13", "三人搬運法", 328),
    ("13-1", "臥有病人床鋪法", 346), ("13-2", "修面、剃鬍鬚", 349), ("13-3", "床上洗頭", 351),
    ("13-4", "特別口腔清潔法", 353), ("13-5", "床上沐浴", 356), ("13-6", "背部護理", 361),
    ("13-7", "協助服務對象更衣", 365), ("13-8", "指（趾）甲護理", 367),
    ("13-9", "協助服務對象床上使用便盆", 369), ("13-10", "會陰沖洗法", 371), ("13-11", "尿管清潔", 375),
    ("13-12", "甘油球灌腸", 377),
    ("16-1", "協助服務對象使用冰枕（或冰袋、冰寶）", 471), ("16-2", "協助服務對象使用溼冷敷", 473),
    ("16-3", "協助服務對象使用熱水袋", 475), ("16-4", "協助服務對象使用溼熱敷", 477),
    ("16-5", "協助服務對象溫水坐浴", 479), ("16-6", "協助服務對象使用蒸氣吸入", 481),
    ("16-7", "使用無菌有蓋容器法", 483), ("16-8", "使用無菌敷料鉗", 484), ("16-9", "打開無菌包法", 485),
    ("16-10", "傾倒無菌溶液", 487), ("18-1", "成人心肺復甦術", 586), ("18-2", "哈姆立克法（腹戳法）", 588),
]

FIRST_PDF = 12          # 書頁 1 在 PDF 第 12 頁右半
LAST_PAGE = 731          # 原書頁數；截圖只到第 709 頁
CN = "一二三四五六七八九十"

NOISE_RE = re.compile(r"^(C?H?APTER|APPEN ?D[IⅨX]+|\(續\)|（續）|\d{1,3}|[A-Za-z]?\d{1,3}[A-Za-z]?|.{0,12}編著(／修訂|/修訂)?|本章大綱|學習目標|·?\d+%)$")
MARKER_RE = re.compile(
    r"^([一二三四五六七八九十]+[、,，.]|[(（][一二三四五六七八九十\d]+[)）]|\d+[.、,，]|[①-⑳]|[●•■□◆★※▲]|Step|步驟)"
)
END_RE = re.compile(r"[。：！？；:!?;」』）)]$")


def despace(t: str) -> str:
    """移除中文字之間的空白，保留英文單字間空白，並修正常見 OCR 誤判。"""
    t = re.sub(r"(?<=[^\x00-\x7f]) +|(?<=\S) +(?=[^\x00-\x7f])", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"(?<=\d) ?[|丨] ?(?=\d)", "1", t)            # 20 | 2 → 2012
    t = re.sub(r"(?<=[\d~])川|川(?=\d)", "11", t)              # 20川、8~川位
    t = re.sub(r"(?<=\d)Ⅱ", "11", t)
    t = re.sub(r"(?<=\d)[一ー](?=\d)", "-", t)                # 技術10一5 → 10-5
    t = re.sub(r"(?<![\dA-Za-z])-(?=[一-鿿])", "一", t)  # 按-下 → 按一下
    # 條列編號：I. l. 亻. & 開頭，以及「2照顧…」漏掉的點
    t = re.sub(r"^[Il](?=[.,、])", "1", t)
    t = re.sub(r"^亻(?=[.,])", "4", t)
    t = re.sub(r"^&(?=[一-鿿])", "8.", t)
    t = re.sub(r"^(\d{1,2}) ?[,，] ?(?=[^\d\s])", r"\1.", t)
    t = re.sub(r"^([1-9])(?=[一-鿿])(?![年月日個位人歲項次種名小時分條天週周成倍度級類期段])", r"\1.", t)
    for a, b in (("吿", "告"), ("説", "說"), ("悦", "悅"), ("閲", "閱"), ("囗", "口"), ("丶", "、")):
        t = t.replace(a, b)
    t = re.sub(r"(?<=\S)•", "：", t)
    return t


def pdf_page_map(ocr):
    """書頁 → (PDF 頁, 左0/右1)。依每張截圖底部「第 a-b 頁」判斷（原檔缺了幾張截圖），
    讀不到時沿用前一張 +2。書頁 1 在 PDF 第 12 頁右半。"""
    pm = {}
    a = -2
    for key in sorted(ocr, key=int):
        pno = int(key)
        if pno < FIRST_PDF:
            continue
        foot = "".join(t.replace(" ", "") for x0, y0, x1, y1, t in ocr[key]["lines"] if y0 > 1545)
        m = re.search(r"第(\d+)-(\d+)頁", foot)
        a = int(m.group(1)) if m and int(m.group(1)) % 2 == 0 and int(m.group(1)) > a else a + 2
        pm[a] = (pno, 0)
        pm[a + 1] = (pno, 1)
    pm.pop(0, None)
    return pm


def half_lines(page, side):
    """取出 PDF 某一頁左半或右半的內文行（去掉狀態列、頁碼、側邊章名）。"""
    w = page["w"]
    mid = w / 2
    out = []
    for x0, y0, x1, y1, t in page["lines"]:
        if y0 < 120 or y0 > 1545:
            continue
        if (x0 < mid) != (side == 0):
            continue
        if x0 < 185 or x0 > w - 190 or (y1 - y0) > 60:
            continue
        t = despace(t)
        if len(t) <= 1 or NOISE_RE.match(t.replace(" ", "")):
            continue
        off = 0 if side == 0 else mid
        out.append({"x0": x0 - off, "x1": x1 - off, "y0": y0, "h": y1 - y0, "t": t})
    out.sort(key=lambda l: l["y0"])
    return out


def page_rows(ocr, pm, pg):
    """一個書頁的內文行：(line, 書頁, 左邊界, 右邊界)。
    技術操作的「步驟｜說明」雙欄表格：右欄說明掛到左欄對應步驟（line["note"]），避免交錯。"""
    if pg not in pm:
        return []
    pno, side = pm[pg]
    page = ocr.get(str(pno))
    if not page:
        return []
    lines = half_lines(page, side)
    if not lines:
        return []
    xs = sorted(l["x0"] for l in lines)
    L = xs[len(xs) // 10]
    R = sorted(l["x1"] for l in lines)[int(len(lines) * 0.9)]
    right = [l for l in lines if l["x0"] >= L + 420 and l["h"] < 26]
    left = [l for l in lines if l["x1"] <= L + 415]
    if len(right) >= 4 and len(left) >= 4:
        main_ = [l for l in lines if l not in right]
        notes = []
        for l in right:   # 右欄依縮排合併成段
            if notes and not re.match(r"^[·•.。,]|^\d+[.]", l["t"]) and l["y0"] - notes[-1]["y1"] < 50:
                notes[-1]["t"] += l["t"]
                notes[-1]["y1"] = l["y0"]
            else:
                notes.append({"y0": l["y0"], "y1": l["y0"], "t": re.sub(r"^[·•.。,]\s*", "", l["t"])})
        for n in notes:
            tgt = None
            for l in main_:
                if l["y0"] <= n["y0"] + 8 and MARKER_RE.match(l["t"]):
                    tgt = l
            tgt = tgt or next((l for l in main_ if l["y0"] >= n["y0"]), main_[-1] if main_ else None)
            if tgt is not None:
                tgt.setdefault("note", []).append(n["t"])
        lines = main_
        R = L + 400   # 表格內左欄較窄
    return [(l, pg, L, R) for l in lines]


SKILL_RE = re.compile(r"^技術\s*(\d+\s*[-一–]\s*\d+)$")


def to_blocks(rows):
    """rows: [(line, 書頁, 左邊界, 右邊界)] → 段落 blocks"""
    blocks = []
    prev = None
    pending = ""  # 「技術10-1」標籤，接到下一個標題前
    for ln, pg, L, R in rows:
        t, h = ln["t"], ln["h"]
        m = SKILL_RE.match(t.replace(" ", ""))
        if m:
            pending = "技術" + re.sub(r"[一–\s]", "-", m.group(1)).replace("--", "-") + " "
            prev = None
            continue
        if h >= 25:
            t = re.sub(r"^[0O○◎]\s*(?=[一-鿿])", "", t)  # 標題前的圖示
        if h >= 27.5 and len(t) <= 32:
            t = re.sub(r"^[一ー-]\s*(?=\S{2})", "", t) if h >= 30 else re.sub(
                r"^([一二三四五六七八九十]{1,2})(?=[一-鿿]{2})(?!、)", r"\1、", t)
            blocks.append({"t": "h3", "x": pending + t, "pg": pg})
            pending, prev = "", None
            continue
        if h >= 25 and len(t) <= 26 and not END_RE.search(t) and ln["x1"] < R - 60:
            blocks.append({"t": "h4", "x": pending + t, "pg": pg})
            pending, prev = "", None
            continue
        if pending:
            blocks.append({"t": "h3", "x": pending.strip(), "pg": pg})
            pending = ""
        indent = ln["x0"] - L
        is_marker = bool(MARKER_RE.match(t))
        cont = (
            prev is not None
            and blocks and blocks[-1]["t"] in ("p", "li")
            and prev["x1"] >= R - 45            # 上一行寫滿
            and not is_marker
            and indent < 38                     # 不是首行縮排
        )
        if cont:
            last = blocks[-1]["x"]
            sep = " " if re.search(r"[A-Za-z0-9,]$", last) and re.match(r"[A-Za-z0-9(]", t) else ""
            blocks[-1]["x"] = last + sep + t
        else:
            blocks.append({"t": "li" if is_marker else "p", "x": t, "pg": pg, "_ind": indent})
        if ln.get("note"):
            blocks[-1].setdefault("_note", []).extend(ln["note"])
        prev = ln
    # 補回 OCR 漏掉的「1.」，並修正把 1 認成 7 的情形
    num = re.compile(r"^(\d+)\.")
    for i, b in enumerate(blocks):
        nxt = next((x for x in blocks[i + 1:i + 4] if x["t"] == "li" and num.match(x["x"])), None)
        if not nxt or not num.match(nxt["x"]).group(1) == "2":
            continue
        if b["t"] == "li" and b["x"].startswith("7."):
            b["x"] = "1." + b["x"][2:]
        elif b["t"] == "p" and 8 <= b.get("_ind", 0) < 38 and (i == 0 or blocks[i - 1]["t"] != "li"):
            b["t"], b["x"] = "li", "1." + b["x"]
    for b in blocks:
        b.pop("_ind", None)
        if b.get("_note"):
            b["n"] = "；".join(b.pop("_note"))
        b.pop("_note", None)
    return blocks


SEC_LABEL = re.compile(r"^(第\s*([一二三四五六七八九十]+)\s*節|附錄\s*([一二三四五六七八九十]+))")


def sec_name(title):
    return re.sub(r"^(第.節|附錄[一二三四五六七八九十]+)\s*", "", title)


def find_cut(rows, title):
    """在起始頁找到「第X節」「附錄X」標記，或與節名相符的大標題。"""
    m = SEC_LABEL.match(title)
    want = m.group(2) or m.group(3)
    for i, (ln, *_rest) in enumerate(rows):
        mm = SEC_LABEL.match(ln["t"].replace(" ", ""))
        if mm and (mm.group(2) or mm.group(3)) == want:
            return i
    name = sec_name(title)
    for i, (ln, *_rest) in enumerate(rows):
        t = ln["t"].replace(" ", "")
        if ln["h"] >= 29 and len(t) >= 2 and (t[:4] in name or name[:4] in t):
            return i
    return None


def main():
    ocr = json.loads(OCR.read_text(encoding="utf-8"))
    pm = pdf_page_map(ocr)
    # 扁平化：所有節（含各章「導讀」）及起始頁；章首頁是封面大綱，略過
    flat, covers = [], set()
    for chap, cstart, secs in TOC:
        covers.add(cstart)
        if secs[0][1] > cstart + 1:
            flat.append((chap, "本章導讀", cstart + 1))
        for title, start in secs:
            flat.append((chap, title, start))
    stream = []
    for pg in range(1, LAST_PAGE + 1):
        if pg not in covers:
            stream.extend(page_rows(ocr, pm, pg))
    first_idx = {}
    for i, (ln, pg, *_r) in enumerate(stream):
        first_idx.setdefault(pg, i)

    def locate(title, start):
        pages = [p for p in range(start, start + 3) if p in first_idx]
        if not pages:
            return None
        if title == "本章導讀":
            return first_idx[pages[0]]
        for p in pages[:2]:
            i0 = first_idx[p]
            rows = [r for r in stream[i0:] if r[1] == p]
            c = find_cut(rows, title)
            if c is not None:
                return i0 + c
        return first_idx[pages[0]]

    cuts = []
    for chap, title, start in flat:
        c = locate(title, start)
        if c is None or (cuts and c < cuts[-1]):
            c = cuts[-1] if cuts else 0
        cuts.append(c)
    cuts.append(len(stream))

    sections = []
    for i, (chap, title, start) in enumerate(flat):
        rows = stream[cuts[i]:cuts[i + 1]]
        if rows and title != "本章導讀" and SEC_LABEL.match(rows[0][0]["t"].replace(" ", "")):
            rows = rows[1:]
        # 去掉開頭與節名相同的大標
        name = sec_name(title)
        while rows and len(rows[0][0]["t"]) <= 30 and rows[0][0]["h"] >= 29 and (
                rows[0][0]["t"].replace(" ", "")[:4] in name or name[:4] in rows[0][0]["t"].replace(" ", "")):
            rows.pop(0)
        end = flat[i + 1][2] - 1 if i + 1 < len(flat) else max(pm)
        sections.append({"id": f"s{i + 1}", "chap": chap, "title": title, "start": start,
                         "end": max(start, end), "blocks": to_blocks(rows)})

    data = {
        "title": TITLE,
        "source": PDF_NAME,
        "pages": LAST_PAGE,
        "pdf": {str(k): v[0] for k, v in pm.items()},
        "skills": [{"no": n, "name": t, "pg": p} for n, t, p in SKILLS],
        "sections": sections,
    }
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "data.js").write_text("window.MANUAL = " + js + ";\n", encoding="utf-8")
    dl = ROOT / "download"
    dl.mkdir(exist_ok=True)
    (dl / f"{TITLE}-資料.json").write_text(js, encoding="utf-8")
    build_standalone(js)
    nb = sum(len(s["blocks"]) for s in sections)
    nc = sum(len(b["x"]) for s in sections for b in s["blocks"])
    print(f"{len(sections)} sections, {nb} blocks, {nc} chars", file=sys.stderr)


def build_standalone(js):
    """單一 HTML 檔：資料與圖示內嵌，下載後直接開啟即可使用。"""
    import base64

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    html = html.replace('<script src="data.js"></script>', "<script>window.MANUAL = " + js.replace("</", "<\\/") + ";</script>")
    icon = base64.b64encode((ROOT / "icons" / "favicon-32.png").read_bytes()).decode()
    touch = base64.b64encode((ROOT / "icons" / "apple-touch-icon.png").read_bytes()).decode()
    html = re.sub(r'<link rel="(icon|manifest)"[^>]*>\n', "", html)
    html = html.replace(
        '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">',
        f'<link rel="icon" type="image/png" href="data:image/png;base64,{icon}">\n'
        f'<link rel="apple-touch-icon" href="data:image/png;base64,{touch}">',
    )
    html = html.replace("const STANDALONE = false;", "const STANDALONE = true;")
    (ROOT / "download" / f"{TITLE}.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
