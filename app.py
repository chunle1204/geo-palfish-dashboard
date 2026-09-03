"""
GEO PalFish VN — Dashboard theo dõi kiểm tra AI
================================================
Đọc TRỰC TIẾP tab "4a Nhat ky luot chay" từ Google Sheet.
Sheet đổi -> dashboard tự cập nhật (cache 2 phút + nút làm mới + tự refresh).

Chạy:
    pip install -r requirements.txt
    streamlit run app.py

YÊU CẦU: Google Sheet phải cho xem công khai:
    Chia sẻ -> "Bất kỳ ai có đường liên kết" -> Người xem
(không cần cho chỉnh sửa; dashboard chỉ đọc)
"""

from __future__ import annotations

import datetime as dt
import io
import re
from urllib.request import Request, urlopen

import altair as alt
import pandas as pd
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:  # thư viện phụ, không có cũng chạy được
    st_autorefresh = None

# ------------------------------------------------------------------ cấu hình
SHEET_ID_MAC_DINH = "172WzrO47njz-fMmi035PcmmVBTcaR2PIXg_GeaDBbNY"
SHEET_GID_MAC_DINH = "1347201081"          # tab "4a Nhat ky luot chay"
SHEET_TEN = "4a Nhat ky luot chay"
TTL = 120                                  # giây — hết hạn thì tải lại sheet

# Mức ưu tiên từng mã lỗi (KHÔNG có trong sheet 4a -> khai ở đây).
# Nguồn: bản chấm baseline + tab "3 Issue tracker".
PF_MUC = {
    "PF-001": "P0", "PF-002": "P1", "PF-003": "P1", "PF-004": "P1",
    "PF-005": "P1", "PF-006": "P1", "PF-007": "P0", "PF-008": "P1",
    "PF-009": "P1", "PF-010": "P1", "PF-011": "P0", "PF-012": "P0",
    "PF-013": "P0", "PF-014": "P1", "PF-015": "P1", "PF-016": "P2",
    "PF-017": "P2", "PF-018": "P1", "PF-019": "P1", "PF-020": "P1",
    "PF-021": "P2", "PF-022": "P1", "PF-023": "P1",
}
# Tên gọi ngắn cho từng mã lỗi (hiện kèm mã ở chú thích biểu đồ / bộ lọc).
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
# Diễn giải một dòng — dùng cho bảng "Danh mục lỗi".
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


def pf_nhan(ma: str) -> str:
    """PF-011 -> 'PF-011 (Nguồn gốc)'."""
    ten = PF_TEN.get(ma)
    return f"{ma} ({ten})" if ten else ma
# 9 nhóm chi tiết theo Prompt ID (mịn hơn 4 nhóm gốc)
NHOM_PROMPT = {
    **{f"P{n:02d}": "Pháp nhân & nhận diện" for n in range(1, 5)},
    "P05": "Địa chỉ văn phòng", "P06": "Địa chỉ văn phòng",
    "P07": "Liên hệ & đăng ký học thử", "P08": "Liên hệ & đăng ký học thử",
    "P09": "Độ tuổi & hình thức học", "P10": "Độ tuổi & hình thức học",
    "P11": "Giáo viên",
    "P12": "Giáo trình & khóa học", "P14": "Giáo trình & khóa học",
    "P13": "Học phí",
    "P15": "Uy tín & đánh giá phụ huynh", "P16": "Uy tín & đánh giá phụ huynh",
    **{f"P{n:02d}": "So sánh & quy mô & báo chí" for n in range(17, 21)},
}
NHOM_ORDER = ["Pháp nhân & nhận diện", "Địa chỉ văn phòng", "Liên hệ & đăng ký học thử",
              "Độ tuổi & hình thức học", "Giáo viên", "Giáo trình & khóa học", "Học phí",
              "Uy tín & đánh giá phụ huynh", "So sánh & quy mô & báo chí"]
MOC_ORDER = ["Baseline", "Cuối T1", "Cuối T2", "Test lại"]
BAC_CX = ["Đúng", "Đúng một phần", "Sai", "Không có thông tin", "Chưa chấm được"]
MAU_CX = ["#2E7D32", "#F9A825", "#C62828", "#90A4AE", "#CFD8DC"]
MAU_MUC = {"P0": "#C62828", "P1": "#F9A825", "P2": "#90A4AE"}
DOMAIN_RE = re.compile(r"(?:https?://)?(?:www\.)?([a-z0-9][a-z0-9\-.]+\.[a-z]{2,})", re.I)

# Icon con cá lấy từ favicon chính thức của palfish.vn (rel="icon").
PALFISH_ICON = "https://palfish.vn/wp-content/uploads/2022/07/Group-1-1.svg"
st.set_page_config(page_title="GEO PalFish · Báo cáo giám sát AI",
                   page_icon=PALFISH_ICON, layout="wide")


# ------------------------------------------------------------------ tải & chuẩn hoá
def tach_id_gid(text: str) -> tuple[str, str | None]:
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", text or "")
    sid = m.group(1) if m else (text or "").strip()
    g = re.search(r"[#&?]gid=(\d+)", text or "")
    return sid, (g.group(1) if g else None)


@st.cache_data(ttl=TTL, show_spinner="Đang tải dữ liệu từ Google Sheet…")
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
                loi = ("Google trả về trang HTML (đăng nhập) thay vì dữ liệu.\n"
                       "-> Mở Sheet -> Chia sẻ -> 'Bất kỳ ai có đường liên kết' -> Người xem.")
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
    o["Prompt ID"] = g(col(df, "prompt id") or col(df, "prompt")).str.upper()
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
    # Câu "Đúng" -> KHÔNG tính lỗi (mã PF trên câu Đúng chỉ là ghi chú, không đếm)
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
    mask = o["Prompt ID"].str.match(r"^P\d\d$") & o["Câu trả lời"].str.len().gt(0)
    return o[mask].reset_index(drop=True)


# ------------------------------------------------------------------ tính toán
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
        rows.append({
            "Mã": ma,
            "Tên lỗi": PF_TEN.get(ma, ""),
            "Mô tả": PF_MOTA.get(ma, ""),
            "Mức": PF_MUC.get(ma, "?"),
            "Số lượt": len(grp),
            "Nền tảng dính": ", ".join(sorted(grp["Nền tảng"].unique())),
            "Prompt": ", ".join(sorted(grp["Prompt ID"].unique())),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["Mức", "Số lượt"], ascending=[True, False]).reset_index(drop=True)


# Trục Y dùng chung cho mọi biểu đồ phân tích: hiện ĐỦ nhãn, không cắt chữ.
def _y_nhom(group_col: str, order: list[str]):
    return alt.Y(f"{group_col}:N", sort=order,
                 scale=alt.Scale(domain=order, paddingInner=0.3, paddingOuter=0.15),
                 axis=alt.Axis(labelOverlap=False, labelLimit=260, title=None,
                               labelFontSize=12, labelPadding=6))


def _cao(n: int) -> int:
    return max(280, 58 * n)


def _bd_ty_le_cx(fr: pd.DataFrame, group_col: str, order: list[str]):
    """Thanh xếp chồng 100%: tỷ lệ Đúng / Một phần / Sai theo `group_col` (đủ nhóm)."""
    d = (fr[fr["Độ chính xác"].isin(BAC_CX)]
         .groupby([group_col, "Độ chính xác"], observed=True).size()
         .reset_index(name="Số câu"))
    d["_o"] = d["Độ chính xác"].map({b: i for i, b in enumerate(BAC_CX)})
    return alt.Chart(d).mark_bar().encode(
        x=alt.X("Số câu:Q", stack="normalize", axis=alt.Axis(format="%"), title="Tỷ lệ"),
        y=_y_nhom(group_col, order),
        color=alt.Color("Độ chính xác:N", sort=BAC_CX,
                        scale=alt.Scale(domain=BAC_CX, range=MAU_CX),
                        legend=alt.Legend(orient="bottom", title=None)),
        order=alt.Order("_o:Q"),
        tooltip=[alt.Tooltip(f"{group_col}:N", title="Nhóm"), "Độ chính xác:N", "Số câu:Q"],
    ).properties(height=_cao(len(order)))


def _bd_so_loi_muc(fr: pd.DataFrame, group_col: str, order: list[str]):
    """Thanh xếp chồng: số ý lỗi theo `group_col`, tách theo mức P0/P1/P2 (đủ nhóm)."""
    ex = fr.explode("_pf")
    ex = ex[ex["_pf"].astype(str).str.startswith("PF-")]
    ex = ex.assign(Mức=ex["_pf"].map(PF_MUC).fillna("?"))
    d = ex.groupby([group_col, "Mức"], observed=True).size().reset_index(name="Số ý lỗi")
    return alt.Chart(d).mark_bar().encode(
        x=alt.X("Số ý lỗi:Q"),
        y=_y_nhom(group_col, order),
        color=alt.Color("Mức:N", sort=list(MAU_MUC),
                        scale=alt.Scale(domain=list(MAU_MUC), range=list(MAU_MUC.values())),
                        legend=alt.Legend(orient="bottom", title="Mức ưu tiên")),
        order=alt.Order("Mức:N"),
        tooltip=[alt.Tooltip(f"{group_col}:N", title="Nhóm"), "Mức:N", "Số ý lỗi:Q"],
    ).properties(height=_cao(len(order)))


def _bd_pf_theo_nhom(fr: pd.DataFrame, group_col: str, order: list[str]):
    """Thanh xếp chồng: `group_col` dính những mã PF nào (đếm số lượt, đủ nhóm)."""
    ex = fr.explode("_pf")
    ex = ex[ex["_pf"].astype(str).str.startswith("PF-")]
    d = ex.groupby([group_col, "_pf"], observed=True).size().reset_index(name="Số lượt")
    d["Mã lỗi"] = d["_pf"].map(pf_nhan)
    thu_tu = [pf_nhan(m) for m in sorted(d["_pf"].unique())]
    return alt.Chart(d).mark_bar().encode(
        x=alt.X("Số lượt:Q", title="Số lượt dính"),
        y=_y_nhom(group_col, order),
        color=alt.Color("Mã lỗi:N", sort=thu_tu,
                        legend=alt.Legend(orient="right", columns=1, title="Mã lỗi",
                                          symbolLimit=0)),
        tooltip=[alt.Tooltip(f"{group_col}:N", title="Nhóm"), "Mã lỗi:N", "Số lượt:Q"],
    ).properties(height=_cao(len(order)))


def bao_cao_tuan(fr: pd.DataFrame, k: dict) -> str:
    p0 = sorted({x for p in fr["_pf"] for x in p if PF_MUC.get(x) == "P0"})
    p1 = sorted({x for p in fr["_pf"] for x in p if PF_MUC.get(x) == "P1"})
    return "\n".join([
        f"# Báo cáo giám sát GEO PalFish — {dt.date.today():%d/%m/%Y}",
        "",
        f"Phạm vi: mốc {', '.join(sorted(fr['Mốc'].unique()))} · {k['n']} lượt · "
        f"nền tảng {', '.join(sorted(fr['Nền tảng'].unique()))}",
        "",
        "## Chỉ số",
        f"- Tỷ lệ xuất hiện: {k['xuat_hien']:.0%}",
        f"- Tỷ lệ chính xác (Đúng / đã chấm): {k['chinh_xac']:.0%}",
        f"- Trích palfish.vn: {k['palfish']:.0%}",
        f"- Có ≥1 kênh chính thống: {k['kenh']:.0%}",
        f"- Tổng số lỗi ghi nhận: {k['tong_loi']} · lượt dính P0: {k['p0']}",
        "",
        "## Lỗi theo mức",
        f"- P0: {', '.join(pf_nhan(x) for x in p0) or '—'}",
        f"- P1: {', '.join(pf_nhan(x) for x in p1) or '—'}",
        "",
        "## Lỗi đã đóng (đã test lại đạt)",
        "- …",
        "",
        "## Cần Josh / Jacob quyết",
        "- …",
    ])


# ------------------------------------------------------------------ giao diện
with st.sidebar:
    st.header("Thiết lập & bộ lọc")
    with st.expander("Nguồn dữ liệu"):
        link = st.text_input("Liên kết Google Sheet (để trống dùng mặc định)", value="")
        sid, gid = tach_id_gid(link) if link.strip() else (SHEET_ID_MAC_DINH, SHEET_GID_MAC_DINH)
    c1, c2 = st.columns(2)
    if c1.button("Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    auto = c2.toggle("Tự động cập nhật", value=True, help=f"Tải lại mỗi {TTL // 60} phút")

if st_autorefresh and auto:
    st_autorefresh(interval=TTL * 1000, key="auto")

try:
    raw, tai_luc = tai_4a(sid, gid)
except Exception as e:  # noqa: BLE001
    st.error("**Không đọc được Google Sheet.**")
    st.code(str(e))
    st.stop()

df = chuan_hoa(raw)
if df.empty:
    st.warning("Sheet đọc được nhưng chưa có lượt chạy nào hợp lệ "
               "(cần Prompt ID dạng Pxx và cột 'Câu trả lời đầy đủ' có nội dung).")
    st.stop()

with st.sidebar:
    st.caption(f"Cập nhật lúc {tai_luc:%H:%M:%S %d/%m} · {len(df)} lượt")
    f_moc = st.multiselect("Mốc đánh giá", sorted(df["Mốc"].unique(), key=lambda m: MOC_ORDER.index(m) if m in MOC_ORDER else 9),
                           default=list(df["Mốc"].unique()))
    f_nt = st.multiselect("Nền tảng AI", sorted(df["Nền tảng"].unique()), default=list(df["Nền tảng"].unique()))
    f_nhom = st.multiselect("Nhóm câu hỏi", NHOM_ORDER, default=NHOM_ORDER)
    f_tk = st.multiselect("Loại tài khoản", sorted(df["Loại tài khoản"].unique()),
                          default=list(df["Loại tài khoản"].unique()))

    ngay_co = sorted(x for x in df["Ngày chạy"].dropna().unique())
    if ngay_co:
        lo, hi = ngay_co[0], ngay_co[-1]
        sel = st.date_input("Khoảng thời gian", (lo, hi), min_value=lo, max_value=hi)
        if isinstance(sel, (list, tuple)):
            f_ngay = (sel[0], sel[-1] if len(sel) > 1 else sel[0])
        else:
            f_ngay = (sel, sel)
    else:
        f_ngay = None

    f_loi = st.multiselect("Mã lỗi (PF)", sorted({x for lst in df["_pf"] for x in lst}),
                           format_func=pf_nhan,
                           help="Chọn ≥1 mã để chỉ xem lượt có mã đó")

f = df[df["Mốc"].isin(f_moc) & df["Nền tảng"].isin(f_nt)
       & df["Nhóm prompt"].isin(f_nhom) & df["Loại tài khoản"].isin(f_tk)]
if f_ngay:
    f = f[f["Ngày chạy"].notna() & f["Ngày chạy"].between(f_ngay[0], f_ngay[1])]
if f_loi:
    _sel_loi = set(f_loi)
    f = f[f["_pf"].apply(lambda p: bool(_sel_loi & set(p)))]

st.title("GEO PalFish VN — Báo cáo giám sát thông tin thương hiệu trên nền tảng AI")
if f.empty:
    st.warning("Không có dòng nào khớp bộ lọc.")
    st.stop()

k = tinh_kpi(f)

m_dung = f["Độ chính xác"] == "Đúng"
m_mot = f["Độ chính xác"] == "Đúng một phần"
m_sai = f["Độ chính xác"] == "Sai"


def _y(mask):  # số "ý" lỗi (tổng cột Số lỗi) của nhóm câu — cùng thang với card Tổng số lỗi
    return int(f.loc[mask, "Số lỗi"].sum())


cols = st.columns(5)
cols[0].metric("Tổng lượt kiểm tra", len(f))
cols[1].metric("Trả lời chính xác", int(m_dung.sum()))
cols[1].caption(f"↳ {_y(m_dung)} ý lỗi trong nhóm")
cols[2].metric("Chính xác một phần", int(m_mot.sum()))
cols[2].caption(f"↳ {_y(m_mot)} ý lỗi trong nhóm")
cols[3].metric("Trả lời sai", int(m_sai.sum()))
cols[3].caption(f"↳ {_y(m_sai)} ý lỗi trong nhóm")
cols[4].metric("Tổng số lỗi ghi nhận", k["tong_loi"])
cols[4].caption("↳ = tổng 3 ô bên trái")

tab_tq, tab_pr, tab_nt, tab_pf, tab_ng, tab_ct, tab_bc = st.tabs(
    ["Tổng quan", "Phân tích theo câu hỏi", "Phân tích theo nền tảng", "Danh mục lỗi",
     "Nguồn trích dẫn", "Dữ liệu chi tiết", "Báo cáo định kỳ"]
)

with tab_tq:
    _RGB_CX = {"Đúng": (46, 125, 50), "Đúng một phần": (249, 168, 37), "Sai": (198, 40, 40),
               "Không có thông tin": (144, 164, 174), "Chưa chấm được": (207, 216, 220)}

    def _bang_dcx(group_col, order=None):
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

        def _sty(_):
            s = pd.DataFrame("", index=disp.index, columns=disp.columns)
            for _c in BAC_CX:
                r, gg, b = _RGB_CX[_c]
                for ix in disp.index:
                    a = 0.10 + 0.90 * float(pct.loc[ix, _c])
                    s.loc[ix, _c] = f"background-color: rgba({r},{gg},{b},{a:.2f})"
            s.loc["TỔNG CỘNG"] = s.loc["TỔNG CỘNG"].str.rstrip(";") + "; font-weight:700"
            return s

        return disp.style.apply(_sty, axis=None)

    c1, c2 = st.columns([7, 3])
    with c1:
        st.subheader("Độ chính xác theo nhóm câu hỏi")
        st.dataframe(_bang_dcx("Nhóm prompt", NHOM_ORDER), use_container_width=True)
        st.caption("Mỗi ô: số câu (tỷ lệ trong nhóm). Màu càng đậm = tỷ lệ ở mức đó càng cao.")
    with c2:
        st.subheader("Tỷ lệ tổng")
        dd = (f["Độ chính xác"].value_counts().reindex(BAC_CX, fill_value=0)
              .rename_axis("Độ chính xác").reset_index(name="Số câu"))
        _tot = int(dd["Số câu"].sum()) or 1
        dd["_o"] = dd["Độ chính xác"].map({b: i for i, b in enumerate(BAC_CX)})
        dd["nhãn"] = (dd["Số câu"].astype(str) + " ("
                      + (dd["Số câu"] / _tot * 100).round().astype(int).astype(str) + "%)")
        base = alt.Chart(dd).encode(
            theta=alt.Theta("Số câu:Q", stack=True),
            order=alt.Order("_o:Q"),
            color=alt.Color("Độ chính xác:N", sort=BAC_CX, title=None,
                            legend=alt.Legend(orient="bottom", columns=1, title=None,
                                              labelLimit=240, symbolSize=120, labelFontSize=12),
                            scale=alt.Scale(domain=BAC_CX, range=MAU_CX)),
        )
        arc = base.mark_arc(innerRadius=48, outerRadius=95)
        lab = (base.transform_filter("datum['Số câu'] > 0")
               .mark_text(radius=114, fontSize=11).encode(text="nhãn:N"))
        st.altair_chart((arc + lab).properties(height=300, width="container"),
                        use_container_width=True)

    st.subheader("Độ chính xác theo nền tảng AI tìm kiếm")
    st.dataframe(_bang_dcx("Nền tảng", sorted(f["Nền tảng"].unique())), use_container_width=True)
    st.metric("Lẫn thông tin nước ngoài / lỗi thời",
              f"{(f['Trộn nước ngoài'] != 'Không').mean():.0%} lượt")

    if f["Mốc"].nunique() > 1:
        st.subheader("Xu hướng qua các mốc đánh giá")
        tr = (f.groupby("Mốc").apply(lambda g: pd.Series(tinh_kpi(g))).reset_index()
              .melt("Mốc", ["xuat_hien", "chinh_xac", "palfish", "kenh"], "Chỉ số", "Giá trị"))
        tr["Mốc"] = pd.Categorical(tr["Mốc"], MOC_ORDER, ordered=True)
        st.altair_chart(alt.Chart(tr).mark_line(point=True).encode(
            x="Mốc:N", y=alt.Y("Giá trị:Q", axis=alt.Axis(format="%")),
            color="Chỉ số:N", tooltip=["Mốc:N", "Chỉ số:N", alt.Tooltip("Giá trị:Q", format=".0%")],
        ).properties(height=300), use_container_width=True)
    else:
        st.info("Chỉ mới có 1 mốc — biểu đồ xu hướng sẽ hiện khi có mốc Cuối T1 / Cuối T2.")

with tab_pr:
    st.caption("Cùng 9 nhóm câu hỏi như bảng “Độ chính xác theo nhóm câu hỏi” ở tab Tổng quan, "
               "sắp xếp theo đúng thứ tự đó.")

    st.subheader("Tỷ lệ độ chính xác theo nhóm câu hỏi")
    st.altair_chart(_bd_ty_le_cx(f, "Nhóm prompt", NHOM_ORDER), use_container_width=True)
    st.caption("Thanh càng nhiều vàng/đỏ → nhóm câu hỏi đó AI trả lời càng kém.")

    st.subheader("Số ý lỗi theo nhóm câu hỏi (tách theo mức ưu tiên)")
    st.altair_chart(_bd_so_loi_muc(f, "Nhóm prompt", NHOM_ORDER), use_container_width=True)
    st.caption("Thanh dài = nhóm tích tụ nhiều lỗi; phần đỏ là lỗi P0 (nghiêm trọng).")

    st.subheader("Nhóm câu hỏi dính những mã lỗi nào")
    st.altair_chart(_bd_pf_theo_nhom(f, "Nhóm prompt", NHOM_ORDER), use_container_width=True)

with tab_nt:
    st.caption("Cùng các nền tảng như bảng “Độ chính xác theo nền tảng AI tìm kiếm” ở tab Tổng quan.")
    plat_order = sorted(f["Nền tảng"].unique())

    st.subheader("Tỷ lệ độ chính xác theo nền tảng")
    st.altair_chart(_bd_ty_le_cx(f, "Nền tảng", plat_order), use_container_width=True)

    st.subheader("Số ý lỗi theo nền tảng (tách theo mức ưu tiên)")
    st.altair_chart(_bd_so_loi_muc(f, "Nền tảng", plat_order), use_container_width=True)

    st.subheader("Nền tảng nào dính những mã lỗi nào")
    st.altair_chart(_bd_pf_theo_nhom(f, "Nền tảng", plat_order), use_container_width=True)
    st.caption("Hành vi trích dẫn nguồn của từng nền tảng: xem tab Nguồn trích dẫn.")

with tab_pf:
    st.subheader("Danh mục & tần suất mã lỗi")
    bpf = bang_pf(f)
    if bpf.empty:
        st.info("Không có mã PF nào trong phạm vi lọc.")
    else:
        bpf_c = bpf.assign(**{"Mã lỗi": bpf["Mã"].map(pf_nhan)})
        st.altair_chart(alt.Chart(bpf_c).mark_bar().encode(
            x=alt.X("Số lượt:Q"),
            y=alt.Y("Mã lỗi:N", sort="-x", title=None),
            color=alt.Color("Mức:N", scale=alt.Scale(domain=list(MAU_MUC), range=list(MAU_MUC.values()))),
            tooltip=["Mã:N", "Tên lỗi:N", "Mô tả:N", "Mức:N", "Số lượt:Q",
                     "Nền tảng dính:N", "Prompt:N"],
        ).properties(height=max(200, 26 * len(bpf))), use_container_width=True)
        st.caption("Bảng dưới: giải thích từng mã lỗi là gì.")
        st.dataframe(bpf, use_container_width=True, hide_index=True,
                     column_config={"Mô tả": st.column_config.TextColumn(width="large")})

    st.divider()
    st.subheader("Phân bố lỗi")
    daca = f[f["Độ chính xác"].isin(["Đúng", "Đúng một phần", "Sai", "Không có thông tin"])]
    if daca.empty:
        st.info("Chưa có lượt nào được chấm trong phạm vi lọc.")
    else:
        d1, d2 = st.columns(2)
        with d1:
            st.caption("Số lỗi trên mỗi lượt trả lời (bao nhiêu lượt có 0 lỗi, 1 lỗi, 2 lỗi…)")
            dist = (daca["Số lỗi"].fillna(0).astype(int).value_counts().sort_index()
                    .rename_axis("Số lỗi / lượt").reset_index(name="Số lượt"))
            st.altair_chart(alt.Chart(dist).mark_bar().encode(
                x=alt.X("Số lỗi / lượt:O"),
                y=alt.Y("Số lượt:Q"),
                tooltip=["Số lỗi / lượt:O", "Số lượt:Q"],
            ).properties(height=300), use_container_width=True)
        with d2:
            st.caption("Phân bố theo nhóm chủ đề lỗi (cột “Loại lỗi” trong sheet)")
            loai = pd.Series([p.strip() for s in f["Loại lỗi"]
                              for p in re.split(r";", str(s)) if p.strip()])
            if loai.empty:
                st.info("Cột “Loại lỗi” đang trống.")
            else:
                vc = loai.value_counts().rename_axis("Nhóm chủ đề").reset_index(name="Số lượt")
                st.altair_chart(alt.Chart(vc).mark_bar().encode(
                    x=alt.X("Số lượt:Q"),
                    y=alt.Y("Nhóm chủ đề:N", sort="-x", title=None),
                    tooltip=["Nhóm chủ đề:N", "Số lượt:Q"],
                ).properties(height=max(200, 26 * len(vc))), use_container_width=True)

with tab_ng:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Tên miền AI thường trích dẫn")
        dom = pd.Series([x for t in f["Nguồn AI trích dẫn"] for x in tach_domain(t)])
        if dom.empty:
            st.info("Cột 'Nguồn AI trích dẫn' đang trống.")
        else:
            vc = dom.value_counts().head(15).rename_axis("Tên miền").reset_index(name="Số lượt")
            st.altair_chart(alt.Chart(vc).mark_bar().encode(
                x="Số lượt:Q", y=alt.Y("Tên miền:N", sort="-x", title=None),
                tooltip=["Tên miền:N", "Số lượt:Q"],
            ).properties(height=max(200, 24 * len(vc))), use_container_width=True)
    with c2:
        st.subheader("Nguồn phát sinh thông tin sai")
        bad = pd.Series([x for t in f["Nguồn thông tin sai"]
                         for x in re.split(r"[;,]", t) if x.strip()]).str.strip()
        bad = bad[bad.ne("")].apply(lambda s: s.split("/")[0].split()[0] if s else s)
        if bad.empty:
            st.info("Cột 'Nguồn thông tin sai' đang trống.")
        else:
            vc = bad.value_counts().head(15).rename_axis("Nguồn").reset_index(name="Số lượt")
            st.altair_chart(alt.Chart(vc).mark_bar(color="#C62828").encode(
                x="Số lượt:Q", y=alt.Y("Nguồn:N", sort="-x", title=None),
                tooltip=["Nguồn:N", "Số lượt:Q"],
            ).properties(height=max(200, 24 * len(vc))), use_container_width=True)

    st.subheader("Hành vi trích dẫn nguồn theo nền tảng")
    gnt = f.groupby("Nền tảng").agg(**{
        "Số lượt": ("Prompt ID", "size"),
        "Trích palfish.vn": ("Trích palfish.vn", "mean"),
        "Có kênh chính thống": ("Kênh chính thống khác", "mean"),
    })
    gnt["Lẫn TT nước ngoài"] = (f.assign(_x=f["Trộn nước ngoài"].ne("Không"))
                               .groupby("Nền tảng")["_x"].mean())
    for c in ["Trích palfish.vn", "Có kênh chính thống", "Lẫn TT nước ngoài"]:
        gnt[c] = (gnt[c] * 100).round().astype(int).astype(str) + "%"
    st.dataframe(gnt.reset_index(), use_container_width=True, hide_index=True)

with tab_ct:
    st.subheader("Toàn bộ lượt kiểm tra")
    show = ["Ngày chạy", "Mốc", "Nền tảng", "Loại tài khoản", "Prompt ID", "Nhóm prompt", "Xuất hiện",
            "Vị trí đề cập", "Độ chính xác", "Số lỗi", "Loại lỗi", "Trộn nước ngoài",
            "Trích palfish.vn", "Nguồn thông tin sai"]
    st.dataframe(f[show], use_container_width=True, hide_index=True)

    st.subheader("Xem chi tiết một lượt")
    nhan = f.apply(lambda r: f"{r['Nền tảng']} · {r['Prompt ID']} · {r['Độ chính xác']}", axis=1)
    idx = st.selectbox("Chọn lượt kiểm tra", options=list(f.index), format_func=lambda i: nhan[i])
    r = f.loc[idx]
    st.markdown(f"**{r['Nền tảng']} — {r['Prompt ID']}** · {r['Nhóm prompt']} · "
                f"độ chính xác: **{r['Độ chính xác']}** · số lỗi: **{int(r['Số lỗi'])}**")
    if r["_pf"]:
        st.markdown("\n".join(f"- **{pf_nhan(x)}** — {PF_MOTA.get(x, '')}" for x in r["_pf"]))
    if r["Đoạn có vấn đề"]:
        st.error(f"**Nội dung có vấn đề:** {r['Đoạn có vấn đề']}")
    if r["Nguồn thông tin sai"]:
        st.write(f"**Nguồn phát sinh thông tin sai:** {r['Nguồn thông tin sai']}")
    if r["Ghi chú"]:
        st.info(f"**Ghi chú:** {r['Ghi chú']}")
    with st.expander("Nội dung trả lời của AI"):
        st.write(r["Câu trả lời"])
    with st.expander("Nguồn AI trích dẫn"):
        st.write(r["Nguồn AI trích dẫn"] or "(trống)")
    if r["Link bằng chứng"]:
        st.write(f"[Ảnh chụp / hội thoại minh chứng]({r['Link bằng chứng']})")

with tab_bc:
    st.subheader("Bản tổng hợp định kỳ (tự động tạo)")
    txt = bao_cao_tuan(f, k)
    st.code(txt, language="markdown")
    st.download_button("Tải bản .md", data=txt.encode("utf-8"),
                       file_name=f"bao-cao-GEO-{dt.date.today():%Y%m%d}.md", mime="text/markdown")
