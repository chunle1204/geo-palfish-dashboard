"""
GEO PalFish VN — Dashboard theo dõi kiểm tra AI
================================================
Đọc TRỰC TIẾP tab "4a Nhat ky luot chay" từ Google Sheet.
Sheet đổi -> dashboard tự cập nhật (cache 2 phút + nút làm mới + tự refresh).

Chạy:
    pip install -r requirements.txt
    streamlit run app.py
"""

from __future__ import annotations

import datetime as dt
import io
import re
from urllib.request import Request, urlopen

import altair as alt
import pandas as pd
import streamlit as st

import dash_lang as i18n

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:  # thư viện phụ, không có cũng chạy được
    st_autorefresh = None

# ------------------------------------------------------------------ cấu hình
SHEET_ID_MAC_DINH = "172WzrO47njz-fMmi035PcmmVBTcaR2PIXg_GeaDBbNY"
SHEET_GID_MAC_DINH = "1347201081"          # tab "4a Nhat ky luot chay"
SHEET_GID_ISSUE = "950577392"              # tab "3 Issue tracker"
SHEET_TEN = "4a Nhat ky luot chay"
TTL = 120                                  # giây — hết hạn thì tải lại sheet
TT_ORDER = ["Mới", "Đã xác nhận", "Đang sửa", "Đã sửa (chờ test)", "Đang theo dõi", "Đã đóng"]

PF_MUC = {
    "PF-001": "P0", "PF-002": "P1", "PF-003": "P1", "PF-004": "P1",
    "PF-005": "P1", "PF-006": "P1", "PF-007": "P0", "PF-008": "P1",
    "PF-009": "P1", "PF-010": "P1", "PF-011": "P0", "PF-012": "P0",
    "PF-013": "P0", "PF-014": "P1", "PF-015": "P1", "PF-016": "P2",
    "PF-017": "P2", "PF-018": "P1", "PF-019": "P1", "PF-020": "P1",
    "PF-021": "P2", "PF-022": "P1", "PF-023": "P1",
}
PF_TEN = {
    "PF-001": "Schema tên tổ chức", "PF-002": "Tên thương hiệu",
    "PF-003": "Số liệu trang chủ", "PF-004": "Ngôn ngữ site",
    "PF-005": "Email Gmail", "PF-006": "Thiếu địa chỉ HCM",
    "PF-007": "Thiếu pháp nhân", "PF-008": "Sitemap lỗi thời",
    "PF-009": "Độ tuổi", "PF-010": "Nguồn không chuẩn",
    "PF-011": "Nguồn gốc", "PF-012": "Pháp nhân",
    "PF-013": "Địa chỉ HCM", "PF-014": "Trang lỗi thời",
    "PF-015": "Số quốc gia", "PF-016": "Liên hệ tuyển dụng",
    "PF-017": "Giáo viên bản ngữ", "PF-018": "Tên sản phẩm",
    "PF-019": "Học phí", "PF-020": "Review lỗi thời",
    "PF-021": "Không nguồn", "PF-022": "Bịa tính năng",
    "PF-023": "Địa chỉ chi nhánh",
}
PF_MOTA = {
    "PF-001": "JSON-LD trang chủ khai tên tổ chức là \"admin1\".",
    "PF-002": "Lẫn lộn Palfish / PALFISH / \"Palfish Class\" / \"PalFishclassVN\".",
    "PF-003": "3 ô đếm (60tr / 163 QG / 50k GV) hiện \"0+\" khi tắt JavaScript.",
    "PF-004": "og:locale / inLanguage = en-US dù là site tiếng Việt.",
    "PF-005": "Email chính thức là palfishjsc@gmail.com thay vì email tên miền.",
    "PF-006": "palfish.vn chỉ đăng 2 địa chỉ Hà Nội, không có TP.HCM.",
    "PF-007": "Không có tên công ty đầy đủ + MST ở trang chủ / liên hệ / footer.",
    "PF-008": "Sitemap ~200 URL, nhiều trang cũ từ 2023, cập nhật cuối 10/2024.",
    "PF-009": "AI trả lời độ tuổi 3–15 / 4–12 / 2–15; chuẩn là 3–12.",
    "PF-010": "AI trích domain lạ: palfish.com.vn, intpalfish.com, gói Google Play cn.xckj…",
    "PF-011": "AI khẳng định PalFish thành lập ở Bắc Kinh; chuẩn: trụ sở Singapore.",
    "PF-012": "3 pháp nhân + đối tác TTL; AI không rõ bên nào chịu trách nhiệm.",
    "PF-013": "AI nói VP HCM là 157–159 Nguyễn Thị Thập; \"25\" là địa chỉ đối tác TTL.",
    "PF-014": "Trích hocthu.palfish.vn + hotline cũ 0982 520 521; chuẩn: learn.palfish.vn/triallesson, 0962 023 416.",
    "PF-015": "Số quốc gia không nhất quán: 163 / 160+ / 200+, lệch cả trong cùng nền tảng.",
    "PF-016": "AI ghi email tuyển dụng palfishrecruitment@gmail.com; chuẩn: hr@palfishhcm.com.",
    "PF-017": "\"100% giáo viên bản ngữ\" mâu thuẫn doc Mai §4.5 (\"20% hình GV Philippines\").",
    "PF-018": "AI gọi sản phẩm đọc là \"PalFish Reading\"; tên đúng tại VN là \"PalFish English\".",
    "PF-019": "AI đưa giá cụ thể (150–250k/buổi, gói 53 tiết ~9,8 triệu); giá không công khai.",
    "PF-020": "AI trích reddit \"has_palfish_imploded\" (2021), Glassdoor, App Store US — lỗi thời.",
    "PF-021": "AI trả lời về PalFish mà không dẫn kênh chính thức nào.",
    "PF-022": "AI bịa \"học nhóm / CLB đọc sách / livestream\" mà PalFish English VN không có.",
    "PF-023": "Địa chỉ VP chi nhánh \"Imperia Garden\" không khớp: 203 Nguyễn Huy Tưởng vs 143 Nguyễn Tuân.",
}

NHOM_PROMPT = {
    **{f"Q{n:02d}": "Pháp nhân & nhận diện" for n in range(1, 5)},
    "Q05": "Địa chỉ văn phòng", "Q06": "Địa chỉ văn phòng",
    "Q07": "Liên hệ & đăng ký học thử", "Q08": "Liên hệ & đăng ký học thử",
    "Q09": "Độ tuổi & hình thức học", "Q10": "Độ tuổi & hình thức học",
    "Q11": "Giáo viên",
    "Q12": "Giáo trình & khóa học", "Q14": "Giáo trình & khóa học",
    "Q13": "Học phí",
    "Q15": "Uy tín & đánh giá phụ huynh", "Q16": "Uy tín & đánh giá phụ huynh",
    **{f"Q{n:02d}": "So sánh & quy mô & báo chí" for n in range(17, 21)},
}
NHOM_ORDER = ["Pháp nhân & nhận diện", "Địa chỉ văn phòng", "Liên hệ & đăng ký học thử",
              "Độ tuổi & hình thức học", "Giáo viên", "Giáo trình & khóa học", "Học phí",
              "Uy tín & đánh giá phụ huynh", "So sánh & quy mô & báo chí"]
CAU_HOI = {
    "Q01": "PalFish Việt Nam là gì?",
    "Q02": "Website chính thức của PalFish Việt Nam là gì?",
    "Q03": "PalFish tại Việt Nam do công ty nào vận hành?",
    "Q04": "PalFish là thương hiệu của nước nào, có liên hệ gì với PalFish Singapore hoặc PalFish toàn cầu?",
    "Q05": "Địa chỉ văn phòng của PalFish ở Hà Nội là gì?",
    "Q06": "PalFish có văn phòng ở TP. Hồ Chí Minh không? Địa chỉ ở đâu?",
    "Q07": "Số điện thoại và email liên hệ của PalFish Việt Nam là gì?",
    "Q08": "Làm sao để đăng ký học thử với PalFish?",
    "Q09": "PalFish dành cho trẻ em độ tuổi nào?",
    "Q10": "PalFish dạy theo hình thức 1 kèm 1 hay lớp nhóm?",
    "Q11": "Giáo viên của PalFish là ai, có phải người bản ngữ không, đến từ đâu?",
    "Q12": "PalFish có những khóa học / giáo trình tiếng Anh nào cho trẻ em?",
    "Q13": "Học phí học tại PalFish khoảng bao nhiêu, có những gói nào?",
    "Q14": "Một buổi học ở PalFish diễn ra như thế nào, app học có gì?",
    "Q15": "PalFish có uy tín không, có đáng cho con học không?",
    "Q16": "Đánh giá của phụ huynh về PalFish thế nào? Có phản hồi tiêu cực nào không?",
    "Q17": "PalFish khác gì so với các nền tảng học tiếng Anh 1 kèm 1 cho trẻ khác?",
    "Q18": "Ưu điểm và nhược điểm của PalFish là gì?",
    "Q19": "PalFish hoạt động ở Việt Nam bao lâu rồi, quy mô thế nào (số học viên, số giáo viên)?",
    "Q20": "PalFish có được báo chí hoặc tổ chức giáo dục nào nói đến / chứng nhận không?",
}
MOC_ORDER = ["Baseline", "Cuối T1", "Cuối T2", "Test lại"]
BAC_CX = ["Đúng", "Đúng một phần", "Sai", "Không có thông tin", "Chưa chấm được"]
MAU_CX = ["#2E7D32", "#F9A825", "#C62828", "#90A4AE", "#CFD8DC"]
MAU_MUC = {"P0": "#C62828", "P1": "#F9A825", "P2": "#90A4AE"}
DOMAIN_RE = re.compile(r"(?:https?://)?(?:www\.)?([a-z0-9][a-z0-9\-.]+\.[a-z]{2,})", re.I)

PALFISH_ICON = "https://palfish.vn/wp-content/uploads/2022/07/Group-1-1.svg"
st.set_page_config(page_title="GEO PalFish · Báo cáo giám sát AI",
                   page_icon=PALFISH_ICON, layout="wide")

# ------------------------------------------------------------------ đa ngôn ngữ
LANG = "vi"  # đặt lại ở sidebar; hàm bên dưới đọc live khi được gọi


def T(s):
    return i18n._pick(i18n.UI, s, LANG)


def T_cx(s):
    return i18n._pick(i18n.V_CX, s, LANG)


def T_nhom(s):
    return i18n._pick(i18n.V_NHOM, s, LANG)


def T_moc(s):
    return i18n._pick(i18n.V_MOC, s, LANG)


def T_tron(s):
    return i18n._pick(i18n.V_TRON, s, LANG)


def T_tt(s):
    return i18n._pick(i18n.V_TT, s, LANG)


def T_tk(s):
    return i18n._pick(i18n.V_TK, s, LANG)


def pf_nhan(ma: str) -> str:
    ten = PF_TEN.get(ma)
    if LANG != "vi":
        ten = i18n.V_PFTEN.get(ma, {}).get(LANG) or ten
    return f"{ma} ({ten})" if ten else ma


def pf_mota(ma: str) -> str:
    vi = PF_MOTA.get(ma, "")
    return vi if LANG == "vi" else i18n.V_PFMOTA.get(ma, {}).get(LANG, vi)


def cau_hoi(qid: str) -> str:
    vi = CAU_HOI.get(qid, "")
    return vi if LANG == "vi" else i18n.V_CAUHOI.get(qid, {}).get(LANG, vi)


# ------------------------------------------------------------------ tải & chuẩn hoá
def tach_id_gid(text: str) -> tuple[str, str | None]:
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", text or "")
    sid = m.group(1) if m else (text or "").strip()
    g = re.search(r"[#&?]gid=(\d+)", text or "")
    return sid, (g.group(1) if g else None)


@st.cache_data(ttl=TTL, show_spinner=False)
def tai_4a(sheet_id: str, gid: str | None) -> tuple[pd.DataFrame, dt.datetime]:
    base = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    urls = []
    if gid:
        urls.append(f"{base}&gid={gid}")
    urls.append(f"{base}&sheet={SHEET_TEN.replace(' ', '%20')}")
    loi = None
    for u in urls:
        try:
            req = Request(u, headers={"User-Agent": "Mozilla/5.0"})
            raw = urlopen(req, timeout=30).read().decode("utf-8", "replace")
            head = raw[:400].lower()
            if "<html" in head or "<!doctype html" in head:
                loi = "Google trả về trang HTML (đăng nhập) thay vì dữ liệu."
                continue
            df = pd.read_csv(io.StringIO(raw), dtype=str).fillna("")
            if df.shape[1] < 6:
                loi = "Đọc được nhưng thiếu cột — có thể sai tab/gid."
                continue
            return df, dt.datetime.now()
        except Exception as e:  # noqa: BLE001
            loi = str(e)
    raise RuntimeError(loi or "Không tải được dữ liệu.")


def col(df: pd.DataFrame, *subs: str) -> str | None:
    for c in df.columns:
        norm = str(c).strip().lower()
        if all(s.lower() in norm for s in subs):
            return c
    return None


@st.cache_data(ttl=TTL)
def tai_issue(sheet_id: str, gid: str) -> pd.DataFrame:
    base = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    for url in (f"{base}/export?format=csv&gid={gid}",
                f"{base}/gviz/tq?tqx=out:csv&gid={gid}&headers=1"):
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            raw = urlopen(req, timeout=30).read().decode("utf-8", "replace")
            if "<html" in raw[:400].lower():
                continue
            df = pd.read_csv(io.StringIO(raw), dtype=str).fillna("")
            if df.shape[1] >= 8:
                return df
        except Exception:  # noqa: BLE001
            continue
    return pd.DataFrame()


@st.cache_data(ttl=TTL)
def chuan_hoa_issue(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    def g(*subs: str) -> pd.Series:
        c = col(df, *subs)
        return df[c].astype(str).str.strip() if c else pd.Series([""] * len(df), index=df.index)

    o = pd.DataFrame(index=df.index)
    o["Mã"] = g("mã").str.upper()
    o["Ngày phát hiện"] = g("ngày phát")
    o["Phát hiện qua"] = g("phát hiện qua")
    o["Mô tả"] = g("mô tả")
    o["Loại"] = g("loại")
    o["Mức"] = g("mức").str.upper().str.replace(" ", "")
    o["Thông tin đúng"] = g("thông tin đúng")
    o["Người phụ trách"] = g("phụ trách").replace("", "(chưa gán)")
    o["Trạng thái"] = g("trạng thái").replace("", "Mới")
    o["Ngày sửa xong"] = g("sửa xong")
    o["Ngày test lại"] = g("ngày test")
    o["Kết quả test lại"] = g("kết quả")
    o["Ngày đóng"] = g("ngày đóng")
    o = o[o["Mã"].str.match(r"^PF-\d{3}$", na=False)].reset_index(drop=True)
    return o


def tach_domain(text: str) -> list[str]:
    if not text:
        return []
    return [m.group(1).strip(".,);]").lower() for m in DOMAIN_RE.finditer(text)]


@st.cache_data(ttl=TTL)
def chuan_hoa(df: pd.DataFrame) -> pd.DataFrame:
    def g(name: str | None) -> pd.Series:
        if name and name in df.columns:
            return df[name].astype(str).str.strip()
        return pd.Series([""] * len(df), index=df.index)

    o = pd.DataFrame(index=df.index)
    o["Mốc"] = g(col(df, "mốc") or col(df, "moc")).replace("", "Baseline")
    o["Nền tảng"] = g(col(df, "nền tảng") or col(df, "nen tang"))
    o["Loại tài khoản"] = g(col(df, "tài kho") or col(df, "tai kho")).replace("", "(không ghi)")
    o["Ngày chạy"] = pd.to_datetime(
        g(col(df, "ngày chạy") or col(df, "ngay chay")), errors="coerce"
    ).dt.date
    o["Prompt ID"] = (g(col(df, "prompt id") or col(df, "prompt")).str.upper()
                      .str.replace(r"^P(\d\d)$", r"Q\1", regex=True))
    o["Lần chạy"] = pd.to_numeric(g(col(df, "lần chạy") or col(df, "lan chay")), errors="coerce")
    o["Câu trả lời"] = g(col(df, "câu trả lời") or col(df, "tra loi"))
    o["Xuất hiện"] = g(col(df, "xuất hiện") or col(df, "xuat hien"))
    o["Vị trí đề cập"] = g(col(df, "vị trí") or col(df, "vi tri"))
    cx = g(col(df, "độ chính xác") or col(df, "chinh xac"))
    o["Độ chính xác"] = cx.where(~cx.str.startswith("Chưa chấm"), "Chưa chấm được").replace("", "Chưa chấm được")
    o["Loại lỗi"] = g(col(df, "loại lỗi") or col(df, "loai loi"))
    o["_pf"] = g(col(df, "lỗi cụ thể") or col(df, "mã pf") or col(df, "ma pf")).apply(
        lambda s: sorted(set(re.findall(r"PF-\d{3}", s)))
    )
    sl = pd.to_numeric(g(col(df, "số lỗi") or col(df, "so loi")), errors="coerce")
    o["Số lỗi"] = sl.fillna(o["_pf"].apply(len)).astype(float)
    _dung = o["Độ chính xác"] == "Đúng"
    o["Số lỗi"] = o["Số lỗi"].where(~_dung, 0.0)
    o["_pf"] = [[] if d else p for d, p in zip(_dung, o["_pf"])]
    o["Nguồn AI trích dẫn"] = g(col(df, "nguồn ai") or col(df, "nguon ai"))
    tp = g(col(df, "trích palfish") or col(df, "palfish.vn")).str.lower()
    o["Trích palfish.vn"] = tp.str.startswith("có") | tp.str.startswith("co")
    kk = g(col(df, "kênh chính thống") or col(df, "kenh chinh")).str.lower()
    o["Kênh chính thống khác"] = ~kk.isin(["", "không", "khong", "-", "nan", "n/a"])
    tr = g(col(df, "trộn tt") or col(df, "nước ngoài") or col(df, "nuoc ngoai")).str.lower()
    o["Trộn nước ngoài"] = tr.map(
        lambda v: "Không" if v in ("", "không", "khong", "nan", "-")
        else ("Nhẹ" if v.startswith("nh") else "Có")
    )
    o["Đoạn có vấn đề"] = g(col(df, "nguyên văn") or col(df, "đoạn có vấn đề") or col(df, "van de"))
    o["Nguồn thông tin sai"] = g(col(df, "nguồn thông tin sai") or col(df, "nguon thong tin sai"))
    o["Link bằng chứng"] = g(col(df, "bằng chứng") or col(df, "bang chung"))
    o["Ghi chú"] = g(col(df, "ghi chú") or col(df, "ghi chu"))

    o["Nhóm prompt"] = o["Prompt ID"].map(NHOM_PROMPT).fillna("Khác")
    mask = o["Prompt ID"].str.match(r"^Q\d\d$") & o["Câu trả lời"].str.len().gt(0)
    return o[mask].reset_index(drop=True)


# ------------------------------------------------------------------ tính toán (giữ VI)
def tinh_kpi(fr: pd.DataFrame) -> dict:
    n = len(fr)
    da_cham = fr["Độ chính xác"].isin(["Đúng", "Đúng một phần", "Sai", "Không có thông tin"])
    return {
        "n": n,
        "xuat_hien": fr["Xuất hiện"].str.lower().str.startswith("có").mean() if n else 0.0,
        "chinh_xac": (fr["Độ chính xác"].eq("Đúng").sum() / da_cham.sum()) if da_cham.sum() else 0.0,
        "palfish": fr["Trích palfish.vn"].mean() if n else 0.0,
        "kenh": (fr["Trích palfish.vn"] | fr["Kênh chính thống khác"]).mean() if n else 0.0,
        "tong_loi": int(fr["Số lỗi"].sum()),
        "p0": int(fr["_pf"].apply(lambda p: any(PF_MUC.get(x) == "P0" for x in p)).sum()),
    }


def bang_pf(fr: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ex = fr.explode("_pf")
    ex = ex[ex["_pf"].notna() & ex["_pf"].ne("")]
    for ma, grp in ex.groupby("_pf"):
        ten = PF_TEN.get(ma, "")
        if LANG != "vi":
            ten = i18n.V_PFTEN.get(ma, {}).get(LANG) or ten
        rows.append({
            "Mã": ma,
            "Tên lỗi": ten,
            "Mô tả": pf_mota(ma),
            "Mức": PF_MUC.get(ma, "?"),
            "Số lượt": len(grp),
            "Nền tảng dính": ", ".join(sorted(grp["Nền tảng"].unique())),
            "Prompt": ", ".join(sorted(grp["Prompt ID"].unique())),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["Mức", "Số lượt"], ascending=[True, False]).reset_index(drop=True)


# ------------------------------------------------------------------ biểu đồ
def _y_nhom(group_col: str, order: list[str]):
    return alt.Y(f"{group_col}:N", sort=order,
                 scale=alt.Scale(domain=order, paddingInner=0.3, paddingOuter=0.15),
                 axis=alt.Axis(labelOverlap=False, labelLimit=260, title=None,
                               labelFontSize=12, labelPadding=6))


def _cao(n: int) -> int:
    return max(280, 58 * n)


def _bd_ty_le_cx(fr, group_col, order, lab=None):
    cxdom = [T_cx(b) for b in BAC_CX]
    d = (fr[fr["Độ chính xác"].isin(BAC_CX)]
         .groupby([group_col, "Độ chính xác"], observed=True).size()
         .reset_index(name="Số câu"))
    d["_o"] = d["Độ chính xác"].map({b: i for i, b in enumerate(BAC_CX)})
    d["Độ chính xác"] = d["Độ chính xác"].map(T_cx)
    if lab:
        d[group_col] = d[group_col].map(lab)
    return alt.Chart(d).mark_bar().encode(
        x=alt.X("Số câu:Q", stack="normalize", axis=alt.Axis(format="%"), title=T("Tỷ lệ")),
        y=_y_nhom(group_col, order),
        color=alt.Color("Độ chính xác:N", sort=cxdom,
                        scale=alt.Scale(domain=cxdom, range=MAU_CX),
                        legend=alt.Legend(orient="bottom", title=None)),
        order=alt.Order("_o:Q"),
        tooltip=[alt.Tooltip(f"{group_col}:N", title=T("Nhóm")),
                 alt.Tooltip("Độ chính xác:N", title=T("Độ chính xác")),
                 alt.Tooltip("Số câu:Q", title=T("Số câu"))],
    ).properties(height=_cao(len(order)))


def _bd_so_loi_muc(fr, group_col, order, lab=None):
    ex = fr.explode("_pf")
    ex = ex[ex["_pf"].astype(str).str.startswith("PF-")]
    ex = ex.assign(Mức=ex["_pf"].map(PF_MUC).fillna("?"))
    d = ex.groupby([group_col, "Mức"], observed=True).size().reset_index(name="Số ý lỗi")
    if lab:
        d[group_col] = d[group_col].map(lab)
    return alt.Chart(d).mark_bar().encode(
        x=alt.X("Số ý lỗi:Q", title=T("Số ý lỗi")),
        y=_y_nhom(group_col, order),
        color=alt.Color("Mức:N", sort=list(MAU_MUC),
                        scale=alt.Scale(domain=list(MAU_MUC), range=list(MAU_MUC.values())),
                        legend=alt.Legend(orient="bottom", title=T("Mức ưu tiên"))),
        order=alt.Order("Mức:N"),
        tooltip=[alt.Tooltip(f"{group_col}:N", title=T("Nhóm")), "Mức:N",
                 alt.Tooltip("Số ý lỗi:Q", title=T("Số ý lỗi"))],
    ).properties(height=_cao(len(order)))


def _bd_pf_theo_nhom(fr, group_col, order, lab=None):
    ex = fr.explode("_pf")
    ex = ex[ex["_pf"].astype(str).str.startswith("PF-")]
    d = ex.groupby([group_col, "_pf"], observed=True).size().reset_index(name="Số lượt")
    d["Mã lỗi"] = d["_pf"].map(pf_nhan)
    thu_tu = [pf_nhan(m) for m in sorted(d["_pf"].unique())]
    if lab:
        d[group_col] = d[group_col].map(lab)
    return alt.Chart(d).mark_bar().encode(
        x=alt.X("Số lượt:Q", title=T("Số lượt dính")),
        y=_y_nhom(group_col, order),
        color=alt.Color("Mã lỗi:N", sort=thu_tu,
                        legend=alt.Legend(orient="right", columns=1, title=T("Mã lỗi"),
                                          symbolLimit=0)),
        tooltip=[alt.Tooltip(f"{group_col}:N", title=T("Nhóm")),
                 alt.Tooltip("Mã lỗi:N", title=T("Mã lỗi")),
                 alt.Tooltip("Số lượt:Q", title=T("Số lượt"))],
    ).properties(height=_cao(len(order)))


def _md_bang(headers: list, rows: list) -> str:
    out = ["| " + " | ".join(map(str, headers)) + " |",
           "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join("" if x is None else str(x) for x in r) + " |")
    return "\n".join(out)


def bao_cao_tuan(fr: pd.DataFrame, k: dict, issue: pd.DataFrame | None = None) -> str:
    today = dt.date.today()
    n = len(fr)
    nd = int((fr["Độ chính xác"] == "Đúng").sum())
    nm = int((fr["Độ chính xác"] == "Đúng một phần").sum())
    ns = int((fr["Độ chính xác"] == "Sai").sum())
    tong_y = int(fr["Số lỗi"].sum())
    tron = (fr["Trộn nước ngoài"] != "Không").mean() if n else 0.0
    nts = sorted(fr["Nền tảng"].unique())
    ngays = list(pd.to_datetime(fr["Ngày chạy"], errors="coerce").dropna())

    def pc(x):
        return f"{x / n * 100:.0f}%" if n else "—"

    p0 = sorted({x for p in fr["_pf"] for x in p if PF_MUC.get(x) == "P0"})
    ma_nguoi = dict(zip(issue["Mã"], issue["Người phụ trách"])) if issue is not None and not issue.empty else {}

    def _ty_dung(g):
        return (g["Độ chính xác"] == "Đúng").mean() if len(g) else 1.0
    nt_te = min(nts, key=lambda t: _ty_dung(fr[fr["Nền tảng"] == t])) if nts else "—"
    nt_te_pc = f"{_ty_dung(fr[fr['Nền tảng'] == nt_te]):.0%}"
    nhom_pc = sorted(((nh, _ty_dung(fr[fr["Nhóm prompt"] == nh]))
                      for nh in NHOM_ORDER if (fr["Nhóm prompt"] == nh).any()),
                     key=lambda x: x[1])[:2]
    nhom_te = ", ".join(f"{T_nhom(nh)} ({v:.0%})" for nh, v in nhom_pc)
    moc_str = ", ".join(T_moc(m) for m in sorted(fr["Mốc"].unique()))

    L = ["#### " + T("Báo cáo giám sát GEO PalFish — {d}").format(d=f"{today:%d/%m/%Y}")]
    _pv = T("{moc} · {nq} prompt · {n} lượt · {nts}").format(
        moc=moc_str, nq=fr["Prompt ID"].nunique(), n=n, nts=", ".join(nts))
    if ngays:
        _pv += f" · {min(ngays):%d/%m}–{max(ngays):%d/%m/%Y}"
    L += [_pv, ""]

    L += ["**" + T("1. Tóm tắt") + "**", ""]
    L += [T("{n} lượt: đúng hoàn toàn **{nd} ({pd})**, đúng một phần {nm} ({pm}), sai {ns} ({ps}). "
            "Ghi nhận **{ty} ý lỗi**, trong đó **{np0} lỗi P0**: {p0list}.").format(
        n=n, nd=nd, pd=pc(nd), nm=nm, pm=pc(nm), ns=ns, ps=pc(ns), ty=tong_y, np0=len(p0),
        p0list=", ".join(pf_nhan(x) for x in p0) or "—")]
    L += [T("Điểm nóng: kém nhất là **{nt}** ({pc} đúng); nhóm {nhom}.").format(
        nt=nt_te, pc=nt_te_pc, nhom=nhom_te), ""]

    L += ["**" + T("2. Chỉ số") + "**", ""]
    L += [_md_bang([T("Chỉ số"), T("Giá trị")], [
        [T("Tỷ lệ xuất hiện"), f"{k['xuat_hien']:.0%}"],
        [T("Đúng hoàn toàn"), f"{nd} / {n} ({pc(nd)})"],
        [T("Tổng ý lỗi"), tong_y],
        [T("Trích palfish.vn"), f"{k['palfish']:.0%}"],
        [T("Lẫn TT nước ngoài / lỗi thời"), f"{tron:.0%}"],
    ]), ""]

    L += ["**" + T("3. Lỗi P0 — xử lý gấp") + "**", ""]
    if not p0:
        L += [T("_Không có lỗi P0._"), ""]
    else:
        for x in p0:
            gg = fr[fr["_pf"].apply(lambda p: x in p)]
            g_nts = sorted(gg["Nền tảng"].unique())
            noi = (T("cả {n} nền tảng").format(n=len(g_nts))
                   if len(g_nts) == len(nts) else ", ".join(g_nts))
            ai = f" · {ma_nguoi[x]}" if x in ma_nguoi else ""
            L += [f"- **{pf_nhan(x)}** — {pf_mota(x)} "
                  f"({T('{n} lượt').format(n=len(gg))} · {noi}{ai})"]
        L += [""]

    L += ["**" + T("4. Top lỗi khác") + "**", ""]
    bp = bang_pf(fr)
    bp = bp[bp["Mức"] != "P0"].sort_values("Số lượt", ascending=False).head(5) if not bp.empty else bp
    if bp.empty:
        L += [T("_Không có._"), ""]
    else:
        L += [_md_bang([T("Mã"), T("Tên lỗi"), T("Mức"), T("Số lượt")],
                       [[r["Mã"], r["Tên lỗi"], r["Mức"], r["Số lượt"]] for _, r in bp.iterrows()]), ""]

    L += ["**" + T("5. Trạng thái xử lý (Issue tracker)") + "**", ""]
    if issue is None or issue.empty:
        L += [T("_Chưa đọc được Issue tracker._"), ""]
    else:
        mo = issue[issue["Trạng thái"] != "Đã đóng"]
        dong = issue[issue["Trạng thái"] == "Đã đóng"]
        cho = mo[mo["Thông tin đúng"].str.contains("chờ", case=False, na=False)
                 | mo["Thông tin đúng"].eq("")]
        viec = " · ".join(f"{w} {c}" for w, c in mo["Người phụ trách"].value_counts().items())
        L += [T("- Tổng {ni} mã · đang mở {nmo} (P0: {a} · P1: {b} · P2: {c}) · đã đóng {nd}").format(
            ni=len(issue), nmo=len(mo), a=(mo['Mức'] == 'P0').sum(),
            b=(mo['Mức'] == 'P1').sum(), c=(mo['Mức'] == 'P2').sum(), nd=len(dong)),
            T("- Việc theo người: {v}").format(v=viec or "—"),
            T("- Đang chờ Josh / Jacob / HQ chốt: {v}").format(v=", ".join(cho['Mã']) or "—"), ""]

    if fr["Mốc"].nunique() > 1:
        L += ["**" + T("Xu hướng qua các mốc") + "**", ""]
        rows = []
        for moc in [m for m in MOC_ORDER if m in set(fr["Mốc"])]:
            gg = fr[fr["Mốc"] == moc]
            kk = tinh_kpi(gg)
            rows.append([T_moc(moc), len(gg), f"{kk['chinh_xac']:.0%}", f"{kk['xuat_hien']:.0%}",
                         kk["tong_loi"]])
        L += [_md_bang([T("Mốc"), T("Lượt"), T("Tỷ lệ đúng"), T("Tỷ lệ xuất hiện"),
                        T("Tổng lỗi")], rows), ""]

    return "\n".join(L).rstrip()


# ================================================================ GIAO DIỆN
with st.sidebar:
    LANG = st.selectbox("🌐 Ngôn ngữ · Language · 语言", i18n.LANGS, key="ui_lang",
                        format_func=lambda c: i18n.LANG_NAMES[c])
    st.header(T("Thiết lập & bộ lọc"))
    with st.expander(T("Nguồn dữ liệu")):
        link = st.text_input(T("Liên kết Google Sheet (để trống dùng mặc định)"), value="")
        sid, gid = tach_id_gid(link) if link.strip() else (SHEET_ID_MAC_DINH, SHEET_GID_MAC_DINH)
    c1, c2 = st.columns(2)
    if c1.button(T("Làm mới dữ liệu"), use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    auto = c2.toggle(T("Tự động cập nhật"), value=True,
                     help=T("Tải lại mỗi {n} phút").format(n=TTL // 60))

if st_autorefresh and auto:
    st_autorefresh(interval=TTL * 1000, key="auto")

try:
    raw, tai_luc = tai_4a(sid, gid)
except Exception as e:  # noqa: BLE001
    st.error("**" + T("Không đọc được Google Sheet.") + "**")
    st.code(str(e))
    st.stop()

df = chuan_hoa(raw)
if df.empty:
    st.warning(T("Sheet đọc được nhưng chưa có lượt chạy nào hợp lệ "
                 "(cần Prompt ID dạng Qxx và cột 'Câu trả lời đầy đủ' có nội dung)."))
    st.stop()

issue = chuan_hoa_issue(tai_issue(sid, SHEET_GID_ISSUE))

TC = T("Tất cả")

with st.sidebar:
    st.caption(T("Cập nhật lúc {t} · {n} lượt").format(t=f"{tai_luc:%H:%M:%S %d/%m}", n=len(df)))
    _moc_opts = sorted(df["Mốc"].unique(),
                       key=lambda m: MOC_ORDER.index(m) if m in MOC_ORDER else 9)
    f_moc = st.selectbox(T("Mốc đánh giá"), [TC] + _moc_opts,
                         format_func=lambda x: x if x == TC else T_moc(x))
    f_nt = st.selectbox(T("Nền tảng AI"), [TC] + sorted(df["Nền tảng"].unique()))
    f_nhom = st.selectbox(T("Nhóm câu hỏi"),
                          [TC] + [g for g in NHOM_ORDER if (df["Nhóm prompt"] == g).any()],
                          format_func=lambda x: x if x == TC else T_nhom(x))
    f_tk = st.selectbox(T("Loại tài khoản"), [TC] + sorted(df["Loại tài khoản"].unique()),
                        format_func=lambda x: x if x == TC else T_tk(x))
    f_loi = st.selectbox(T("Mã lỗi (PF)"),
                         [TC] + sorted({x for lst in df["_pf"] for x in lst}),
                         format_func=lambda x: x if x == TC else pf_nhan(x),
                         help=T("Chọn 1 mã để chỉ xem lượt có mã đó"))

    ngay_co = sorted(x for x in df["Ngày chạy"].dropna().unique())
    if ngay_co:
        lo, hi = ngay_co[0], ngay_co[-1]
        sel = st.date_input(T("Khoảng thời gian"), (lo, hi), min_value=lo, max_value=hi)
        if isinstance(sel, (list, tuple)):
            f_ngay = (sel[0], sel[-1] if len(sel) > 1 else sel[0])
        else:
            f_ngay = (sel, sel)
    else:
        f_ngay = None

f = df
if f_moc != TC:
    f = f[f["Mốc"] == f_moc]
if f_nt != TC:
    f = f[f["Nền tảng"] == f_nt]
if f_nhom != TC:
    f = f[f["Nhóm prompt"] == f_nhom]
if f_tk != TC:
    f = f[f["Loại tài khoản"] == f_tk]
if f_ngay:
    f = f[f["Ngày chạy"].notna() & f["Ngày chạy"].between(f_ngay[0], f_ngay[1])]
if f_loi != TC:
    f = f[f["_pf"].apply(lambda p: f_loi in p)]

st.title(T("GEO PalFish VN — Báo cáo giám sát thông tin thương hiệu trên nền tảng AI"))
_sheet_url = f"https://docs.google.com/spreadsheets/d/{sid}/edit"
st.markdown(T("📄 [Mở Google Sheet nguồn]({u}) · [tab 4a — Nhật ký lượt chạy]({u4}) · "
              "[tab 3 — Issue tracker]({u3})").format(
    u=_sheet_url, u4=f"{_sheet_url}#gid={SHEET_GID_MAC_DINH}",
    u3=f"{_sheet_url}#gid={SHEET_GID_ISSUE}"))

_INTRO_VI = (
    "**Dashboard này làm gì**  \n"
    "Theo dõi cách các nền tảng AI (ChatGPT, Gemini, AI Google, Perplexity) trả lời "
    "khi người dùng hỏi về PalFish Việt Nam.\n\n"
    "**Cách chấm**  \n"
    "Mỗi đợt đánh giá: hỏi 4 nền tảng **20 câu hỏi cố định** (xem “Chú giải” bên dưới), "
    "mỗi câu vài lần. Đối chiếu từng câu trả lời với **bộ thông tin thương hiệu PalFish đã "
    "được duyệt** rồi chấm: Đúng / Đúng một phần / Sai / Không có thông tin.\n\n"
    "**Hiểu các con số**\n"
    "- **Lượt kiểm tra** = 1 lần hỏi 1 câu trên 1 nền tảng.\n"
    "- **Ý lỗi** = 1 điểm sai cụ thể trong câu trả lời. Một lượt có thể dính nhiều ý lỗi "
    "→ tổng ý lỗi thường lớn hơn số câu sai.\n"
    "- **Mã lỗi PF‑xxx** = một loại lỗi đã được đặt tên (PF = *PalFish*). Tên + mô tả ở "
    "tab **Danh mục lỗi**.\n"
    "- **Mức P0 / P1 / P2**: P0 = nghiêm trọng, cần sửa gấp · P1 = quan trọng · "
    "P2 = tối ưu dài hạn.\n\n"
    "**Ai xử lý lỗi** (tab *Trạng thái xử lý lỗi*)\n"
    "- **Mai** — sửa nội dung, cập nhật kênh chính thống.\n"
    "- **IT‑Minh** — sửa kỹ thuật website (redirect, schema, tên miền).\n"
    "- **Josh** — duyệt thông điệp & xử lý vấn đề lớn (nguồn gốc thương hiệu, pháp nhân).\n\n"
    "**Đợt đánh giá (“mốc”)**: mỗi lần đo là một mốc. Hiện mới có mốc đầu (*Baseline*); "
    "biểu đồ xu hướng sẽ hiện khi có mốc thứ 2."
)
with st.expander(T("ℹ️ Giới thiệu & cách đọc dashboard")):
    st.markdown(_INTRO_VI if LANG == "vi" else i18n.UI["INTRO_BODY"][LANG])

if f.empty:
    st.warning(T("Không có dòng nào khớp bộ lọc."))
    st.stop()

k = tinh_kpi(f)
m_dung = f["Độ chính xác"] == "Đúng"
m_mot = f["Độ chính xác"] == "Đúng một phần"
m_sai = f["Độ chính xác"] == "Sai"


def _y(mask):
    return int(f.loc[mask, "Số lỗi"].sum())


cols = st.columns(5)
cols[0].metric(T("Tổng lượt kiểm tra"), len(f))
cols[1].metric(T("Trả lời chính xác"), int(m_dung.sum()))
cols[1].caption(T("↳ {n} ý lỗi trong nhóm").format(n=_y(m_dung)))
cols[2].metric(T("Chính xác một phần"), int(m_mot.sum()))
cols[2].caption(T("↳ {n} ý lỗi trong nhóm").format(n=_y(m_mot)))
cols[3].metric(T("Trả lời sai"), int(m_sai.sum()))
cols[3].caption(T("↳ {n} ý lỗi trong nhóm").format(n=_y(m_sai)))
cols[4].metric(T("Tổng số lỗi ghi nhận"), k["tong_loi"])
cols[4].caption(T("↳ = tổng 3 ô bên trái"))

with st.expander(T("📋 Chú giải: 20 câu hỏi prompt & 9 nhóm")):
    _rows_ch = [{T("Nhóm"): T_nhom(_nh), T("Mã"): _q, T("Câu hỏi"): cau_hoi(_q)}
                for _nh in NHOM_ORDER
                for _q in sorted(m for m, g in NHOM_PROMPT.items() if g == _nh)]
    st.dataframe(pd.DataFrame(_rows_ch), use_container_width=True, hide_index=True,
                 column_config={T("Câu hỏi"): st.column_config.TextColumn(width="large")})
    st.caption(T("20 câu hỏi cố định (nguyên văn — không đổi giữa các mốc). "
                 "Nguồn: tab “20 Prompt” trong Google Sheet."))

tab_tq, tab_pr, tab_nt, tab_pf, tab_ng, tab_tt, tab_ct, tab_bc = st.tabs(
    [T("Tổng quan"), T("Phân tích theo câu hỏi"), T("Phân tích theo nền tảng"),
     T("Danh mục lỗi"), T("Nguồn trích dẫn"), T("Trạng thái xử lý lỗi"),
     T("Dữ liệu chi tiết"), T("Báo cáo định kỳ")]
)

_NHOM_ORDER_T = [T_nhom(g) for g in NHOM_ORDER]

with tab_tq:
    _RGB_CX = {"Đúng": (46, 125, 50), "Đúng một phần": (249, 168, 37), "Sai": (198, 40, 40),
               "Không có thông tin": (144, 164, 174), "Chưa chấm được": (207, 216, 220)}

    def _bang_dcx(group_col, order=None, nhom=False):
        _b = pd.Categorical(f["Độ chính xác"], BAC_CX, ordered=True)
        cnt = (f.assign(_b=_b).groupby([group_col, "_b"], observed=False)
               .size().unstack(fill_value=0))
        cnt = cnt.reindex(order, fill_value=0) if order else cnt
        cnt = cnt[BAC_CX]
        cnt["Tổng"] = cnt.sum(axis=1)
        _t = cnt.sum(axis=0)
        _t.name = "TỔNG CỘNG"
        cnt = pd.concat([cnt, _t.to_frame().T])
        pct = cnt[BAC_CX].div(cnt["Tổng"].replace(0, 1), axis=0)
        disp = cnt.astype(object)
        for _c in BAC_CX:
            disp[_c] = (cnt[_c].astype(int).astype(str) + " ("
                        + (pct[_c] * 100).round().astype(int).astype(str) + "%)")
        disp["% Đúng"] = (pct["Đúng"] * 100).round().astype(int).astype(str) + "%"

        S = pd.DataFrame("", index=disp.index, columns=disp.columns)
        for _c in BAC_CX:
            r, gg, b = _RGB_CX[_c]
            for ix in disp.index:
                a = 0.10 + 0.90 * float(pct.loc[ix, _c])
                S.loc[ix, _c] = f"background-color: rgba({r},{gg},{b},{a:.2f})"
        S.loc["TỔNG CỘNG"] = S.loc["TỔNG CỘNG"].str.rstrip(";") + "; font-weight:700"

        cmap = {b: T_cx(b) for b in BAC_CX}
        cmap["Tổng"] = T("Tổng")
        cmap["% Đúng"] = T("% Đúng")
        imap = {ix: (T_nhom(ix) if nhom else ix) for ix in disp.index}
        imap["TỔNG CỘNG"] = T("TỔNG CỘNG")
        disp = disp.rename(columns=cmap, index=imap)
        S = S.rename(columns=cmap, index=imap)
        return disp.style.apply(lambda _: S, axis=None)

    c1, c2 = st.columns([7, 3])
    with c1:
        st.subheader(T("Độ chính xác theo nhóm câu hỏi"))
        st.dataframe(_bang_dcx("Nhóm prompt", NHOM_ORDER, nhom=True), use_container_width=True)
        st.caption(T("Mỗi ô: số câu (tỷ lệ trong nhóm). Màu càng đậm = tỷ lệ ở mức đó càng cao."))
    with c2:
        st.subheader(T("Tỷ lệ tổng"))
        dd = (f["Độ chính xác"].value_counts().reindex(BAC_CX, fill_value=0)
              .rename_axis("Độ chính xác").reset_index(name="Số câu"))
        _tot = int(dd["Số câu"].sum()) or 1
        dd["_o"] = dd["Độ chính xác"].map({b: i for i, b in enumerate(BAC_CX)})
        dd["nhãn"] = (dd["Số câu"].astype(str) + " ("
                      + (dd["Số câu"] / _tot * 100).round().astype(int).astype(str) + "%)")
        dd["Độ chính xác"] = dd["Độ chính xác"].map(T_cx)
        _cxdom = [T_cx(b) for b in BAC_CX]
        base = alt.Chart(dd).encode(
            theta=alt.Theta("Số câu:Q", stack=True),
            order=alt.Order("_o:Q"),
            color=alt.Color("Độ chính xác:N", sort=_cxdom, title=None,
                            legend=alt.Legend(orient="bottom", columns=1, title=None,
                                              labelLimit=240, symbolSize=120, labelFontSize=12),
                            scale=alt.Scale(domain=_cxdom, range=MAU_CX)),
        )
        arc = base.mark_arc(innerRadius=48, outerRadius=95)
        lab = (base.transform_filter("datum['Số câu'] > 0")
               .mark_text(radius=114, fontSize=11).encode(text="nhãn:N"))
        st.altair_chart((arc + lab).properties(height=300, width="container"),
                        use_container_width=True)

    st.subheader(T("Độ chính xác theo nền tảng AI tìm kiếm"))
    st.dataframe(_bang_dcx("Nền tảng", sorted(f["Nền tảng"].unique())), use_container_width=True)
    st.metric(T("Lẫn thông tin nước ngoài / lỗi thời"),
              T("{p} lượt").format(p=f"{(f['Trộn nước ngoài'] != 'Không').mean():.0%}"))

    if f["Mốc"].nunique() > 1:
        st.subheader(T("Xu hướng qua các mốc đánh giá"))
        _CHISO = {"xuat_hien": T("Tỷ lệ xuất hiện"), "chinh_xac": T("Đúng hoàn toàn"),
                  "palfish": T("Trích palfish.vn"), "kenh": T("Có kênh chính thống")}
        tr = (f.groupby("Mốc").apply(lambda g: pd.Series(tinh_kpi(g))).reset_index()
              .melt("Mốc", ["xuat_hien", "chinh_xac", "palfish", "kenh"], "Chỉ số", "Giá trị"))
        tr["Mốc"] = tr["Mốc"].map(T_moc)
        tr["Chỉ số"] = tr["Chỉ số"].map(_CHISO)
        st.altair_chart(alt.Chart(tr).mark_line(point=True).encode(
            x="Mốc:N", y=alt.Y("Giá trị:Q", axis=alt.Axis(format="%")),
            color="Chỉ số:N",
            tooltip=["Mốc:N", "Chỉ số:N", alt.Tooltip("Giá trị:Q", format=".0%")],
        ).properties(height=300), use_container_width=True)
    else:
        st.info(T("Chỉ mới có 1 mốc — biểu đồ xu hướng sẽ hiện khi có mốc Cuối T1 / Cuối T2."))

with tab_pr:
    st.caption(T("Cùng 9 nhóm câu hỏi như bảng “Độ chính xác theo nhóm câu hỏi” ở tab Tổng quan, "
                 "sắp xếp theo đúng thứ tự đó."))
    st.subheader(T("Tỷ lệ độ chính xác theo nhóm câu hỏi"))
    st.altair_chart(_bd_ty_le_cx(f, "Nhóm prompt", _NHOM_ORDER_T, lab=T_nhom),
                    use_container_width=True)
    st.caption(T("Thanh càng nhiều vàng/đỏ → nhóm câu hỏi đó AI trả lời càng kém."))

    st.subheader(T("Số ý lỗi theo nhóm câu hỏi (tách theo mức ưu tiên)"))
    st.altair_chart(_bd_so_loi_muc(f, "Nhóm prompt", _NHOM_ORDER_T, lab=T_nhom),
                    use_container_width=True)
    st.caption(T("Thanh dài = nhóm tích tụ nhiều lỗi; phần đỏ là lỗi P0 (nghiêm trọng)."))

    st.subheader(T("Nhóm câu hỏi dính những mã lỗi nào"))
    st.altair_chart(_bd_pf_theo_nhom(f, "Nhóm prompt", _NHOM_ORDER_T, lab=T_nhom),
                    use_container_width=True)

with tab_nt:
    st.caption(T("Cùng các nền tảng như bảng “Độ chính xác theo nền tảng AI tìm kiếm” ở tab Tổng quan."))
    plat_order = sorted(f["Nền tảng"].unique())

    st.subheader(T("Tỷ lệ độ chính xác theo nền tảng"))
    st.altair_chart(_bd_ty_le_cx(f, "Nền tảng", plat_order), use_container_width=True)

    st.subheader(T("Số ý lỗi theo nền tảng (tách theo mức ưu tiên)"))
    st.altair_chart(_bd_so_loi_muc(f, "Nền tảng", plat_order), use_container_width=True)

    st.subheader(T("Nền tảng nào dính những mã lỗi nào"))
    st.altair_chart(_bd_pf_theo_nhom(f, "Nền tảng", plat_order), use_container_width=True)
    st.caption(T("Hành vi trích dẫn nguồn của từng nền tảng: xem tab Nguồn trích dẫn."))

with tab_pf:
    st.subheader(T("Danh mục & tần suất mã lỗi"))
    bpf = bang_pf(f)
    if bpf.empty:
        st.info(T("Không có mã PF nào trong phạm vi lọc."))
    else:
        bpf_c = bpf.assign(**{"_ml": bpf["Mã"].map(pf_nhan)})
        st.altair_chart(alt.Chart(bpf_c).mark_bar().encode(
            x=alt.X("Số lượt:Q", title=T("Số lượt")),
            y=alt.Y("_ml:N", sort="-x", title=None),
            color=alt.Color("Mức:N",
                            scale=alt.Scale(domain=list(MAU_MUC), range=list(MAU_MUC.values()))),
            tooltip=[alt.Tooltip("Mã:N", title=T("Mã")),
                     alt.Tooltip("Tên lỗi:N", title=T("Tên lỗi")),
                     alt.Tooltip("Mô tả:N", title=T("Mô tả")), "Mức:N",
                     alt.Tooltip("Số lượt:Q", title=T("Số lượt")),
                     alt.Tooltip("Nền tảng dính:N", title=T("Nền tảng dính")),
                     alt.Tooltip("Prompt:N", title=T("Prompt"))],
        ).properties(height=max(200, 26 * len(bpf))), use_container_width=True)
        st.caption(T("Bảng dưới: giải thích từng mã lỗi là gì."))
        _cc = {"Mã": T("Mã"), "Tên lỗi": T("Tên lỗi"), "Mô tả": T("Mô tả"), "Mức": T("Mức"),
               "Số lượt": T("Số lượt"), "Nền tảng dính": T("Nền tảng dính"), "Prompt": T("Prompt")}
        st.dataframe(bpf.rename(columns=_cc), use_container_width=True, hide_index=True,
                     column_config={T("Mô tả"): st.column_config.TextColumn(width="large")})

    st.divider()
    st.subheader(T("Phân bố lỗi"))
    daca = f[f["Độ chính xác"].isin(["Đúng", "Đúng một phần", "Sai", "Không có thông tin"])]
    if daca.empty:
        st.info(T("Chưa có lượt nào được chấm trong phạm vi lọc."))
    else:
        st.caption(T("Số lỗi trên mỗi lượt trả lời (bao nhiêu lượt có 0 lỗi, 1 lỗi, 2 lỗi…)"))
        dist = (daca["Số lỗi"].fillna(0).astype(int).value_counts().sort_index()
                .rename_axis("k").reset_index(name="v"))
        st.altair_chart(alt.Chart(dist).mark_bar().encode(
            x=alt.X("k:O", title=T("Số lỗi / lượt")),
            y=alt.Y("v:Q", title=T("Số lượt")),
            tooltip=[alt.Tooltip("k:O", title=T("Số lỗi / lượt")),
                     alt.Tooltip("v:Q", title=T("Số lượt"))],
        ).properties(height=300), use_container_width=True)

with tab_ng:
    st.caption(T("Những nguồn AI dựa vào khi trả lời. **“Nguồn phát sinh thông tin sai”** = nơi AI "
                 "học thông tin không đúng (Baidu, trang review nước ngoài, tin crypto…) — xử lý "
                 "hoặc tạo nguồn chính thống đối trọng sẽ giảm lỗi."))
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(T("Tên miền AI thường trích dẫn"))
        dom = pd.Series([x for t in f["Nguồn AI trích dẫn"] for x in tach_domain(t)])
        if dom.empty:
            st.info(T("Cột 'Nguồn AI trích dẫn' đang trống."))
        else:
            vc = dom.value_counts().head(15).rename_axis("d").reset_index(name="v")
            st.altair_chart(alt.Chart(vc).mark_bar().encode(
                x=alt.X("v:Q", title=T("Số lượt")),
                y=alt.Y("d:N", sort="-x", title=None),
                tooltip=[alt.Tooltip("d:N", title=T("Tên miền")),
                         alt.Tooltip("v:Q", title=T("Số lượt"))],
            ).properties(height=max(200, 24 * len(vc))), use_container_width=True)
    with c2:
        st.subheader(T("Nguồn phát sinh thông tin sai"))
        bad = pd.Series([x for t in f["Nguồn thông tin sai"]
                         for x in re.split(r"[;,]", t) if x.strip()]).str.strip()
        bad = bad[bad.ne("")].apply(lambda s: s.split("/")[0].split()[0] if s else s)
        if bad.empty:
            st.info(T("Cột 'Nguồn thông tin sai' đang trống."))
        else:
            vc = bad.value_counts().head(15).rename_axis("d").reset_index(name="v")
            st.altair_chart(alt.Chart(vc).mark_bar(color="#C62828").encode(
                x=alt.X("v:Q", title=T("Số lượt")),
                y=alt.Y("d:N", sort="-x", title=None),
                tooltip=[alt.Tooltip("d:N", title=T("Nguồn")),
                         alt.Tooltip("v:Q", title=T("Số lượt"))],
            ).properties(height=max(200, 24 * len(vc))), use_container_width=True)

    st.subheader(T("Hành vi trích dẫn nguồn theo nền tảng"))
    gnt = f.groupby("Nền tảng").agg(**{
        "sl": ("Prompt ID", "size"),
        "pf": ("Trích palfish.vn", "mean"),
        "kc": ("Kênh chính thống khác", "mean"),
    })
    gnt["nn"] = (f.assign(_x=f["Trộn nước ngoài"].ne("Không"))
                 .groupby("Nền tảng")["_x"].mean())
    for c in ["pf", "kc", "nn"]:
        gnt[c] = (gnt[c] * 100).round().astype(int).astype(str) + "%"
    gnt = gnt.reset_index().rename(columns={
        "Nền tảng": T("Nền tảng"), "sl": T("Số lượt"), "pf": T("Trích palfish.vn"),
        "kc": T("Có kênh chính thống"), "nn": T("Lẫn TT nước ngoài")})
    st.dataframe(gnt, use_container_width=True, hide_index=True)

with tab_tt:
    st.caption(T("Tình trạng xử lý từng lỗi. Người phụ trách: **Mai** = nội dung · "
                 "**IT‑Minh** = kỹ thuật website · **Josh** = duyệt / vấn đề lớn. "
                 "Lỗi đóng khi test lại 3 lần, hết ở ≥ 2/3 lần. "
                 "(Bộ lọc bên trái không áp dụng ở tab này.)"))
    if issue.empty:
        st.info(T("Chưa đọc được tab “3 Issue tracker” (kiểm tra Sheet đã bật quyền xem, "
                  "hoặc bạn đang trỏ tới một Sheet khác)."))
    else:
        _mo = issue[issue["Trạng thái"] != "Đã đóng"]
        _dong = issue[issue["Trạng thái"] == "Đã đóng"]
        _p0mo = _mo[_mo["Mức"] == "P0"]
        mc = st.columns(4)
        mc[0].metric(T("Tổng lỗi ghi nhận"), len(issue))
        mc[1].metric(T("Đang mở"), len(_mo))
        mc[2].metric(T("P0 đang mở"), len(_p0mo))
        mc[3].metric(T("Đã đóng"), len(_dong))

        _MUC_BG = {"P0": "rgba(198,40,40,.18)", "P1": "rgba(249,168,37,.16)",
                   "P2": "rgba(144,164,174,.14)"}

        def _to_muc(colv):
            return [f"background-color: {_MUC_BG.get(v, '')}" for v in colv]

        _CC_TT = {"Mã": T("Mã"), "Loại": T("Loại"), "Mức": T("Mức"), "Mô tả": T("Mô tả"),
                  "Thông tin đúng": T("Thông tin đúng"), "Người phụ trách": T("Người phụ trách"),
                  "Trạng thái": T("Trạng thái"), "Ngày sửa xong": T("Ngày sửa xong"),
                  "Ngày test lại": T("Ngày test lại"), "Ngày đóng": T("Ngày đóng"),
                  "Kết quả test lại": T("Kết quả test lại")}

        st.subheader(T("Lỗi đang mở"))
        if _mo.empty:
            st.success(T("Không còn lỗi nào đang mở 🎉"))
        else:
            mm = _mo.assign(_o=_mo["Mức"].map({"P0": 0, "P1": 1, "P2": 2}).fillna(9),
                            _t=_mo["Trạng thái"].map({s: i for i, s in enumerate(TT_ORDER)}).fillna(0))
            mm = mm.sort_values(["_o", "_t", "Mã"])
            mm = mm.assign(**{"Trạng thái": mm["Trạng thái"].map(T_tt),
                              "Người phụ trách": mm["Người phụ trách"].map(T_tk)})
            show_c = ["Mã", "Loại", "Mức", "Mô tả", "Thông tin đúng",
                      "Người phụ trách", "Trạng thái", "Ngày sửa xong", "Ngày test lại"]
            _tbl = mm[show_c].rename(columns=_CC_TT)
            st.dataframe(_tbl.style.apply(_to_muc, subset=[T("Mức")]),
                         use_container_width=True, hide_index=True,
                         column_config={T("Mô tả"): st.column_config.TextColumn(width="large"),
                                        T("Thông tin đúng"): st.column_config.TextColumn(width="medium")})

        st.subheader(T("Việc đang mở theo người phụ trách"))
        if _mo.empty:
            st.caption("—")
        else:
            byo = (_mo.assign(P0=(_mo["Mức"] == "P0").astype(int),
                              P1=(_mo["Mức"] == "P1").astype(int),
                              P2=(_mo["Mức"] == "P2").astype(int))
                   .groupby("Người phụ trách")
                   .agg(**{"sl": ("Mã", "size"), "P0": ("P0", "sum"),
                           "P1": ("P1", "sum"), "P2": ("P2", "sum")})
                   .reset_index().sort_values("sl", ascending=False))
            byo["Người phụ trách"] = byo["Người phụ trách"].map(T_tk)
            byo = byo.rename(columns={"Người phụ trách": T("Người phụ trách"), "sl": T("Số lỗi")})
            st.dataframe(byo, use_container_width=True, hide_index=True)

        st.subheader(T("Lỗi đã đóng"))
        if _dong.empty:
            st.caption(T("Chưa có lỗi nào được đóng."))
        else:
            _dd = _dong[["Mã", "Loại", "Mức", "Người phụ trách", "Ngày đóng", "Kết quả test lại"]].copy()
            _dd["Người phụ trách"] = _dd["Người phụ trách"].map(T_tk)
            st.dataframe(_dd.rename(columns=_CC_TT), use_container_width=True, hide_index=True)

with tab_ct:
    st.subheader(T("Toàn bộ lượt kiểm tra"))
    show = ["Ngày chạy", "Mốc", "Nền tảng", "Loại tài khoản", "Prompt ID", "Nhóm prompt",
            "Xuất hiện", "Vị trí đề cập", "Độ chính xác", "Số lỗi", "Loại lỗi",
            "Trộn nước ngoài", "Trích palfish.vn", "Nguồn thông tin sai"]
    _tbl = f[show].copy()
    _tbl["Mốc"] = _tbl["Mốc"].map(T_moc)
    _tbl["Loại tài khoản"] = _tbl["Loại tài khoản"].map(T_tk)
    _tbl["Nhóm prompt"] = _tbl["Nhóm prompt"].map(T_nhom)
    _tbl["Độ chính xác"] = _tbl["Độ chính xác"].map(T_cx)
    _tbl["Trộn nước ngoài"] = _tbl["Trộn nước ngoài"].map(T_tron)
    _CC_CT = {"Ngày chạy": T("Ngày chạy"), "Mốc": T("Mốc"), "Nền tảng": T("Nền tảng"),
              "Loại tài khoản": T("Loại tài khoản"), "Prompt ID": T("Prompt ID"),
              "Nhóm prompt": T("Nhóm prompt"), "Xuất hiện": T("Xuất hiện"),
              "Vị trí đề cập": T("Vị trí đề cập"), "Độ chính xác": T("Độ chính xác"),
              "Số lỗi": T("Số lỗi"), "Loại lỗi": T("Loại lỗi"),
              "Trộn nước ngoài": T("Trộn nước ngoài"), "Trích palfish.vn": T("Trích palfish.vn"),
              "Nguồn thông tin sai": T("Nguồn thông tin sai")}
    st.dataframe(_tbl.rename(columns=_CC_CT), use_container_width=True, hide_index=True)

    st.subheader(T("Xem chi tiết một lượt"))
    nhan = f.apply(lambda r: f"{r['Nền tảng']} · {r['Prompt ID']} · {T_cx(r['Độ chính xác'])}",
                   axis=1)
    idx = st.selectbox(T("Chọn lượt kiểm tra"), options=list(f.index),
                       format_func=lambda i: nhan[i])
    r = f.loc[idx]
    st.markdown(f"**{r['Nền tảng']} — {r['Prompt ID']}** · {T_nhom(r['Nhóm prompt'])} · "
                f"{T('độ chính xác')}: **{T_cx(r['Độ chính xác'])}** · "
                f"{T('số lỗi')}: **{int(r['Số lỗi'])}**")
    if r["_pf"]:
        st.markdown("\n".join(f"- **{pf_nhan(x)}** — {pf_mota(x)}" for x in r["_pf"]))
    if r["Đoạn có vấn đề"]:
        st.error(T("**Nội dung có vấn đề:** {v}").format(v=r["Đoạn có vấn đề"]))
    if r["Nguồn thông tin sai"]:
        st.write(T("**Nguồn phát sinh thông tin sai:** {v}").format(v=r["Nguồn thông tin sai"]))
    if r["Ghi chú"]:
        st.info(T("**Ghi chú:** {v}").format(v=r["Ghi chú"]))
    with st.expander(T("Nội dung trả lời của AI")):
        st.write(r["Câu trả lời"])
    with st.expander(T("Nguồn AI trích dẫn")):
        st.write(r["Nguồn AI trích dẫn"] or T("(trống)"))
    if r["Link bằng chứng"]:
        st.write(T("[Ảnh chụp / hội thoại minh chứng]({u})").format(u=r["Link bằng chứng"]))

with tab_bc:
    st.subheader(T("Bản tổng hợp định kỳ (tự động tạo)"))
    _bc_ngays = sorted(x for x in df["Ngày chạy"].dropna().unique())
    bc1, bc2 = st.columns([1, 2])
    _opts = [T("Toàn bộ (mọi ngày)"), T("Chọn ngày / khoảng ngày")]
    bc_che_do = bc1.radio("bc", _opts, label_visibility="collapsed")
    dfr = df
    if bc_che_do == _opts[1] and _bc_ngays:
        _lo, _hi = _bc_ngays[0], _bc_ngays[-1]
        _sel = bc2.date_input(T("Khoảng ngày"), (_lo, _hi), min_value=_lo, max_value=_hi,
                              help=T("Chọn cùng 1 ngày cho cả 2 ô để lấy đúng ngày đó."))
        if isinstance(_sel, (list, tuple)):
            _a, _b = _sel[0], _sel[-1]
        else:
            _a = _b = _sel
        dfr = df[df["Ngày chạy"].notna() & df["Ngày chạy"].between(_a, _b)]

    st.caption(T("Không theo bộ lọc bên trái. Phần Issue tracker luôn là trạng thái hiện tại. "
                 "Copy / tải về, thêm phần “Việc cần làm” rồi gửi. Công cụ không tự lưu / gửi."))
    if dfr.empty:
        st.warning(T("Không có lượt kiểm tra nào trong khoảng ngày đã chọn."))
    else:
        txt = bao_cao_tuan(dfr, tinh_kpi(dfr), issue)
        st.download_button(T("Tải bản .md"), data=txt.encode("utf-8"),
                           file_name=f"bao-cao-GEO-{dt.date.today():%Y%m%d}.md",
                           mime="text/markdown")
        st.markdown("<style>div[data-testid='stMarkdownContainer'] h4"
                    "{font-size:1.05rem;margin:.3rem 0}</style>", unsafe_allow_html=True)
        st.markdown(txt)
        with st.expander(T("Xem dạng văn bản thô (để copy sang email / chat)")):
            st.code(txt, language="markdown")

