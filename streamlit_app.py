# -*- coding: utf-8 -*-
"""
AI CMO 데모 대시보드 (포트폴리오용)
────────────────────────────────────────────────────────
- Claude Code로 직접 만든 실제 광고 분석 대시보드의 '데모 버전'입니다.
- 표시되는 모든 수치는 가상(임시) 데이터이며, 실제 광고주 데이터가 아닙니다.
- API 연동 없이 메모리에서 데이터를 생성하므로 조회가 즉시 이뤄집니다.
- 실제 운영 대시보드와 동일한 UI/UX(shadcn zinc 다크 테마 + 8탭 구성).
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(page_title="윤지욱 마케팅 대시보드", page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

# ── shadcn zinc 다크 팔레트 (실제 대시보드와 동일) ──
BG = "#09090b"; CARD = "#18181b"; BORDER = "#27272a"
TEXT = "#fafafa"; MUTED = "#a1a1aa"
ACCENT = "#6366f1"; GREEN = "#22c55e"; RED = "#ef4444"; AMBER = "#f59e0b"

st.markdown(f"""
<style>
.stApp {{ background:{BG}; }}
#MainMenu, header, footer {{ visibility:hidden; }}
.block-container {{ padding-top:2rem; max-width:1280px; }}
h1,h2,h3,h4,h5 {{ color:{TEXT}; letter-spacing:-0.01em; }}
.block-container h1 {{ font-size:1.55rem; }}
.block-container h3 {{ font-size:1.1rem; }}
.block-container h5 {{ font-size:0.92rem; }}
section[data-testid="stSidebar"] h2 {{ font-size:1.0rem; }}
div[data-testid="stMetric"] {{ background:{CARD}; border:1px solid {BORDER}; border-radius:12px;
    padding:14px 16px; transition:border-color .15s; }}
div[data-testid="stMetric"]:hover {{ border-color:{ACCENT}; }}
div[data-testid="stMetricLabel"] p {{ color:{MUTED}; font-size:11px; font-weight:600;
    text-transform:uppercase; letter-spacing:.5px; }}
div[data-testid="stMetricValue"] {{ color:{TEXT}; font-size:22px; font-weight:700;
    font-variant-numeric:tabular-nums; }}
.stTabs [data-baseweb="tab-list"] {{ gap:30px; }}
.stTabs [data-baseweb="tab"] {{ font-size:14px; font-weight:600; color:{MUTED};
    border-bottom:2px solid transparent; padding-bottom:6px; }}
.stTabs [aria-selected="true"] {{ color:{ACCENT}; border-bottom-color:{ACCENT}; }}
div[data-testid="stExpander"] {{ background:{CARD}; border:1px solid {BORDER}; border-radius:12px; }}
section[data-testid="stSidebar"] {{ background:#0a0a0c; border-right:1px solid {BORDER}; }}
.demo-banner {{ background:rgba(99,102,241,.12); color:#a5b4fc; border:1px solid rgba(99,102,241,.3);
    border-radius:10px; padding:9px 14px; font-size:12.5px; font-weight:600; margin-bottom:16px; }}
div[role="radiogroup"] {{ gap:30px; border-bottom:1px solid {BORDER}; margin-bottom:18px; padding-bottom:0; }}
div[role="radiogroup"] > label {{ margin:0 !important; padding:0 2px 10px 2px; border-bottom:2px solid transparent; }}
div[role="radiogroup"] > label > div:first-child {{ display:none !important; }}
div[role="radiogroup"] > label p {{ font-size:14px; font-weight:600; color:{MUTED}; transition:color .15s; }}
div[role="radiogroup"] > label:hover p {{ color:{TEXT}; }}
div[role="radiogroup"] > label:has(input:checked) {{ border-bottom-color:{ACCENT}; }}
div[role="radiogroup"] > label:has(input:checked) p {{ color:{ACCENT}; }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 가상 데이터 (deterministic)
# ============================================================
@st.cache_data
def gen():
    np.random.seed(42)
    start = date(2026, 1, 1); days = 180
    dates = [start + timedelta(d) for d in range(days)]
    per = {"Google Ads": 2, "Meta": 2, "TikTok": 1}  # 총 5개 캠페인
    AGS = ["광고그룹 1", "광고그룹 2"]
    ADS = ["영상소재 A", "영상소재 B", "영상소재 C"]
    structure = []
    for ch, n in per.items():
        for c in range(n):
            camp = f"{ch} 캠페인 {c+1}"
            for ag in AGS:
                for ad in ADS:
                    structure.append((ch, camp, ag, ad))
    rows = []
    for ch, camp, ag, cr in structure:
        bcvr = np.random.uniform(1.5, 3.2); bcpa = np.random.uniform(40000, 52000)
        q = np.random.uniform(.75, 1.3); broas = np.random.uniform(1.3, 1.8)
        for i, dt in enumerate(dates):
            t = i / (days - 1)
            cvr = bcvr * (1 + 1.3 * t) * np.random.uniform(.8, 1.2)
            cpa = bcpa * (1 - .45 * t) / q * np.random.uniform(.85, 1.15)
            clicks = int(np.random.uniform(70, 380) * q)
            impr = int(clicks / np.random.uniform(.008, .02))
            conv = max(0, int(clicks * cvr / 100))
            spend = int(conv * cpa) if conv else int(clicks * np.random.uniform(300, 800))
            rev = int(spend * (broas + 1.9 * t) * np.random.uniform(.85, 1.2))
            rows.append(dict(date=pd.Timestamp(dt), channel=ch, campaign=camp, adgroup=ag,
                             creative=cr, spend=spend, impressions=impr, clicks=clicks,
                             conversions=conv, revenue=rev))
    return pd.DataFrame(rows)


def metrics(df):
    df = df.copy(); c = set(df.columns)
    if {"spend", "conversions"} <= c:
        df["CPA"] = (df.spend / df.conversions).replace([np.inf, -np.inf], 0).fillna(0).round(0)
    if {"clicks", "impressions"} <= c:
        df["CTR"] = (df.clicks / df.impressions * 100).replace([np.inf], 0).fillna(0).round(2)
        df["CPC"] = (df.spend / df.clicks).replace([np.inf], 0).fillna(0).round(0)
        df["CPM"] = (df.spend / df.impressions * 1000).replace([np.inf], 0).fillna(0).round(0)
    if {"conversions", "clicks"} <= c:
        df["CVR"] = (df.conversions / df.clicks * 100).replace([np.inf], 0).fillna(0).round(2)
    if {"revenue", "spend"} <= c:
        df["ROAS"] = (df.revenue / df.spend * 100).replace([np.inf], 0).fillna(0).round(0)
    return df


def chart(fig, h=320):
    fig.update_layout(font_family="sans-serif", font_color=TEXT, plot_bgcolor=CARD,
                      paper_bgcolor=CARD, height=h, margin=dict(l=10, r=10, t=30, b=10),
                      colorway=[ACCENT, GREEN, AMBER],
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    fig.update_xaxes(showgrid=False, linecolor=BORDER)
    fig.update_yaxes(showgrid=True, gridcolor=BORDER, zeroline=False)
    return fig


def won(v): return f"₩{int(v):,}"


df = metrics(gen())
df["month"] = df["date"].dt.to_period("M").astype(str)
TODAY = df["date"].max()

# ── 사이드바 ──
with st.sidebar:
    st.markdown("## 📊 윤지욱 마케팅 대시보드")
    st.caption("캠페인 성과 모니터링 + AI 시뮬레이션")
    st.button("⚡ API 데이터 동기화", type="primary", use_container_width=True, key="sync")
    st.caption(f"마지막 동기화: {TODAY.strftime('%Y-%m-%d')} 14:30")
    st.caption(f"데이터: {df['date'].min().strftime('%m/%d')} ~ {TODAY.strftime('%m/%d')}")

st.markdown("# 📊 윤지욱 마케팅 대시보드")
st.markdown('<div class="demo-banner">데모 버전 · 표시 수치는 모두 가상 데이터입니다 (실제 광고주 데이터 아님). '
            'Claude Code로 직접 개발한 실제 운영 대시보드의 데모입니다.</div>', unsafe_allow_html=True)

CHS = ["Google Ads", "Meta", "TikTok"]
TAB_NAMES = ["📊 실시간", "📅 일자별", "🔬 A/B테스트", "🆕 신규소재", "🔁 월간 중복DB 현황", "📺 노출 Youtube 채널", "🔍 경쟁사 분석"]
active = st.radio("탭 네비게이션", TAB_NAMES, horizontal=True, label_visibility="collapsed", key="active_tab")

# ============================================================
# 1) 📊 금일
# ============================================================
if active == TAB_NAMES[0]:
    st.markdown(f"###### {TODAY.strftime('%Y-%m-%d %H:%M')} 기준")
    tdf = df[df.date == TODAY]; ydf = df[df.date == TODAY - pd.Timedelta(days=1)]
    cols = st.columns(len(CHS) + 1)
    for col, ch in zip(cols, CHS):
        c = tdf[tdf.channel == ch]
        conv = int(c.conversions.sum() * 0.85); spend = int(c.spend.sum())
        col.metric(ch, won(spend // conv) if conv else "-", f"{conv}건 · {spend//10000:,}만원", delta_color="off")
    tot_conv = int(tdf.conversions.sum() * 0.85); tot_spend = int(tdf.spend.sum())
    cols[-1].metric("합계", won(tot_spend // tot_conv) if tot_conv else "-",
                    f"{tot_conv}건 · {tot_spend//10000:,}만원", delta_color="off")

    st.markdown("##### 캠페인별 금일 성과")
    k = st.columns(4)
    y_conv = int(ydf.conversions.sum() * 0.85); y_spend = int(ydf.spend.sum())
    k[0].metric("금일 비용 (합계)", won(tot_spend))
    k[1].metric("금일 실전환 (합계)", f"{tot_conv:,}건")
    k[2].metric("금일 실CPA", won(tot_spend // tot_conv) if tot_conv else "-")
    k[3].metric("어제 실CPA (합계)", won(y_spend // y_conv) if y_conv else "-")

    g = metrics(tdf.groupby("campaign", as_index=False)[["spend", "impressions", "clicks", "conversions"]].sum())
    gy = ydf.groupby("campaign", as_index=False)["spend"].sum().rename(columns={"spend": "y_spend"})
    gyc = ydf.groupby("campaign", as_index=False)["conversions"].sum().rename(columns={"conversions": "y_conv"})
    g = g.merge(gy, on="campaign", how="left").merge(gyc, on="campaign", how="left")
    g["real_conv"] = (g.conversions * 0.85).round(0)
    g["real_cpa"] = (g.spend / g.real_conv).replace([np.inf], 0).fillna(0)
    g["y_real_cpa"] = (g.y_spend / (g.y_conv * 0.85)).replace([np.inf], 0).fillna(0)
    g = g.sort_values("spend", ascending=False)
    disp = pd.DataFrame({
        "캠페인": g.campaign, "비용": g.spend.map(won), "노출": g.impressions.map(lambda x: f"{int(x):,}"),
        "클릭": g.clicks.map(lambda x: f"{int(x):,}"), "CPC": g.CPC.map(won),
        "CTR(%)": g.CTR.map(lambda x: f"{x:.2f}"), "전환(실제)": g.real_conv.map(lambda x: f"{int(x):,}"),
        "CPA(실제)": g.real_cpa.map(lambda x: won(x) if x else "-"),
        "전일 실CPA": g.y_real_cpa.map(lambda x: won(x) if x else "-")})
    st.dataframe(disp, use_container_width=True, hide_index=True)

    st.markdown("##### 크리에이티브(소재)별 금일 성과")
    cg = metrics(tdf.groupby(["campaign", "adgroup", "creative"], as_index=False)[
        ["spend", "impressions", "clicks", "conversions"]].sum())
    cg["real_conv"] = (cg.conversions * 0.85).round(0)
    cg["real_cpa"] = (cg.spend / cg.real_conv).replace([np.inf], 0).fillna(0)
    cg = cg[cg.spend > 0].sort_values("spend", ascending=False)
    cdisp = pd.DataFrame({
        "캠페인": cg.campaign, "광고그룹": cg.adgroup, "소재명": cg.creative,
        "비용": cg.spend.map(won), "노출": cg.impressions.map(lambda x: f"{int(x):,}"),
        "클릭": cg.clicks.map(lambda x: f"{int(x):,}"), "CTR(%)": cg.CTR.map(lambda x: f"{x:.2f}"),
        "전환(실제)": cg.real_conv.map(lambda x: f"{int(x):,}"),
        "CPA(실제)": cg.real_cpa.map(lambda x: won(x) if x else "-")})
    st.dataframe(cdisp, use_container_width=True, hide_index=True, height=400)

# ============================================================
# 2) 📅 일자별
# ============================================================
elif active == TAB_NAMES[1]:
    st.markdown("#### 📅 일자별 성과 상세 비교")
    st.caption("매체/캠페인을 선택하면 일자별 성과 데이터와 추이를 확인할 수 있습니다")
    c1, c2 = st.columns([1, 1])
    chsel = c1.multiselect("📡 매체", CHS, default=CHS, key="d_media")
    rng = c2.date_input("조회 기간 (직접 설정)", value=(TODAY - pd.Timedelta(days=13), TODAY),
                        min_value=df.date.min(), max_value=TODAY, key="d_range")
    if isinstance(rng, (list, tuple)) and len(rng) == 2:
        s, e = pd.Timestamp(rng[0]), pd.Timestamp(rng[1])
    else:
        d0 = rng[0] if isinstance(rng, (list, tuple)) else rng; s = e = pd.Timestamp(d0)
    d = df[df.channel.isin(chsel)]
    d = d[(d.date >= s) & (d.date <= e)]
    agg = metrics(d.groupby("date", as_index=False)[["spend", "impressions", "clicks", "conversions", "revenue"]].sum())
    agg["real_conv"] = (agg.conversions * 0.85).round(0)
    rc = int(agg.real_conv.sum()); sp = int(agg.spend.sum())
    k = st.columns(5)
    k[0].metric("합계 비용", won(sp))
    k[1].metric("전환(실제)", f"{rc:,}건")
    k[2].metric("CPA(실제)", won(sp // rc) if rc else "-")
    k[3].metric("평균 CPM", won(agg.spend.sum() / agg.impressions.sum() * 1000))
    k[4].metric("합계 클릭", f"{int(agg.clicks.sum()):,}")

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**일별 비용 & 전환**")
        f = go.Figure()
        f.add_bar(x=agg.date, y=agg.spend, name="비용", marker_color=ACCENT)
        f.add_trace(go.Scatter(x=agg.date, y=agg.real_conv * (agg.spend.max() / max(1, agg.real_conv.max())),
                               name="전환(실제)", line=dict(color=GREEN, width=2)))
        st.plotly_chart(chart(f), use_container_width=True)
    with g2:
        st.markdown("**CPA & CTR 추이**")
        f = go.Figure()
        f.add_trace(go.Scatter(x=agg.date, y=agg.CPA, name="CPA", line=dict(color=ACCENT, width=2)))
        f.add_trace(go.Scatter(x=agg.date, y=agg.CTR * (agg.CPA.max() / max(0.1, agg.CTR.max())),
                               name="CTR", line=dict(color=AMBER, width=2)))
        st.plotly_chart(chart(f), use_container_width=True)

    st.markdown("##### 캠페인 → 광고그룹 → 소재 드릴다운")
    s1, s2, s3 = st.columns(3)
    cs = s1.selectbox("캠페인", ["전체"] + sorted(d.campaign.unique()), key="d_camp")
    dd = d if cs == "전체" else d[d.campaign == cs]
    asel = s2.selectbox("광고그룹", ["전체"] + sorted(dd.adgroup.unique()), key="d_ag")
    if asel != "전체": dd = dd[dd.adgroup == asel]
    s3.selectbox("소재", ["전체"] + sorted(dd.creative.unique()), key="d_cr")
    gb, lbl = ("campaign", "캠페인") if cs == "전체" else (("adgroup", "광고그룹") if asel == "전체" else ("creative", "소재"))
    t = metrics(dd.groupby(gb, as_index=False)[["spend", "impressions", "clicks", "conversions", "revenue"]].sum()).sort_values("conversions", ascending=False)
    ddisp = pd.DataFrame({
        lbl: t[gb], "비용": t.spend.map(won),
        "노출": t.impressions.map(lambda x: f"{int(x):,}"), "클릭": t.clicks.map(lambda x: f"{int(x):,}"),
        "전환": t.conversions.map(lambda x: f"{int(x):,}"), "CPA": t.CPA.map(won),
        "CTR(%)": t.CTR.map(lambda x: f"{x:.2f}"), "CVR(%)": t.CVR.map(lambda x: f"{x:.2f}"),
        "ROAS(%)": t.ROAS.map(lambda x: f"{int(x):,}%")})
    st.dataframe(ddisp, use_container_width=True, hide_index=True)

# ============================================================
# 3) 🔬 A/B테스트
# ============================================================
elif active == TAB_NAMES[2]:
    st.markdown("### 🔬 A/B테스트 — 가설 / 액션 / 성과")
    st.caption("Claude 대화로 결정된 액션이 자동 등록됩니다. 액션 이후 일별 성과(실 전환 포함)를 자동 수집.")

    import calendar as _cal
    with st.expander("📅 액션 캘린더", expanded=True):
        _months = [f"{TODAY.year}-{m:02d}" for m in range(1, 13)]
        sel = st.selectbox("월 선택", _months, index=TODAY.month - 1, key="ab_month")
        yr, mo = int(sel[:4]), int(sel[5:7])
        events = {3: [("🎨", "Google Ads 캠페인 1", GREEN)], 7: [("💰", "Meta 캠페인 2", AMBER)],
                  10: [("⏸", "Google Ads 캠페인 2", RED)], 14: [("💵", "TikTok 캠페인 1", ACCENT)],
                  18: [("🆕", "Meta 캠페인 1", ACCENT)]}
        evals = {12: ["Meta 캠페인 2"], 17: ["Google Ads 캠페인 2"]}
        weeks = _cal.Calendar(firstweekday=6).monthdayscalendar(yr, mo)
        heads = ["일", "월", "화", "수", "목", "금", "토"]
        html = '<table style="width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed">'
        html += "<tr>" + "".join(
            f'<th style="padding:6px;border:1px solid {BORDER};'
            f'color:{RED if h=="일" else (ACCENT if h=="토" else MUTED)}">{h}</th>' for h in heads) + "</tr>"
        for wk in weeks:
            html += "<tr>"
            for day in wk:
                if day == 0:
                    html += f'<td style="border:1px solid {BORDER};height:78px;background:{BG}"></td>'; continue
                chips = ""
                for emoji, label, color in events.get(day, []):
                    chips += (f'<div style="background:{color}22;color:{color};border-radius:6px;'
                              f'padding:1px 5px;margin:2px 0;font-size:10px;white-space:nowrap;'
                              f'overflow:hidden;text-overflow:ellipsis">{emoji} {label}</div>')
                for c in evals.get(day, []):
                    chips += (f'<div style="border:1px dashed {MUTED};color:{MUTED};border-radius:6px;'
                              f'padding:1px 5px;margin:2px 0;font-size:10px">🔚 {c}</div>')
                mark = " 📍" if (day == TODAY.day and yr == TODAY.year and mo == TODAY.month) else ""
                html += (f'<td style="border:1px solid {BORDER};height:78px;vertical-align:top;'
                         f'padding:4px;background:{CARD}"><div style="color:{TEXT};font-weight:600;'
                         f'font-size:11px">{day}{mark}</div>{chips}</td>')
            html += "</tr>"
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
        st.caption("🆕신설 🎯입찰 💰tCPA 💵예산 🎨자산 ⏸OFF · 🟡진행중 🟢성공 🔴실패 · 🔚평가예정 · 📍오늘")

    acts = pd.DataFrame([
        dict(상태="🟢 성공", 계정="Google Ads", 캠페인="Google Ads 캠페인 1", 액션="🎨 신규소재 투입", 경과="D+9", 평가="✅ 완료", 태그="소재"),
        dict(상태="🟡 진행중", 계정="Meta", 캠페인="Meta 캠페인 2", 액션="💰 tCPA 조정", 경과="D+3", 평가="평가 D-1", 태그="입찰"),
        dict(상태="🟡 진행중", 계정="Google Ads", 캠페인="Google Ads 캠페인 2", 액션="⏸ 저효율 소재 OFF", 경과="D+2", 평가="평가 D-2", 태그="OFF"),
        dict(상태="🔴 실패", 계정="TikTok", 캠페인="TikTok 캠페인 1", 액션="💵 예산 증액", 경과="D+14", 평가="❌ 실패", 태그="예산"),
    ])
    st.radio("필터", ["🟡 진행 중", "🟢 완료", "🔴 실패", "📋 전체"], horizontal=True, index=3, key="ab_filter")
    st.markdown(f"#### 📋 전체 ({len(acts)}건)")
    st.dataframe(acts, use_container_width=True, hide_index=True)

    st.markdown("##### 📊 A/B테스트 캠페인 성과 조회")
    camp = st.selectbox("캠페인 선택", sorted(df.campaign.unique()), key="ab_camp")

    AB_INFO = {
        "Google Ads 캠페인 1": ("기존 가로형 소재는 CTR은 높지만 CVR이 낮다 → 세로형 신규 소재가 전환을 끌어올릴 것",
                             "🎨 세로형 신규소재 3종 투입 (D+0)"),
        "Google Ads 캠페인 2": ("저효율 소재가 노출을 독식해 전체 CVR을 낮춘다 → OFF하면 잔여 소재로 전환 회복",
                             "⏸ CTR↑·CVR↓ 소재 OFF (D+0)"),
        "Meta 캠페인 1": ("LP 경유 유입이 즉시 리드폼보다 불량률이 낮다 → LP 전환 캠페인으로 내원율 개선",
                       "🆕 LP 전환 캠페인 신설 (D+0)"),
        "Meta 캠페인 2": ("tCPA를 낮추면 효율은 오르나 볼륨이 준다 → 5.5만원으로 상향해 볼륨 확보",
                       "💰 tCPA 50,000 → 55,000원 (D+0)"),
        "TikTok 캠페인 1": ("예산 증액 시 학습 리셋으로 단기 CPA 악화 → 점진 증액 필요",
                         "💵 일예산 +50% 증액 (D+0)"),
    }
    hyp, act = AB_INFO.get(camp, ("(가설 미등록)", "(액션 미등록)"))
    ca, cb = st.columns(2)
    ca.info(f"**💡 가설**\n\n{hyp}")
    cb.success(f"**🎬 액션**\n\n{act}")

    cd = metrics(df[df.campaign == camp].groupby("date", as_index=False)[
        ["spend", "impressions", "clicks", "conversions", "revenue"]].sum())
    cd["real_conv"] = (cd.conversions * 0.85).round(0)
    cd["real_cpa"] = (cd.spend / cd.real_conv).replace([np.inf], 0).fillna(0)
    cd = cd[cd.date > TODAY - pd.Timedelta(days=30)]
    baseline = cd.real_cpa[cd.real_cpa > 0].head(7).mean() if (cd.real_cpa > 0).any() else 0
    sp = int(cd.spend.sum()); rc = int(cd.real_conv.sum())
    rec = cd[cd.date > TODAY - pd.Timedelta(days=7)]; prev = cd[(cd.date <= TODAY - pd.Timedelta(days=7)) & (cd.date > TODAY - pd.Timedelta(days=14))]
    sp_pct = (rec.spend.sum() / prev.spend.sum() - 1) * 100 if prev.spend.sum() else 0
    cv_pct = (rec.real_conv.sum() / prev.real_conv.sum() - 1) * 100 if prev.real_conv.sum() else 0
    m = st.columns(4)
    m[0].metric("기간 총 spend", won(sp))
    m[1].metric("실 전환(시트)", f"{rc:,}건")
    m[2].metric("spend 변화", f"{sp_pct:+.0f}%", delta_color="off")
    m[3].metric("cv 변화", f"{cv_pct:+.0f}%", delta_color="off")

    st.markdown("**📈 액션 이후 성과 추이**")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**일별 spend / cv**")
        f = go.Figure()
        f.add_bar(x=cd.date, y=cd.spend, name="spend", marker_color=ACCENT)
        f.add_trace(go.Scatter(x=cd.date, y=cd.real_conv * (cd.spend.max() / max(1, cd.real_conv.max())),
                               name="cv", line=dict(color=RED, width=2.5), mode="lines+markers"))
        st.plotly_chart(chart(f, 300), use_container_width=True)
    with g2:
        st.markdown("**CPA 추이**")
        f = go.Figure()
        f.add_trace(go.Scatter(x=cd.date, y=cd.real_cpa, name="실CPA", line=dict(color=GREEN, width=2), mode="lines+markers"))
        if baseline:
            f.add_hline(y=baseline, line_dash="dash", line_color=MUTED, annotation_text="baseline")
        st.plotly_chart(chart(f, 300), use_container_width=True)

    st.markdown("**📝 평가 메모**")
    st.text_area("평가 메모", placeholder="이 액션의 결과·판단을 기록하세요 (예: D+9 실CPA -26%, 성공적 풀 확장 → 유지)",
                 key="ab_memo", label_visibility="collapsed", height=90)
    st.button("💾 평가 저장", key="ab_save")

# ============================================================
# 5) 🆕 신규소재
# ============================================================
elif active == TAB_NAMES[3]:
    st.markdown("### 🆕 신규 소재 D+4 모니터링")
    st.caption("첫 노출일이 21일 이내인 광고 자동 감지. D+0~D+3 학습 페이즈 관망 → D+4부터 본인 CPA × 기존 회복 진단.")
    st.button("🔄 신규 소재 API 조회", type="primary", key="new_scan")
    assets = [
        dict(camp="Google Ads 캠페인 1", ad="영상소재 D", ad_id="38…309", d=9, cpa=31200, pre=42000, post=38500, rec=True, phase="진단"),
        dict(camp="Google Ads 캠페인 2", ad="영상소재 E", ad_id="36…118", d=5, cpa=46800, pre=39000, post=44500, rec=False, phase="진단"),
        dict(camp="Meta 캠페인 1", ad="영상소재 F", ad_id="37…820", d=2, cpa=35400, pre=41000, post=40200, rec=True, phase="학습"),
    ]
    learn = sum(1 for a in assets if a["d"] < 4); diag = sum(1 for a in assets if 4 <= a["d"] <= 21)
    off = sum(1 for a in assets if not a["rec"] and a["d"] >= 4)
    k = st.columns(4)
    k[0].metric("전체 모니터링", f"{len(assets)}개")
    k[1].metric("🟡 학습 페이즈", f"{learn}개", "D+0 ~ D+3", delta_color="off")
    k[2].metric("진단 단계", f"{diag}개", "D+4 ~ D+21", delta_color="off")
    k[3].metric("🔴 OFF 권고", f"{off}개", delta_color="off")

    for a in assets:
        with st.container(border=True):
            h1, h2 = st.columns([3, 1])
            h1.markdown(f"**{a['camp']}**")
            h1.caption(f"소재: **{a['ad']}** (YOUTUBE_VIDEO) · ad_id: `{a['ad_id']}`")
            badge = "🟢" if a["d"] < 4 else ("🟢" if a["rec"] else "🔴")
            h2.markdown(f"### {badge} D+{a['d']}")
            delta = (a["post"] / a["pre"] - 1) * 100
            m = st.columns(3)
            m[0].metric("본인 CPA", won(a["cpa"]))
            m[1].metric("캠페인 CPA pre→post", won(a["post"]), f"{delta:+.1f}% vs {won(a['pre'])}", delta_color="inverse")
            m[2].metric("기존 회복 여부", "🟢 회복" if a["rec"] else "🔴 미회복",
                        "투입 전 ±10% 이내" if a["rec"] else "미회복", delta_color="off")
            if a["d"] < 4:
                st.info("**진단**: 학습 페이즈 — 변경 절대 금지 (ML 학습 사이클 진행 중)")
            elif a["rec"]:
                st.success("**진단**: 성공적 풀 확장 — 유지")
            else:
                st.error("**진단**: 신규가 부진 풀 끌어옴 — 신규만 OFF 검토")

    st.markdown("#### 📈 신규 소재 CPA 추이 (D+0 → 현재)")
    _f = go.Figure()
    for a in assets:
        nd = a["d"] + 1
        series = [round(a["cpa"] * (1 + 0.012 * (a["d"] - x))) for x in range(nd)]
        _f.add_trace(go.Scatter(x=[f"D+{x}" for x in range(nd)], y=series, mode="lines+markers", name=a["ad"]))
    st.plotly_chart(chart(_f, 320), use_container_width=True)
    st.caption("신규 소재가 D+4 이후 CPA가 안정·하락하는지로 안착 여부를 판단합니다.")

# ============================================================
# 6) 🔁 중복률
# ============================================================
elif active == TAB_NAMES[4]:
    st.markdown("### 🔁 월간 중복DB 현황")
    st.caption("해당월 전체 DB에서 연락처 중복 측정. 첫 등장은 unique, 이후 등장은 중복으로 카운트.")
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.date_input("기준일", value=TODAY.date(), key="dup_date")
    c2.multiselect("매체 필터", CHS, default=CHS, key="dup_media")
    c3.info(f"기준월: **{TODAY.year}년 {TODAY.month}월**")
    np.random.seed(11)
    camps = sorted(df.campaign.unique())
    month_db = {c: int(np.random.uniform(800, 1600)) for c in camps}
    dup_rate = {c: round(np.random.uniform(12, 22), 1) for c in camps}
    tot_db = sum(month_db.values()); tot_dup = sum(int(month_db[c] * dup_rate[c] / 100) for c in camps)
    k = st.columns(5)
    k[0].metric("월 합산 DB", f"{tot_db:,}")
    k[1].metric("중복 DB", f"{tot_dup:,}")
    k[2].metric("월 중복률", f"{tot_dup/tot_db*100:.1f}%")
    k[3].metric(f"{TODAY.strftime('%m/%d')} DB", f"{int(tot_db/15):,}")
    k[4].metric(f"{TODAY.strftime('%m/%d')} 중복 DB", f"{int(tot_db/15*np.random.uniform(0.1,0.18)):,}")

    st.markdown("#### 📈 월 중복률 추이 (차단 적용 후 하락)")
    np.random.seed(110)
    dn = max(2, int(TODAY.day))
    trend = [round(max(8, 23 - (0 if x < dn*0.4 else (x-dn*0.4)/(dn*0.6)*8) + np.random.uniform(-1.2, 1.2)), 1) for x in range(dn)]
    _f = go.Figure()
    _f.add_trace(go.Scatter(x=list(range(1, dn+1)), y=trend, mode="lines", line=dict(color=ACCENT, width=2.5),
                            fill="tozeroy", fillcolor="rgba(99,102,241,0.12)"))
    _f.add_vline(x=int(dn*0.4), line_dash="dash", line_color=RED, annotation_text="차단 적용")
    st.plotly_chart(chart(_f, 280), use_container_width=True)

    st.markdown("#### 📊 캠페인별 해당월 누적 중복률")
    dt = pd.DataFrame({"캠페인": camps, "월합산": [month_db[c] for c in camps],
                       "월내중복건": [int(month_db[c] * dup_rate[c] / 100) for c in camps],
                       "월내중복률": [f"{dup_rate[c]:.1f}%" for c in camps]})
    dt["월합산"] = dt["월합산"].map(lambda x: f"{x:,}")
    st.dataframe(dt, use_container_width=True, hide_index=True)

# ============================================================
# 7) 📺 노출 유튜브 채널
# ============================================================
elif active == TAB_NAMES[5]:
    st.markdown("### 📺 노출 Youtube 채널")
    st.caption("Google Ads 디멘드젠 캠페인이 노출된 YouTube 채널 풀을 분석합니다.")

    # 일별 채널 수 가상 시계열 (총 노출 / 신규 유입 / 전환 우수)
    np.random.seed(21)
    _d0 = df["date"].min(); _ndays = (TODAY - _d0).days + 1
    _tot = 120; _yrows = []
    for i in range(_ndays):
        _tot = max(80, _tot + int(np.random.randint(-3, 6)))
        _yrows.append(dict(date=_d0 + pd.Timedelta(days=i), total=_tot,
                           new=int(np.random.randint(2, 12)),
                           good=int(_tot * np.random.uniform(0.18, 0.28))))
    ytd = pd.DataFrame(_yrows); maxd = ytd.date.max()

    cmp_mode = st.checkbox("📊 일자별 비교 모드", key="yt_cmp")

    if not cmp_mode:
        c1, c2 = st.columns([2, 1])
        rng = c1.date_input("조회 기간", value=(maxd - pd.Timedelta(days=13), maxd),
                            min_value=ytd.date.min(), max_value=maxd, key="yt_range")
        c2.button("🔄 API 새로고침", type="primary", use_container_width=True, key="yt_refresh")
        if isinstance(rng, (list, tuple)) and len(rng) == 2:
            s, e = pd.Timestamp(rng[0]), pd.Timestamp(rng[1])
        else:
            d0 = rng[0] if isinstance(rng, (list, tuple)) else rng
            s = e = pd.Timestamp(d0)
        sub = ytd[(ytd.date >= s) & (ytd.date <= e)]
        if sub.empty: sub = ytd.tail(1)
        latest = sub.iloc[-1]
        k = st.columns(3)
        k[0].metric("총 노출 채널", f"{int(latest.total):,}개")
        k[1].metric("기간 내 신규 유입 채널", f"{int(sub.new.sum()):,}개")
        k[2].metric("전환 우수 채널 유지", f"{int(latest.good):,}개", "전환 발생 채널", delta_color="off")
        st.markdown("#### 📈 일별 채널 수 추이")
        f = go.Figure()
        f.add_bar(x=sub.date, y=sub.new, name="신규 유입 채널", marker_color=AMBER)
        f.add_trace(go.Scatter(x=sub.date, y=sub.total, name="총 노출 채널", line=dict(color=ACCENT, width=2.5)))
        f.add_trace(go.Scatter(x=sub.date, y=sub.good, name="전환 우수 채널", line=dict(color=GREEN, width=2)))
        st.plotly_chart(chart(f, 340), use_container_width=True)
        st.caption("총 노출 채널·신규 유입·전환 우수 채널 수를 일별로 추적해 풀 회전을 모니터링합니다.")
    else:
        cc = st.columns(4)
        a1 = cc[0].date_input("기간 A 시작", value=maxd - pd.Timedelta(days=27), key="yt_a1")
        a2 = cc[1].date_input("기간 A 종료", value=maxd - pd.Timedelta(days=14), key="yt_a2")
        b1 = cc[2].date_input("기간 B 시작", value=maxd - pd.Timedelta(days=13), key="yt_b1")
        b2 = cc[3].date_input("기간 B 종료", value=maxd, key="yt_b2")
        A = ytd[(ytd.date >= pd.Timestamp(a1)) & (ytd.date <= pd.Timestamp(a2))]
        B = ytd[(ytd.date >= pd.Timestamp(b1)) & (ytd.date <= pd.Timestamp(b2))]
        at, an, ag = (int(A.total.iloc[-1]) if len(A) else 0, int(A.new.sum()), int(A.good.iloc[-1]) if len(A) else 0)
        bt, bn, bg = (int(B.total.iloc[-1]) if len(B) else 0, int(B.new.sum()), int(B.good.iloc[-1]) if len(B) else 0)
        k = st.columns(3)
        k[0].metric("총 노출 채널", f"{bt:,}개", f"{bt-at:+,} vs A", delta_color="off")
        k[1].metric("신규 유입 채널", f"{bn:,}개", f"{bn-an:+,} vs A", delta_color="off")
        k[2].metric("전환 우수 채널 유지", f"{bg:,}개", f"{bg-ag:+,} vs A", delta_color="off")
        st.markdown("#### 📊 기간 A vs B 비교")
        comp = pd.DataFrame({"구분": ["총 노출 채널", "신규 유입 채널", "전환 우수 채널"], "A": [at, an, ag], "B": [bt, bn, bg]})
        f = go.Figure()
        f.add_bar(x=comp["구분"], y=comp.A, name="기간 A", marker_color="#3f3f46")
        f.add_bar(x=comp["구분"], y=comp.B, name="기간 B", marker_color=ACCENT)
        st.plotly_chart(chart(f, 320), use_container_width=True)

    _camps = sorted(df[df.channel == "Google Ads"].campaign.unique())
    st.markdown("#### 💰 비용 누수 추정 (캠페인 간 채널 중복)")
    leak = pd.DataFrame([
        dict(캠페인A=_camps[0], 캠페인B=_camps[1], 공유채널=42, **{"겹침%": "38.0%", "추정누수(원)": "1,240,000"}),
    ])
    st.dataframe(leak, use_container_width=True, hide_index=True)
    st.caption("⚠️ 추정 누수는 보수적 하한값 — 공유 채널이 많을수록 같은 시청자에게 중복 노출 중.")

# ============================================================
# 8) 🔍 경쟁사
# ============================================================
elif active == TAB_NAMES[6]:
    st.markdown("### 🔍 경쟁사 분석")
    cc1, cc2 = st.columns([1, 4])
    cc1.button("🔄 수동 스크래핑", type="primary", use_container_width=True, key="comp_scrape")
    cc2.caption(f"마지막 스크래핑: {TODAY.strftime('%Y-%m-%d')} 03:00 · 24시간 주기 자동 실행")

    st.markdown("#### 📊 노출 점유율 비교")
    share = pd.DataFrame({"경쟁사": ["경쟁사 A", "경쟁사 B", "경쟁사 C", "우리(자사)"],
                          "노출점유": [31, 24, 18, 12]}).sort_values("노출점유")
    _colors = [ACCENT if n == "우리(자사)" else "#3f3f46" for n in share["경쟁사"]]
    _f = go.Figure(); _f.add_bar(y=share["경쟁사"], x=share["노출점유"], orientation="h", marker_color=_colors)
    st.plotly_chart(chart(_f, 240), use_container_width=True)

    st.markdown("#### 📊 경쟁사 LP 비교")
    comp = pd.DataFrame([
        dict(경쟁사="경쟁사 A", 가격="29만원/개", **{"메인 훅": "당일 식립 가능"}, CTA="무료 상담 신청", 폼필드="이름·연락처", 변경="🔴 변경됨"),
        dict(경쟁사="경쟁사 B", 가격="35만원/개", **{"메인 훅": "20년 경력 원장"}, CTA="이벤트 마감임박", 폼필드="연락처", 변경="✅ 동일"),
        dict(경쟁사="경쟁사 C", 가격="33만원/개", **{"메인 훅": "100% 책임시술"}, CTA="비용 확인하기", 폼필드="이름·연락처·지역", 변경="✅ 동일"),
        dict(경쟁사="🟢 우리(자사)", 가격="31만원/개", **{"메인 훅": "무료 정밀검진"}, CTA="검진 예약", 폼필드="연락처", 변경="✅ 동일"),
    ])
    st.dataframe(comp, use_container_width=True, hide_index=True)

    st.markdown("#### 📜 스크래핑 이력")
    hist = pd.DataFrame([
        dict(일시=f"{TODAY.strftime('%m-%d')} 03:00", 경쟁사="경쟁사 A", 변경="🔴 변경", 해시="a3f9…"),
        dict(일시=f"{(TODAY-pd.Timedelta(days=1)).strftime('%m-%d')} 03:00", 경쟁사="경쟁사 A", 변경="✅ 동일", 해시="b1c7…"),
        dict(일시=f"{(TODAY-pd.Timedelta(days=1)).strftime('%m-%d')} 03:00", 경쟁사="경쟁사 B", 변경="✅ 동일", 해시="d4e2…"),
    ])
    st.dataframe(hist, use_container_width=True, hide_index=True)
    st.caption("LP·가격·CTA 변경 감지 시 텔레그램 자동 알림.")
