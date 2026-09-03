# -*- coding: utf-8 -*-
"""Lớp đa ngôn ngữ cho dashboard. Tiếng Việt là gốc; EN + 中文 dịch sẵn.
KHÔNG dịch: dữ liệu tự do lấy từ sheet (câu trả lời AI, Ghi chú, Loại lỗi gõ tay…)."""

LANGS = ["vi", "en", "zh"]
LANG_NAMES = {"vi": "Tiếng Việt", "en": "English", "zh": "中文"}

# ---------------------------------------------------------------- chuỗi giao diện
# key = chuỗi tiếng Việt gốc; value = {"en": ..., "zh": ...}
UI = {
    # sidebar
    "🌐 Ngôn ngữ giao diện": {"en": "🌐 Interface language", "zh": "🌐 界面语言"},
    "Thiết lập & bộ lọc": {"en": "Settings & filters", "zh": "设置与筛选"},
    "Nguồn dữ liệu": {"en": "Data source", "zh": "数据源"},
    "Liên kết Google Sheet (để trống dùng mặc định)":
        {"en": "Google Sheet link (blank = default)", "zh": "Google 表格链接（留空则用默认）"},
    "Làm mới dữ liệu": {"en": "Refresh data", "zh": "刷新数据"},
    "Tự động cập nhật": {"en": "Auto-refresh", "zh": "自动刷新"},
    "Tải lại mỗi {n} phút": {"en": "Reload every {n} min", "zh": "每 {n} 分钟重新加载"},
    "Cập nhật lúc {t} · {n} lượt": {"en": "Updated {t} · {n} runs", "zh": "更新于 {t} · {n} 条记录"},
    "Mốc đánh giá": {"en": "Evaluation round", "zh": "评估轮次"},
    "Nền tảng AI": {"en": "AI platform", "zh": "AI 平台"},
    "Nhóm câu hỏi": {"en": "Question cluster", "zh": "问题分组"},
    "Loại tài khoản": {"en": "Account type", "zh": "账号类型"},
    "Mã lỗi (PF)": {"en": "Error code (PF)", "zh": "错误代码 (PF)"},
    "Chọn 1 mã để chỉ xem lượt có mã đó":
        {"en": "Pick one code to see only runs with it", "zh": "选择一个代码，仅查看含该错误的记录"},
    "Khoảng thời gian": {"en": "Date range", "zh": "日期范围"},
    "Tất cả": {"en": "All", "zh": "全部"},
    # lỗi tải / rỗng
    "Không đọc được Google Sheet.":
        {"en": "Could not read the Google Sheet.", "zh": "无法读取 Google 表格。"},
    "Sheet đọc được nhưng chưa có lượt chạy nào hợp lệ "
    "(cần Prompt ID dạng Qxx và cột 'Câu trả lời đầy đủ' có nội dung).":
        {"en": "Sheet loaded but no valid runs (need Prompt ID like Qxx and a non-empty "
               "'Full answer' column).",
         "zh": "已读取表格，但没有有效记录（需要 Qxx 形式的 Prompt ID，且「完整回答」列有内容）。"},
    "Không có dòng nào khớp bộ lọc.":
        {"en": "No rows match the filters.", "zh": "没有符合筛选条件的数据。"},
    # tiêu đề + link
    "GEO PalFish VN — Báo cáo giám sát thông tin thương hiệu trên nền tảng AI":
        {"en": "GEO PalFish VN — Brand information monitoring on AI platforms",
         "zh": "GEO PalFish 越南 —— AI 平台品牌信息监测报告"},
    "📄 [Mở Google Sheet nguồn]({u}) · [tab 4a — Nhật ký lượt chạy]({u4}) · "
    "[tab 3 — Issue tracker]({u3})":
        {"en": "📄 [Open source Google Sheet]({u}) · [tab 4a — Run log]({u4}) · "
               "[tab 3 — Issue tracker]({u3})",
         "zh": "📄 [打开源 Google 表格]({u}) · [标签页 4a — 检测记录]({u4}) · "
               "[标签页 3 — 问题跟踪]({u3})"},
    # khối giới thiệu
    "ℹ️ Giới thiệu & cách đọc dashboard":
        {"en": "ℹ️ About & how to read this dashboard", "zh": "ℹ️ 说明与阅读指南"},
    "INTRO_BODY": {
        "en": (
            "**What this dashboard does**  \n"
            "It tracks how AI platforms (ChatGPT, Gemini, AI Google, Perplexity) answer "
            "when users ask about PalFish Vietnam.\n\n"
            "**How scoring works**  \n"
            "Each round: run **20 fixed questions** on the 4 platforms (see the “Reference” "
            "panel below), a few times each. Each answer is checked against the **approved "
            "PalFish brand information sheet**, then scored: Fully correct / Partially "
            "correct / Incorrect / No information.\n\n"
            "**Reading the numbers**\n"
            "- **Test run** = one question asked once on one platform.\n"
            "- **Error point** = one specific mistake in an answer. One run can carry "
            "several, so total error points usually exceed the number of wrong answers.\n"
            "- **PF-xxx code** = a named error type (PF = *PalFish*). Name + description on "
            "the **Error catalog** tab.\n"
            "- **Priority P0 / P1 / P2**: P0 = critical, fix now · P1 = important · "
            "P2 = long-term.\n\n"
            "**Who fixes what** (Resolution status tab)\n"
            "- **Mai** — content fixes, official-channel updates.\n"
            "- **IT-Minh** — website technical fixes (redirects, schema, domains).\n"
            "- **Josh** — approves messaging & handles major issues (brand origin, legal "
            "entity).\n\n"
            "**Evaluation round**: each measurement is one round. Only the first round "
            "(*Baseline*) exists so far; the trend chart appears from round 2."),
        "zh": (
            "**这个仪表盘做什么**  \n"
            "跟踪当用户询问 PalFish 越南时，各 AI 平台（ChatGPT、Gemini、AI Google、"
            "Perplexity）的回答情况。\n\n"
            "**如何评分**  \n"
            "每一轮：在 4 个平台上运行 **20 个固定问题**（见下方「对照表」），每题若干次。"
            "将每条回答与**已审定的 PalFish 品牌信息表**比对，评为：完全正确 / 部分正确 / "
            "错误 / 无信息。\n\n"
            "**看懂数字**\n"
            "- **检测次数** = 在一个平台上问一个问题一次。\n"
            "- **错误点** = 回答中的一处具体错误。一次记录可能有多处，所以错误点总数"
            "通常大于错误回答数。\n"
            "- **PF-xxx 代码** = 已命名的错误类型（PF = *PalFish*）。名称与说明见"
            "**「错误目录」**标签页。\n"
            "- **优先级 P0 / P1 / P2**：P0 = 严重，需立即处理 · P1 = 重要 · P2 = 长期优化。\n\n"
            "**谁负责修复**（「处理状态」标签页）\n"
            "- **Mai** —— 内容修复、官方渠道更新。\n"
            "- **IT-Minh** —— 网站技术修复（跳转、结构化数据、域名）。\n"
            "- **Josh** —— 审定口径并处理重大问题（品牌起源、法人主体）。\n\n"
            "**评估轮次**：每次测量为一轮。目前仅第一轮（*基线*）；从第 2 轮起显示趋势图。"),
    },
    # KPI
    "Tổng lượt kiểm tra": {"en": "Total test runs", "zh": "检测总次数"},
    "Trả lời chính xác": {"en": "Fully correct", "zh": "完全正确"},
    "Chính xác một phần": {"en": "Partially correct", "zh": "部分正确"},
    "Trả lời sai": {"en": "Incorrect", "zh": "错误回答"},
    "Tổng số lỗi ghi nhận": {"en": "Total error points", "zh": "错误点总数"},
    "↳ {n} ý lỗi trong nhóm": {"en": "↳ {n} error points in this group", "zh": "↳ 该组共 {n} 个错误点"},
    "↳ = tổng 3 ô bên trái": {"en": "↳ = sum of the 3 cells on the left", "zh": "↳ = 左侧 3 格之和"},
    # chú giải câu hỏi
    "📋 Chú giải: 20 câu hỏi prompt & 9 nhóm":
        {"en": "📋 Reference: the 20 prompt questions & 9 clusters",
         "zh": "📋 对照表：20 个提问与 9 个分组"},
    "20 câu hỏi cố định (nguyên văn — không đổi giữa các mốc). "
    "Nguồn: tab “20 Prompt” trong Google Sheet.":
        {"en": "20 fixed questions (verbatim — unchanged across rounds). "
               "Source: the “20 Prompt” tab in the Google Sheet.",
         "zh": "20 个固定问题（原文，各轮不变）。来源：Google 表格的「20 Prompt」标签页。"},
    "Nhóm": {"en": "Cluster", "zh": "分组"},
    "Mã": {"en": "Code", "zh": "代码"},
    "Câu hỏi": {"en": "Question", "zh": "问题"},
    # tab names
    "Tổng quan": {"en": "Overview", "zh": "总览"},
    "Phân tích theo câu hỏi": {"en": "By question", "zh": "按问题"},
    "Phân tích theo nền tảng": {"en": "By platform", "zh": "按平台"},
    "Danh mục lỗi": {"en": "Error catalog", "zh": "错误目录"},
    "Nguồn trích dẫn": {"en": "Cited sources", "zh": "引用来源"},
    "Trạng thái xử lý lỗi": {"en": "Resolution status", "zh": "处理状态"},
    "Dữ liệu chi tiết": {"en": "Raw data", "zh": "明细数据"},
    "Báo cáo định kỳ": {"en": "Periodic report", "zh": "定期报告"},
    # tab Tổng quan
    "Độ chính xác theo nhóm câu hỏi": {"en": "Accuracy by question cluster", "zh": "各问题分组的准确率"},
    "Mỗi ô: số câu (tỷ lệ trong nhóm). Màu càng đậm = tỷ lệ ở mức đó càng cao.":
        {"en": "Each cell: run count (share within cluster). Darker = higher share at that level.",
         "zh": "每格：记录数（组内占比）。颜色越深 = 该级别占比越高。"},
    "Tỷ lệ tổng": {"en": "Overall breakdown", "zh": "总体占比"},
    "Độ chính xác theo nền tảng AI tìm kiếm": {"en": "Accuracy by AI platform", "zh": "各 AI 平台的准确率"},
    "Lẫn thông tin nước ngoài / lỗi thời": {"en": "Foreign / outdated info mixed in", "zh": "混入境外 / 过时信息"},
    "{p} lượt": {"en": "{p} of runs", "zh": "占 {p}"},
    "Xu hướng qua các mốc đánh giá": {"en": "Trend across evaluation rounds", "zh": "各评估轮次的趋势"},
    "Chỉ mới có 1 mốc — biểu đồ xu hướng sẽ hiện khi có mốc Cuối T1 / Cuối T2.":
        {"en": "Only 1 round so far — the trend chart appears once round 2 exists.",
         "zh": "目前仅 1 轮 —— 出现第 2 轮后将显示趋势图。"},
    "TỔNG CỘNG": {"en": "TOTAL", "zh": "合计"},
    "Tổng": {"en": "Total", "zh": "合计"},
    "% Đúng": {"en": "% Correct", "zh": "正确率"},
    # nhãn biểu đồ dùng chung
    "Tỷ lệ": {"en": "Share", "zh": "占比"},
    "Số câu": {"en": "Runs", "zh": "记录数"},
    "Độ chính xác": {"en": "Accuracy", "zh": "准确度"},
    "Số ý lỗi": {"en": "Error points", "zh": "错误点"},
    "Số lượt dính": {"en": "Affected runs", "zh": "涉及记录数"},
    "Số lượt": {"en": "Runs", "zh": "记录数"},
    "Mã lỗi": {"en": "Error code", "zh": "错误代码"},
    "Mức ưu tiên": {"en": "Priority", "zh": "优先级"},
    "Nền tảng": {"en": "Platform", "zh": "平台"},
    # tab Phân tích theo câu hỏi
    "Cùng 9 nhóm câu hỏi như bảng “Độ chính xác theo nhóm câu hỏi” ở tab Tổng quan, "
    "sắp xếp theo đúng thứ tự đó.":
        {"en": "Same 9 clusters as the “Accuracy by question cluster” table on the Overview "
               "tab, in the same order.",
         "zh": "与「总览」标签页「各问题分组的准确率」表相同的 9 个分组，顺序一致。"},
    "Tỷ lệ độ chính xác theo nhóm câu hỏi":
        {"en": "Accuracy share by question cluster", "zh": "各问题分组的准确率占比"},
    "Thanh càng nhiều vàng/đỏ → nhóm câu hỏi đó AI trả lời càng kém.":
        {"en": "More amber/red in a bar → AI does worse on that cluster.",
         "zh": "条形中黄 / 红越多 → AI 在该分组表现越差。"},
    "Số ý lỗi theo nhóm câu hỏi (tách theo mức ưu tiên)":
        {"en": "Error points by cluster (by priority)", "zh": "各分组的错误点数（按优先级）"},
    "Thanh dài = nhóm tích tụ nhiều lỗi; phần đỏ là lỗi P0 (nghiêm trọng).":
        {"en": "Longer bar = more accumulated errors; red is P0 (critical).",
         "zh": "条形越长 = 该组累积错误越多；红色为 P0（严重）。"},
    "Nhóm câu hỏi dính những mã lỗi nào":
        {"en": "Which error codes affect each cluster", "zh": "各分组涉及哪些错误代码"},
    # tab Phân tích theo nền tảng
    "Cùng các nền tảng như bảng “Độ chính xác theo nền tảng AI tìm kiếm” ở tab Tổng quan.":
        {"en": "Same platforms as the “Accuracy by AI platform” table on the Overview tab.",
         "zh": "与「总览」标签页「各 AI 平台的准确率」表相同的平台。"},
    "Tỷ lệ độ chính xác theo nền tảng":
        {"en": "Accuracy share by platform", "zh": "各平台的准确率占比"},
    "Số ý lỗi theo nền tảng (tách theo mức ưu tiên)":
        {"en": "Error points by platform (by priority)", "zh": "各平台的错误点数（按优先级）"},
    "Nền tảng nào dính những mã lỗi nào":
        {"en": "Which error codes affect each platform", "zh": "各平台涉及哪些错误代码"},
    "Hành vi trích dẫn nguồn của từng nền tảng: xem tab Nguồn trích dẫn.":
        {"en": "Each platform's citation behaviour: see the Cited sources tab.",
         "zh": "各平台的引用行为：见「引用来源」标签页。"},
    # tab Danh mục lỗi
    "Danh mục & tần suất mã lỗi": {"en": "Error catalog & frequency", "zh": "错误目录与频次"},
    "Không có mã PF nào trong phạm vi lọc.":
        {"en": "No PF codes in the current filter.", "zh": "当前筛选下没有 PF 代码。"},
    "Bảng dưới: giải thích từng mã lỗi là gì.":
        {"en": "Table below: what each error code means.", "zh": "下表：每个错误代码的含义。"},
    "Tên lỗi": {"en": "Error name", "zh": "错误名称"},
    "Mô tả": {"en": "Description", "zh": "说明"},
    "Mức": {"en": "Priority", "zh": "优先级"},
    "Nền tảng dính": {"en": "Platforms affected", "zh": "涉及平台"},
    "Prompt": {"en": "Prompt", "zh": "Prompt"},
    "Phân bố lỗi": {"en": "Error distribution", "zh": "错误分布"},
    "Chưa có lượt nào được chấm trong phạm vi lọc.":
        {"en": "No scored runs in the current filter.", "zh": "当前筛选下没有已评分的记录。"},
    "Số lỗi trên mỗi lượt trả lời (bao nhiêu lượt có 0 lỗi, 1 lỗi, 2 lỗi…)":
        {"en": "Errors per answer (how many runs have 0, 1, 2… errors)",
         "zh": "每条回答的错误数（多少条记录有 0、1、2… 个错误）"},
    "Số lỗi / lượt": {"en": "Errors per run", "zh": "每条记录的错误数"},
    # tab Nguồn trích dẫn
    "Những nguồn AI dựa vào khi trả lời. **“Nguồn phát sinh thông tin sai”** = nơi AI "
    "học thông tin không đúng (Baidu, trang review nước ngoài, tin crypto…) — xử lý "
    "hoặc tạo nguồn chính thống đối trọng sẽ giảm lỗi.":
        {"en": "The sources AI relies on. **“Sources behind the wrong info”** = where AI "
               "picked up incorrect information (Baidu, foreign review sites, crypto news…) "
               "— fixing these or creating official counter-content reduces errors.",
         "zh": "AI 回答所依赖的来源。**「错误信息的来源」** = AI 获取错误信息的地方（百度、"
               "境外评价站、加密新闻等）—— 处理这些或建立官方对冲内容可减少错误。"},
    "Tên miền AI thường trích dẫn": {"en": "Domains AI cites most", "zh": "AI 最常引用的域名"},
    "Cột 'Nguồn AI trích dẫn' đang trống.":
        {"en": "The 'AI cited sources' column is empty.", "zh": "「AI 引用来源」列为空。"},
    "Tên miền": {"en": "Domain", "zh": "域名"},
    "Nguồn phát sinh thông tin sai": {"en": "Sources behind the wrong info", "zh": "错误信息的来源"},
    "Cột 'Nguồn thông tin sai' đang trống.":
        {"en": "The 'Wrong-info source' column is empty.", "zh": "「错误信息来源」列为空。"},
    "Nguồn": {"en": "Source", "zh": "来源"},
    "Hành vi trích dẫn nguồn theo nền tảng":
        {"en": "Citation behaviour by platform", "zh": "各平台的引用行为"},
    "Trích palfish.vn": {"en": "Cites palfish.vn", "zh": "引用 palfish.vn"},
    "Có kênh chính thống": {"en": "Has official channel", "zh": "含官方渠道"},
    "Lẫn TT nước ngoài": {"en": "Foreign info mixed", "zh": "混入境外信息"},
    # tab Trạng thái xử lý lỗi
    "Tình trạng xử lý từng lỗi. Người phụ trách: **Mai** = nội dung · "
    "**IT‑Minh** = kỹ thuật website · **Josh** = duyệt / vấn đề lớn. "
    "Lỗi đóng khi test lại 3 lần, hết ở ≥ 2/3 lần. (Bộ lọc bên trái không áp dụng ở tab này.)":
        {"en": "Resolution state of each error. Owners: **Mai** = content · **IT-Minh** = "
               "website tech · **Josh** = approvals / major issues. An error closes when a "
               "re-test 3× clears it in ≥ 2/3 runs. (Left-side filters don't apply here.)",
         "zh": "每个错误的处理状态。负责人：**Mai** = 内容 · **IT-Minh** = 网站技术 · "
               "**Josh** = 审定 / 重大问题。复测 3 次且 ≥ 2/3 次通过即关闭。"
               "（左侧筛选在此标签页不生效。）"},
    "Chưa đọc được tab “3 Issue tracker” (kiểm tra Sheet đã bật quyền xem, "
    "hoặc bạn đang trỏ tới một Sheet khác).":
        {"en": "Could not read the “3 Issue tracker” tab (check the Sheet is shared for "
               "viewing, or you're pointing at a different Sheet).",
         "zh": "无法读取「3 Issue tracker」标签页（请确认表格已开放查看权限，或未指向其他表格）。"},
    "Tổng lỗi ghi nhận": {"en": "Total errors logged", "zh": "已记录错误"},
    "Đang mở": {"en": "Open", "zh": "未关闭"},
    "P0 đang mở": {"en": "P0 open", "zh": "未关闭的 P0"},
    "Đã đóng": {"en": "Closed", "zh": "已关闭"},
    "Lỗi đang mở": {"en": "Open errors", "zh": "未关闭的错误"},
    "Không còn lỗi nào đang mở 🎉": {"en": "No open errors left 🎉", "zh": "已无未关闭的错误 🎉"},
    "Việc đang mở theo người phụ trách": {"en": "Open work by owner", "zh": "按负责人统计的未完成事项"},
    "Lỗi đã đóng": {"en": "Closed errors", "zh": "已关闭的错误"},
    "Chưa có lỗi nào được đóng.": {"en": "No errors closed yet.", "zh": "尚无已关闭的错误。"},
    "Loại": {"en": "Type", "zh": "类型"},
    "Thông tin đúng": {"en": "Correct info", "zh": "正确信息"},
    "Người phụ trách": {"en": "Owner", "zh": "负责人"},
    "Trạng thái": {"en": "Status", "zh": "状态"},
    "Ngày sửa xong": {"en": "Fixed date", "zh": "修复日期"},
    "Ngày test lại": {"en": "Re-test date", "zh": "复测日期"},
    "Ngày đóng": {"en": "Closed date", "zh": "关闭日期"},
    "Kết quả test lại": {"en": "Re-test result", "zh": "复测结果"},
    "Số lỗi": {"en": "Errors", "zh": "错误数"},
    # tab Dữ liệu chi tiết
    "Toàn bộ lượt kiểm tra": {"en": "All test runs", "zh": "全部检测记录"},
    "Xem chi tiết một lượt": {"en": "Inspect one run", "zh": "查看单条记录"},
    "Chọn lượt kiểm tra": {"en": "Pick a run", "zh": "选择一条记录"},
    "độ chính xác": {"en": "accuracy", "zh": "准确度"},
    "số lỗi": {"en": "errors", "zh": "错误数"},
    "**Nội dung có vấn đề:** {v}": {"en": "**Problematic content:** {v}", "zh": "**问题内容：** {v}"},
    "**Nguồn phát sinh thông tin sai:** {v}":
        {"en": "**Source of the wrong info:** {v}", "zh": "**错误信息来源：** {v}"},
    "**Ghi chú:** {v}": {"en": "**Note:** {v}", "zh": "**备注：** {v}"},
    "Nội dung trả lời của AI": {"en": "AI's full answer", "zh": "AI 完整回答"},
    "Nguồn AI trích dẫn": {"en": "AI cited sources", "zh": "AI 引用来源"},
    "(trống)": {"en": "(empty)", "zh": "（空）"},
    "[Ảnh chụp / hội thoại minh chứng]({u})":
        {"en": "[Screenshot / conversation evidence]({u})", "zh": "[截图 / 对话证据]({u})"},
    "Ngày chạy": {"en": "Run date", "zh": "检测日期"},
    "Mốc": {"en": "Round", "zh": "轮次"},
    "Prompt ID": {"en": "Prompt ID", "zh": "Prompt ID"},
    "Nhóm prompt": {"en": "Cluster", "zh": "分组"},
    "Xuất hiện": {"en": "Appeared", "zh": "是否出现"},
    "Vị trí đề cập": {"en": "Mention position", "zh": "提及位置"},
    "Loại lỗi": {"en": "Error type", "zh": "错误类型"},
    "Trộn nước ngoài": {"en": "Foreign info", "zh": "混入境外信息"},
    "Nguồn thông tin sai": {"en": "Wrong-info source", "zh": "错误信息来源"},
    # tab Báo cáo định kỳ (UI ngoài nội dung md)
    "Bản tổng hợp định kỳ (tự động tạo)": {"en": "Periodic summary (auto-generated)", "zh": "定期汇总（自动生成）"},
    "Toàn bộ (mọi ngày)": {"en": "All (every day)", "zh": "全部（所有日期）"},
    "Chọn ngày / khoảng ngày": {"en": "Pick a day / date range", "zh": "选择某天 / 日期范围"},
    "Khoảng ngày": {"en": "Date range", "zh": "日期范围"},
    "Chọn cùng 1 ngày cho cả 2 ô để lấy đúng ngày đó.":
        {"en": "Set both boxes to the same day to get just that day.",
         "zh": "两个框选同一天即可只取该天。"},
    "Không theo bộ lọc bên trái. Phần Issue tracker luôn là trạng thái hiện tại. "
    "Copy / tải về, thêm phần “Việc cần làm” rồi gửi. Công cụ không tự lưu / gửi.":
        {"en": "Ignores the left-side filters. The Issue tracker section is always the "
               "current state. Copy / download, add a “to-do” section, then send. The tool "
               "does not save or send on its own.",
         "zh": "不受左侧筛选影响。问题跟踪部分始终为当前状态。复制 / 下载后自行补充「待办事项」"
               "再发送。工具不会自动保存或发送。"},
    "Không có lượt kiểm tra nào trong khoảng ngày đã chọn.":
        {"en": "No test runs in the selected date range.", "zh": "所选日期范围内没有检测记录。"},
    "Tải bản .md": {"en": "Download .md", "zh": "下载 .md"},
    "Xem dạng văn bản thô (để copy sang email / chat)":
        {"en": "View as plain text (to copy into email / chat)",
         "zh": "查看纯文本（便于复制到邮件 / 聊天）"},
    # nội dung báo cáo định kỳ (nhãn cố định)
    "Báo cáo giám sát GEO PalFish — {d}":
        {"en": "GEO PalFish monitoring report — {d}", "zh": "GEO PalFish 监测报告 —— {d}"},
    "{moc} · {nq} prompt · {n} lượt · {nts}":
        {"en": "{moc} · {nq} prompts · {n} runs · {nts}", "zh": "{moc} · {nq} 个提问 · {n} 条记录 · {nts}"},
    "1. Tóm tắt": {"en": "1. Summary", "zh": "1. 摘要"},
    "{n} lượt: đúng hoàn toàn **{nd} ({pd})**, đúng một phần {nm} ({pm}), sai {ns} ({ps}). "
    "Ghi nhận **{ty} ý lỗi**, trong đó **{np0} lỗi P0**: {p0list}.":
        {"en": "{n} runs: fully correct **{nd} ({pd})**, partially correct {nm} ({pm}), "
               "incorrect {ns} ({ps}). **{ty} error points**, including **{np0} P0 errors**: "
               "{p0list}.",
         "zh": "{n} 条记录：完全正确 **{nd}（{pd}）**，部分正确 {nm}（{pm}），错误 {ns}（{ps}）。"
               "共 **{ty} 个错误点**，其中 **{np0} 个 P0 错误**：{p0list}。"},
    "Điểm nóng: kém nhất là **{nt}** ({pc} đúng); nhóm {nhom}.":
        {"en": "Hot spots: weakest platform **{nt}** ({pc} correct); clusters {nhom}.",
         "zh": "重点：表现最差的平台是 **{nt}**（正确率 {pc}）；分组 {nhom}。"},
    "2. Chỉ số": {"en": "2. Metrics", "zh": "2. 指标"},
    "Chỉ số": {"en": "Metric", "zh": "指标"},
    "Giá trị": {"en": "Value", "zh": "数值"},
    "Tỷ lệ xuất hiện": {"en": "Appearance rate", "zh": "出现率"},
    "Đúng hoàn toàn": {"en": "Fully correct", "zh": "完全正确"},
    "Tổng ý lỗi": {"en": "Total error points", "zh": "错误点总数"},
    "Lẫn TT nước ngoài / lỗi thời": {"en": "Foreign / outdated info", "zh": "境外 / 过时信息"},
    "3. Lỗi P0 — xử lý gấp": {"en": "3. P0 errors — urgent", "zh": "3. P0 错误 —— 紧急"},
    "_Không có lỗi P0._": {"en": "_No P0 errors._", "zh": "_没有 P0 错误。_"},
    "cả {n} nền tảng": {"en": "all {n} platforms", "zh": "全部 {n} 个平台"},
    "{n} lượt": {"en": "{n} runs", "zh": "{n} 条记录"},
    "4. Top lỗi khác": {"en": "4. Other top errors", "zh": "4. 其他主要错误"},
    "_Không có._": {"en": "_None._", "zh": "_无。_"},
    "5. Trạng thái xử lý (Issue tracker)":
        {"en": "5. Resolution status (Issue tracker)", "zh": "5. 处理状态（问题跟踪）"},
    "_Chưa đọc được Issue tracker._":
        {"en": "_Could not read the Issue tracker._", "zh": "_无法读取问题跟踪表。_"},
    "- Tổng {ni} mã · đang mở {nmo} (P0: {a} · P1: {b} · P2: {c}) · đã đóng {nd}":
        {"en": "- {ni} codes total · {nmo} open (P0: {a} · P1: {b} · P2: {c}) · {nd} closed",
         "zh": "- 共 {ni} 个代码 · {nmo} 个未关闭（P0: {a} · P1: {b} · P2: {c}）· {nd} 个已关闭"},
    "- Việc theo người: {v}": {"en": "- Work by owner: {v}", "zh": "- 按负责人：{v}"},
    "- Đang chờ Josh / Jacob / HQ chốt: {v}":
        {"en": "- Awaiting decision from Josh / Jacob / HQ: {v}",
         "zh": "- 等待 Josh / Jacob / 总部拍板：{v}"},
    "Xu hướng qua các mốc": {"en": "Trend across rounds", "zh": "各轮次趋势"},
    "Lượt": {"en": "Runs", "zh": "记录数"},
    "Tỷ lệ đúng": {"en": "Accuracy", "zh": "正确率"},
    "Tổng lỗi": {"en": "Total errors", "zh": "错误总数"},
}

# ---------------------------------------------------------------- danh mục cố định
V_CX = {
    "Đúng": {"en": "Correct", "zh": "正确"},
    "Đúng một phần": {"en": "Partially correct", "zh": "部分正确"},
    "Sai": {"en": "Incorrect", "zh": "错误"},
    "Không có thông tin": {"en": "No information", "zh": "无信息"},
    "Chưa chấm được": {"en": "Not scored", "zh": "未评分"},
}
V_NHOM = {
    "Pháp nhân & nhận diện": {"en": "Legal entity & identity", "zh": "法人主体与品牌识别"},
    "Địa chỉ văn phòng": {"en": "Office addresses", "zh": "办公地址"},
    "Liên hệ & đăng ký học thử": {"en": "Contact & trial signup", "zh": "联系方式与试听报名"},
    "Độ tuổi & hình thức học": {"en": "Age & learning format", "zh": "适学年龄与授课形式"},
    "Giáo viên": {"en": "Teachers", "zh": "师资"},
    "Giáo trình & khóa học": {"en": "Curriculum & courses", "zh": "教材与课程"},
    "Học phí": {"en": "Tuition", "zh": "学费"},
    "Uy tín & đánh giá phụ huynh": {"en": "Reputation & parent reviews", "zh": "口碑与家长评价"},
    "So sánh & quy mô & báo chí": {"en": "Comparison, scale & press", "zh": "对比、规模与媒体报道"},
    "Khác": {"en": "Other", "zh": "其他"},
}
V_MOC = {
    "Baseline": {"en": "Baseline", "zh": "基线"},
    "Cuối T1": {"en": "End of M1", "zh": "第1月末"},
    "Cuối T2": {"en": "End of M2", "zh": "第2月末"},
    "Test lại": {"en": "Re-test", "zh": "复测"},
}
V_TRON = {
    "Không": {"en": "None", "zh": "无"},
    "Nhẹ": {"en": "Slight", "zh": "轻微"},
    "Có": {"en": "Yes", "zh": "有"},
}
V_TT = {
    "Mới": {"en": "New", "zh": "新建"},
    "Đã xác nhận": {"en": "Confirmed", "zh": "已确认"},
    "Đang sửa": {"en": "In progress", "zh": "处理中"},
    "Đã sửa (chờ test)": {"en": "Fixed (pending test)", "zh": "已修复（待测）"},
    "Đang theo dõi": {"en": "Monitoring", "zh": "跟踪中"},
    "Đã đóng": {"en": "Closed", "zh": "已关闭"},
}
V_TK = {
    "Miễn phí": {"en": "Free", "zh": "免费"},
    "Trả phí": {"en": "Paid", "zh": "付费"},
    "(không ghi)": {"en": "(unspecified)", "zh": "（未填）"},
    "(chưa gán)": {"en": "(unassigned)", "zh": "（未分配）"},
}
V_PFTEN = {
    "PF-001": {"en": "Org schema name", "zh": "组织架构名称"},
    "PF-002": {"en": "Brand name", "zh": "品牌名称"},
    "PF-003": {"en": "Homepage figures", "zh": "首页数据"},
    "PF-004": {"en": "Site language tag", "zh": "站点语言标记"},
    "PF-005": {"en": "Gmail address", "zh": "Gmail 邮箱"},
    "PF-006": {"en": "Missing HCMC address", "zh": "缺胡志明市地址"},
    "PF-007": {"en": "Missing legal entity", "zh": "缺法人信息"},
    "PF-008": {"en": "Outdated sitemap", "zh": "过时的站点地图"},
    "PF-009": {"en": "Age range", "zh": "年龄段"},
    "PF-010": {"en": "Non-standard sources", "zh": "非标准来源"},
    "PF-011": {"en": "Brand origin", "zh": "品牌起源"},
    "PF-012": {"en": "Legal entity", "zh": "法人主体"},
    "PF-013": {"en": "HCMC address", "zh": "胡志明市地址"},
    "PF-014": {"en": "Outdated page / hotline", "zh": "过时页面 / 热线"},
    "PF-015": {"en": "Country count", "zh": "国家数量"},
    "PF-016": {"en": "Recruitment contact", "zh": "招聘联系方式"},
    "PF-017": {"en": "Native-teacher claim", "zh": "母语外教说法"},
    "PF-018": {"en": "Product name", "zh": "产品名称"},
    "PF-019": {"en": "Tuition", "zh": "学费"},
    "PF-020": {"en": "Outdated reviews", "zh": "过时评价"},
    "PF-021": {"en": "No source cited", "zh": "未引用来源"},
    "PF-022": {"en": "Fabricated features", "zh": "编造功能"},
    "PF-023": {"en": "Branch address", "zh": "分支地址"},
}
V_PFMOTA = {
    "PF-001": {"en": "JSON-LD homepage declares the org name as \"admin1\".",
               "zh": "首页 JSON-LD 将组织名称写成 “admin1”。"},
    "PF-002": {"en": "Mixes Palfish / PALFISH / \"Palfish Class\" / \"PalFishclassVN\".",
               "zh": "混用 Palfish / PALFISH /「Palfish Class」/「PalFishclassVN」。"},
    "PF-003": {"en": "The 3 counters (60M / 163 countries / 50k teachers) show \"0+\" with "
                     "JavaScript off.",
               "zh": "关闭 JavaScript 时，3 个计数器（6000万 / 163 国 / 5万教师）显示为 “0+”。"},
    "PF-004": {"en": "og:locale / inLanguage = en-US on a Vietnamese-language site.",
               "zh": "越南语站点却把 og:locale / inLanguage 设为 en-US。"},
    "PF-005": {"en": "Official email is palfishjsc@gmail.com instead of a domain email.",
               "zh": "官方邮箱用的是 palfishjsc@gmail.com，而非企业域名邮箱。"},
    "PF-006": {"en": "palfish.vn lists only 2 Hanoi addresses, no HCMC.",
               "zh": "palfish.vn 只列出 2 个河内地址，没有胡志明市地址。"},
    "PF-007": {"en": "No full company name + tax code on home / contact / footer.",
               "zh": "首页 / 联系页 / 页脚均无完整公司名称和税号。"},
    "PF-008": {"en": "Sitemap ~200 URLs, many old 2023 pages, last updated 10/2024.",
               "zh": "站点地图约 200 个网址，多为 2023 年旧页，最后更新于 2024/10。"},
    "PF-009": {"en": "AI answers age as 3–15 / 4–12 / 2–15; the correct range is 3–12.",
               "zh": "AI 把年龄说成 3–15 / 4–12 / 2–15；正确应为 3–12 岁。"},
    "PF-010": {"en": "AI cites odd domains: palfish.com.vn, intpalfish.com, Google Play "
                     "cn.xckj…",
               "zh": "AI 引用了不规范域名：palfish.com.vn、intpalfish.com、Google Play 的 cn.xckj 等。"},
    "PF-011": {"en": "AI states PalFish was founded in Beijing; correct: HQ in Singapore.",
               "zh": "AI 称 PalFish 创立于北京；正确说法为总部位于新加坡。"},
    "PF-012": {"en": "3 legal entities + partner TTL; AI is unclear which one is responsible.",
               "zh": "存在 3 个法人主体 + 合作方 TTL；AI 说不清谁负责。"},
    "PF-013": {"en": "AI says the HCMC office is at 157–159 Nguyen Thi Thap; \"25\" is the "
                     "partner TTL's address.",
               "zh": "AI 称胡志明市办公室位于阮氏十字街 157–159 号；“25 号”其实是合作方 TTL 的地址。"},
    "PF-014": {"en": "Cites hocthu.palfish.vn + old hotline 0982 520 521; correct: "
                     "learn.palfish.vn/triallesson, 0962 023 416.",
               "zh": "引用 hocthu.palfish.vn 和旧热线 0982 520 521；正确应为 "
                     "learn.palfish.vn/triallesson、0962 023 416。"},
    "PF-015": {"en": "Country count inconsistent: 163 / 160+ / 200+, even within one platform.",
               "zh": "国家数量不一致：163 / 160+ / 200+，同一平台内也自相矛盾。"},
    "PF-016": {"en": "AI gives recruitment email palfishrecruitment@gmail.com; correct: "
                     "hr@palfishhcm.com.",
               "zh": "AI 给出的招聘邮箱是 palfishrecruitment@gmail.com；正确应为 hr@palfishhcm.com。"},
    "PF-017": {"en": "\"100% native teachers\" contradicts Mai's doc §4.5 (\"20% of images "
                     "are Filipino teachers\").",
               "zh": "「100% 母语外教」与 Mai 文档 §4.5（「20% 教师图片为菲律宾教师」）相矛盾。"},
    "PF-018": {"en": "AI calls the reading product \"PalFish Reading\"; the correct VN name "
                     "is \"PalFish English\".",
               "zh": "AI 把阅读产品称作「PalFish Reading」；越南市场的正确名称是「PalFish English」。"},
    "PF-019": {"en": "AI gives specific prices (150–250k/lesson, 53-lesson pack ~9.8M); "
                     "pricing is not public.",
               "zh": "AI 给出具体价格（每节 15–25 万越南盾，53 节套餐约 980 万）；官方并未公开价格。"},
    "PF-020": {"en": "AI cites reddit \"has_palfish_imploded\" (2021), Glassdoor, US App "
                     "Store — outdated.",
               "zh": "AI 引用 reddit「has_palfish_imploded」（2021）、Glassdoor、美区 App Store —— 均已过时。"},
    "PF-021": {"en": "AI answers about PalFish without citing any official channel.",
               "zh": "AI 回答 PalFish 相关问题时未引用任何官方渠道。"},
    "PF-022": {"en": "AI invents \"group classes / book club / livestream\" that PalFish "
                     "English VN does not have.",
               "zh": "AI 编造了「小组课 / 读书会 / 直播」等 PalFish English 越南版并不存在的功能。"},
    "PF-023": {"en": "Branch address \"Imperia Garden\" doesn't match: 203 Nguyen Huy Tuong "
                     "vs 143 Nguyen Tuan.",
               "zh": "分支办公室地址「Imperia Garden」对不上：阮辉想街 203 号 vs 阮俊街 143 号。"},
}
V_CAUHOI = {
    "Q01": {"en": "What is PalFish Vietnam?", "zh": "PalFish 越南是什么？"},
    "Q02": {"en": "What is PalFish Vietnam's official website?", "zh": "PalFish 越南的官方网站是什么？"},
    "Q03": {"en": "Which company operates PalFish in Vietnam?", "zh": "PalFish 在越南由哪家公司运营？"},
    "Q04": {"en": "Which country is PalFish from, and how is it related to PalFish Singapore "
                  "or PalFish global?",
            "zh": "PalFish 是哪个国家的品牌？与 PalFish 新加坡或全球 PalFish 有何关系？"},
    "Q05": {"en": "What is PalFish's office address in Hanoi?", "zh": "PalFish 在河内的办公地址是什么？"},
    "Q06": {"en": "Does PalFish have an office in Ho Chi Minh City? Where?",
            "zh": "PalFish 在胡志明市有办公室吗？地址在哪？"},
    "Q07": {"en": "What are PalFish Vietnam's contact phone and email?",
            "zh": "PalFish 越南的联系电话和邮箱是什么？"},
    "Q08": {"en": "How do I sign up for a PalFish trial lesson?", "zh": "如何报名 PalFish 的试听课？"},
    "Q09": {"en": "What age range is PalFish for?", "zh": "PalFish 适合几岁的孩子？"},
    "Q10": {"en": "Does PalFish teach one-on-one or in group classes?",
            "zh": "PalFish 是一对一授课还是小组课？"},
    "Q11": {"en": "Who are PalFish's teachers — are they native speakers, and where from?",
            "zh": "PalFish 的老师是谁？是母语者吗？来自哪里？"},
    "Q12": {"en": "What English courses / curricula does PalFish offer for children?",
            "zh": "PalFish 为孩子提供哪些英语课程 / 教材？"},
    "Q13": {"en": "How much is PalFish tuition, and what packages are available?",
            "zh": "PalFish 的学费大约多少？有哪些套餐？"},
    "Q14": {"en": "What is a PalFish lesson like, and what's in the learning app?",
            "zh": "PalFish 一节课是怎样的？学习 App 有哪些功能？"},
    "Q15": {"en": "Is PalFish reputable — is it worth enrolling my child?",
            "zh": "PalFish 靠谱吗？值得让孩子报名吗？"},
    "Q16": {"en": "What do parents say about PalFish? Any negative feedback?",
            "zh": "家长对 PalFish 的评价如何？有负面反馈吗？"},
    "Q17": {"en": "How does PalFish differ from other one-on-one kids' English platforms?",
            "zh": "PalFish 与其他少儿一对一英语平台有何不同？"},
    "Q18": {"en": "What are PalFish's pros and cons?", "zh": "PalFish 的优点和缺点是什么？"},
    "Q19": {"en": "How long has PalFish operated in Vietnam, and how big is it (students, "
                  "teachers)?",
            "zh": "PalFish 在越南运营多久了？规模如何（学员数、教师数）？"},
    "Q20": {"en": "Has PalFish been mentioned or certified by any press or education body?",
            "zh": "有媒体或教育机构报道 / 认证过 PalFish 吗？"},
}


def _pick(d: dict, vi: str, lang: str) -> str:
    if lang == "vi" or vi not in d:
        return vi
    return d[vi].get(lang, vi)


def make_t(lang: str):
    """Trả về bộ hàm dịch đã gắn ngôn ngữ."""
    def t(vi: str) -> str:
        return _pick(UI, vi, lang)

    def t_cx(v):
        return _pick(V_CX, v, lang)

    def t_nhom(v):
        return _pick(V_NHOM, v, lang)

    def t_moc(v):
        return _pick(V_MOC, v, lang)

    def t_tron(v):
        return _pick(V_TRON, v, lang)

    def t_tt(v):
        return _pick(V_TT, v, lang)

    def t_tk(v):
        return _pick(V_TK, v, lang)

    def t_pften(ma):
        return V_PFTEN.get(ma, {}).get(lang, "") if lang != "vi" else ""

    def t_pfmota(ma, vi_mota):
        return _pick({vi_mota: V_PFMOTA.get(ma, {})}, vi_mota, lang)

    def t_cauhoi(qid, vi_q):
        return _pick({vi_q: V_CAUHOI.get(qid, {})}, vi_q, lang)

    return {
        "t": t, "cx": t_cx, "nhom": t_nhom, "moc": t_moc, "tron": t_tron,
        "tt": t_tt, "tk": t_tk, "pften": t_pften, "pfmota": t_pfmota, "cauhoi": t_cauhoi,
    }
