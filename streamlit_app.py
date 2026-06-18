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
    padding:16px 18px; transition:border-color .15s;
    min-height:120px; display:flex; flex-direction:column; justify-content:center; }}
div[data-testid="stMetric"]:hover {{ border-color:{ACCENT}; }}
div[data-testid="stMetricLabel"] {{ white-space:normal !important; overflow:visible !important; }}
div[data-testid="stMetricLabel"] p {{ color:{MUTED}; font-size:11.5px; font-weight:600;
    letter-spacing:.2px; white-space:normal; overflow:visible; text-overflow:clip; line-height:1.45; }}
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
span[data-baseweb="tag"] {{ max-width:none !important; height:auto !important; }}
span[data-baseweb="tag"] span {{ max-width:none !important; overflow:visible !important;
    text-overflow:clip !important; white-space:normal !important; }}
div[data-baseweb="select"] > div {{ border:1px solid {BORDER} !important; border-radius:8px !important; background:{CARD} !important; }}
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
    fig.update_yaxes(showgrid=True, gridcolor=BORDER, zeroline=False, hoverformat=",.0f")
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
TAB_NAMES = ["📊 실시간", "📅 일자별", "🔬 A/B테스트", "🆕 신규소재", "🔁 월간 중복DB 현황", "📺 노출 Youtube 채널", "🔍 경쟁사 분석", "📊 코호트"]
active = st.radio("탭 네비게이션", TAB_NAMES, horizontal=True, label_visibility="collapsed", key="active_tab")

# ============================================================
# 1) 📊 금일
# ============================================================
if active == TAB_NAMES[0]:
    st.markdown(f"###### {TODAY.strftime('%Y-%m-%d %H:%M')} 기준")
    tdf = df[df.date == TODAY]; ydf = df[df.date == TODAY - pd.Timedelta(days=1)]
    def _mcard(col, title, cpa, conv, spend, d):
        _dc = GREEN if d >= 0 else RED
        _ar = "↑" if d >= 0 else "↓"
        col.markdown(
            f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:16px 18px;min-height:150px">'
            f'<div style="color:{MUTED};font-size:11.5px;font-weight:600;letter-spacing:.3px;margin-bottom:8px">{title} · 실 CPA</div>'
            f'<div style="color:{TEXT};font-size:23px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1">{won(cpa) if cpa else "-"}</div>'
            f'<div style="color:{_dc};font-size:12px;font-weight:700;margin-top:6px">{_ar} {d:+,}건 vs 전일</div>'
            f'<div style="font-size:12.5px;color:{MUTED};margin-top:11px;padding-top:10px;border-top:1px solid {BORDER}">'
            f'전환 <b style="color:{GREEN};font-size:13.5px">{conv:,}</b>건 · '
            f'소진 <b style="color:{GREEN};font-size:13.5px">{spend//10000:,}</b>만원</div></div>',
            unsafe_allow_html=True)

    cols = st.columns(len(CHS) + 1)
    for col, ch in zip(cols, CHS):
        c = tdf[tdf.channel == ch]; cy = ydf[ydf.channel == ch]
        conv = int(c.conversions.sum() * 0.85); spend = int(c.spend.sum())
        convy = int(cy.conversions.sum() * 0.85); d = conv - convy
        _mcard(col, ch, spend // conv if conv else 0, conv, spend, d)
    tot_conv = int(tdf.conversions.sum() * 0.85); tot_spend = int(tdf.spend.sum())
    ty = int(ydf.conversions.sum() * 0.85); td = tot_conv - ty
    _mcard(cols[-1], "합계", tot_spend // tot_conv if tot_conv else 0, tot_conv, tot_spend, td)

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
    _cmf = st.multiselect("📡 매체 필터", CHS, default=CHS, key="rt_cre_media")
    _ctf = tdf[tdf.channel.isin(_cmf)]
    cg = metrics(_ctf.groupby(["channel", "campaign", "adgroup", "creative"], as_index=False)[
        ["spend", "impressions", "clicks", "conversions"]].sum())
    cg["real_conv"] = (cg.conversions * 0.85).round(0)
    cg["real_cpa"] = (cg.spend / cg.real_conv).replace([np.inf], 0).fillna(0)
    cg["_chord"] = cg.channel.map({c: i for i, c in enumerate(CHS)})
    cg = cg[cg.spend > 0].sort_values(["_chord", "spend"], ascending=[True, False])
    cdisp = pd.DataFrame({
        "매체": cg.channel, "캠페인": cg.campaign, "광고그룹": cg.adgroup, "소재명": cg.creative,
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
    st.caption("매체/캠페인 선택 + 기간(또는 A/B 비교)으로 성과를 확인합니다")

    def _kr(x): return pd.Timestamp(x).strftime("%-m월 %-d일")

    chsel = st.multiselect("📡 매체", CHS, default=CHS, key="d_media")
    cmp_mode = st.checkbox("📊 기간 비교 모드 (A vs B)", key="d_cmp")
    dch = df[df.channel.isin(chsel)]

    if not cmp_mode:
        c1, c2 = st.columns([1, 1])
        quick = c1.selectbox("기간", ["최근 7일", "최근 14일", "최근 30일", "이번달", "직접 설정"], index=1, key="d_quick")
        if quick == "직접 설정":
            rng = c2.date_input("직접 설정", value=(TODAY - pd.Timedelta(days=13), TODAY),
                                min_value=df.date.min(), max_value=TODAY, key="d_range")
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                s, e = pd.Timestamp(rng[0]), pd.Timestamp(rng[1])
            else:
                _d0 = rng[0] if isinstance(rng, (list, tuple)) else rng; s = e = pd.Timestamp(_d0)
        elif quick == "이번달":
            s = TODAY.replace(day=1); e = TODAY; c2.caption(f"📅 {_kr(s)} ~ {_kr(e)}")
        else:
            _n = {"최근 7일": 7, "최근 14일": 14, "최근 30일": 30}[quick]
            s = TODAY - pd.Timedelta(days=_n - 1); e = TODAY; c2.caption(f"📅 {_kr(s)} ~ {_kr(e)}")
        d = dch[(dch.date >= s) & (dch.date <= e)]
        agg = metrics(d.groupby("date", as_index=False)[["spend", "impressions", "clicks", "conversions", "revenue"]].sum())
        agg["real_conv"] = (agg.conversions * 0.85).round(0)
        rc = int(agg.real_conv.sum()); sp = int(agg.spend.sum())
        k = st.columns(5)
        k[0].metric("합계 비용", won(sp))
        k[1].metric("전환(실제)", f"{rc:,}건")
        k[2].metric("CPA(실제)", won(sp // rc) if rc else "-")
        k[3].metric("평균 CPM", won(agg.spend.sum() / agg.impressions.sum() * 1000) if agg.impressions.sum() else "-")
        k[4].metric("합계 클릭", f"{int(agg.clicks.sum()):,}")
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("**일별 비용 & 전환**")
            f = go.Figure()
            f.add_bar(x=agg.date, y=agg.spend, name="비용", marker_color=ACCENT, hovertemplate="비용 %{y:,}원<extra></extra>")
            f.add_trace(go.Scatter(x=agg.date, y=agg.real_conv * (agg.spend.max() / max(1, agg.real_conv.max())),
                                   customdata=agg.real_conv, name="전환(실제)", line=dict(color=GREEN, width=2),
                                   hovertemplate="전환 %{customdata:,}건<extra></extra>"))
            f.update_xaxes(tickformat="%-m월 %-d일"); st.plotly_chart(chart(f), use_container_width=True)
        with g2:
            st.markdown("**CPA & CTR 추이**")
            f = go.Figure()
            f.add_trace(go.Scatter(x=agg.date, y=agg.CPA, name="CPA", line=dict(color=ACCENT, width=2)))
            f.add_trace(go.Scatter(x=agg.date, y=agg.CTR * (agg.CPA.max() / max(0.1, agg.CTR.max())),
                                   name="CTR", line=dict(color=AMBER, width=2)))
            f.update_xaxes(tickformat="%-m월 %-d일"); st.plotly_chart(chart(f), use_container_width=True)

        st.markdown("##### 🔎 드릴다운 (단위 선택 + 복수 선택)")
        unit = st.radio("보기 단위", ["캠페인", "광고그룹", "소재"], horizontal=True, key="d_unit")
        dd = d.copy()
        if unit == "캠페인":
            gb, lbl = "campaign", "캠페인"
        elif unit == "광고그룹":
            dd["_k"] = dd.campaign + " · " + dd.adgroup; gb, lbl = "_k", "광고그룹"
        else:
            dd["_k"] = dd.campaign + " · " + dd.adgroup + " · " + dd.creative.astype(str); gb, lbl = "_k", "소재"
        _opts = sorted(dd[gb].unique())
        _sel = st.multiselect(f"{lbl} 선택 (비우면 전체 · 검색 가능)", _opts, default=[], key=f"d_msel_{unit}")
        if _sel:
            dd = dd[dd[gb].isin(_sel)]
        t = metrics(dd.groupby(gb, as_index=False)[["spend", "impressions", "clicks", "conversions", "revenue"]].sum()).sort_values("conversions", ascending=False)
        ddisp = pd.DataFrame({
            lbl: t[gb], "비용": t.spend.map(won),
            "노출": t.impressions.map(lambda x: f"{int(x):,}"), "클릭": t.clicks.map(lambda x: f"{int(x):,}"),
            "전환": t.conversions.map(lambda x: f"{int(x):,}"), "CPA": t.CPA.map(won),
            "CTR(%)": t.CTR.map(lambda x: f"{x:.2f}"), "CVR(%)": t.CVR.map(lambda x: f"{x:.2f}"),
            "ROAS(%)": t.ROAS.map(lambda x: f"{int(x):,}%")})
        st.dataframe(ddisp, use_container_width=True, hide_index=True)
    else:
        cc = st.columns(4)
        a1 = cc[0].date_input("기간 A 시작", value=TODAY - pd.Timedelta(days=27), min_value=df.date.min(), max_value=TODAY, key="dc_a1")
        a2 = cc[1].date_input("기간 A 종료", value=TODAY - pd.Timedelta(days=14), min_value=df.date.min(), max_value=TODAY, key="dc_a2")
        b1 = cc[2].date_input("기간 B 시작", value=TODAY - pd.Timedelta(days=13), min_value=df.date.min(), max_value=TODAY, key="dc_b1")
        b2 = cc[3].date_input("기간 B 종료", value=TODAY, min_value=df.date.min(), max_value=TODAY, key="dc_b2")
        A = dch[(dch.date >= pd.Timestamp(a1)) & (dch.date <= pd.Timestamp(a2))]
        B = dch[(dch.date >= pd.Timestamp(b1)) & (dch.date <= pd.Timestamp(b2))]
        st.caption(f"📅 기간 A: {_kr(a1)} ~ {_kr(a2)}   vs   기간 B: {_kr(b1)} ~ {_kr(b2)}")

        def _cmp(Ax, Bx, group, glabel):
            rows = []
            for key in sorted(set(Ax[group]) | set(Bx[group])):
                ga = Ax[Ax[group] == key]; gbx = Bx[Bx[group] == key]
                asp = ga.spend.sum(); acv = ga.conversions.sum() * 0.85
                bsp = gbx.spend.sum(); bcv = gbx.conversions.sum() * 0.85
                acpa = asp / acv if acv else 0; bcpa = bsp / bcv if bcv else 0
                cvc = (bcv / acv - 1) * 100 if acv else 0
                cpac = (bcpa / acpa - 1) * 100 if acpa else 0
                rows.append({glabel: key, "A 비용": won(asp), "B 비용": won(bsp),
                             "A 전환": f"{acv:.0f}건", "B 전환": f"{bcv:.0f}건", "전환 변화": f"{cvc:+.0f}%",
                             "A CPA": won(acpa) if acpa else "-", "B CPA": won(bcpa) if bcpa else "-",
                             "CPA 변화": f"{cpac:+.0f}%" if acpa else "-"})
            return pd.DataFrame(rows)

        st.markdown("##### 📡 매체별 A vs B (전체 요약)")
        st.dataframe(_cmp(A, B, "channel", "매체"), use_container_width=True, hide_index=True)

        st.markdown("##### 🔎 드릴다운 A vs B (단위 선택 + 복수 선택)")
        unit = st.radio("비교 단위", ["캠페인", "광고그룹", "소재"], horizontal=True, key="dc_unit")
        _Ax = A.copy(); _Bx = B.copy()
        if unit == "캠페인":
            gb, lbl = "campaign", "캠페인"
        elif unit == "광고그룹":
            _Ax["_k"] = _Ax.campaign + " · " + _Ax.adgroup
            _Bx["_k"] = _Bx.campaign + " · " + _Bx.adgroup
            gb, lbl = "_k", "광고그룹"
        else:
            _Ax["_k"] = _Ax.campaign + " · " + _Ax.adgroup + " · " + _Ax.creative.astype(str)
            _Bx["_k"] = _Bx.campaign + " · " + _Bx.adgroup + " · " + _Bx.creative.astype(str)
            gb, lbl = "_k", "소재"
        _opts = sorted(set(_Ax[gb]) | set(_Bx[gb]))
        _sel = st.multiselect(f"{lbl} 선택 (비우면 전체 · 검색 가능)", _opts, default=[], key=f"dc_msel_{unit}")
        if _sel:
            _Ax = _Ax[_Ax[gb].isin(_sel)]; _Bx = _Bx[_Bx[gb].isin(_sel)]
        st.dataframe(_cmp(_Ax, _Bx, gb, lbl), use_container_width=True, hide_index=True)
        st.caption("전환 변화 ↑ / CPA 변화 ↓ 이면 개선. 비교 단위를 고르고, 비교할 항목을 복수 선택하세요. (위는 매체별 전체 요약)")

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
                    chips += (f'<div style="background:{ACCENT}22;color:#c7d2fe;border-radius:6px;'
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
        st.caption("📍 오늘 · 🔚 평가예정 · 각 칩은 등록된 테스트입니다 — 아래 **'테스트 선택'** 에서 무엇을 검증하는지(가설)와 성과를 확인하세요")

    acts = pd.DataFrame([
        dict(상태="🟢 성공", 계정="Google Ads", 캠페인="Google Ads 캠페인 1", 액션="🎨 신규소재 투입",
             검증가설="세로형 신규 소재가 가로형보다 CVR을 끌어올리는가", 경과="D+9", 평가="✅ 완료"),
        dict(상태="🟡 진행중", 계정="Meta", 캠페인="Meta 캠페인 2", 액션="💰 tCPA 조정",
             검증가설="tCPA 상향이 볼륨을 늘리면서 CPA를 유지하는가", 경과="D+3", 평가="평가 D-1"),
        dict(상태="🟡 진행중", 계정="Google Ads", 캠페인="Google Ads 캠페인 2", 액션="⏸ 저효율 소재 OFF",
             검증가설="저효율 소재 OFF가 잔여 소재 전환을 회복시키는가", 경과="D+2", 평가="평가 D-2"),
        dict(상태="🔴 실패", 계정="TikTok", 캠페인="TikTok 캠페인 1", 액션="💵 예산 증액",
             검증가설="예산 증액이 학습 리셋 없이 볼륨을 늘리는가", 경과="D+14", 평가="❌ 실패"),
    ])
    flt = st.radio("필터", ["🟡 진행 중", "🟢 완료", "🔴 실패", "📋 전체"], horizontal=True, index=3, key="ab_filter")
    _fm = {"🟡 진행 중": "🟡 진행중", "🟢 완료": "🟢 성공", "🔴 실패": "🔴 실패"}
    actsf = acts if flt == "📋 전체" else acts[acts["상태"] == _fm[flt]]
    st.markdown(f"#### {flt} ({len(actsf)}건)")
    st.dataframe(actsf, use_container_width=True, hide_index=True)

    st.markdown("##### 🔬 테스트 선택 → 검증 가설 · 성과 조회")
    camp = st.selectbox("테스트(캠페인) 선택", sorted(df.campaign.unique()), key="ab_camp")

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
    m[2].metric("최근 7일 spend", won(rec.spend.sum()), f"{sp_pct:+.0f}%")
    m[3].metric("최근 7일 전환", f"{int(rec.real_conv.sum()):,}건", f"{cv_pct:+.0f}%")

    st.markdown("**📈 액션 이후 성과 추이**")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**일별 spend / cv**")
        f = go.Figure()
        f.add_bar(x=cd.date, y=cd.spend, name="spend", marker_color=ACCENT, hovertemplate="비용 %{y:,}원<extra></extra>")
        f.add_trace(go.Scatter(x=cd.date, y=cd.real_conv * (cd.spend.max() / max(1, cd.real_conv.max())),
                               customdata=cd.real_conv, name="cv", line=dict(color=RED, width=2.5), mode="lines+markers",
                               hovertemplate="전환 %{customdata:,}건<extra></extra>"))
        f.update_xaxes(tickformat="%-m월 %-d일"); st.plotly_chart(chart(f, 300), use_container_width=True)
    with g2:
        st.markdown("**CPA 추이**")
        f = go.Figure()
        f.add_trace(go.Scatter(x=cd.date, y=cd.real_cpa, name="실CPA", line=dict(color=GREEN, width=2), mode="lines+markers"))
        if baseline:
            f.add_hline(y=baseline, line_dash="dash", line_color=MUTED, annotation_text="baseline")
        f.update_xaxes(tickformat="%-m월 %-d일"); st.plotly_chart(chart(f, 300), use_container_width=True)

    st.markdown("**📋 운영 일자별 성과**")
    cd2 = cd.sort_values("date", ascending=False)
    cddisp = pd.DataFrame({
        "날짜": cd2.date.dt.strftime("%-m월 %-d일"), "소진비용": cd2.spend.map(won),
        "노출": cd2.impressions.map(lambda x: f"{int(x):,}"), "CPM": cd2.CPM.map(won),
        "클릭": cd2.clicks.map(lambda x: f"{int(x):,}"), "CTR(%)": cd2.CTR.map(lambda x: f"{x:.2f}"),
        "CPC": cd2.CPC.map(won), "전환(실제)": cd2.real_conv.map(lambda x: f"{int(x):,}"),
        "CVR(%)": cd2.CVR.map(lambda x: f"{x:.2f}"), "CPA(실제)": cd2.real_cpa.map(lambda x: won(x) if x else "-")})
    _allcols = [c for c in cddisp.columns if c != "날짜"]
    _selcols = st.multiselect("표시 지표 (비우면 전체)", _allcols, default=[], key="ab_dcols",
                              help="CPM·CTR 등 보고 싶은 지표만 골라서 볼 수 있습니다")
    _show = ["날짜"] + (_selcols if _selcols else _allcols)
    st.dataframe(cddisp[_show], use_container_width=True, hide_index=True, height=360)

    st.markdown("**📝 평가**")
    _evd = (TODAY + pd.Timedelta(days=7)).strftime("%-m월 %-d일")
    st.caption(f"⏱ 기본 **+7일 후 평가 진행** (예정일: {_evd}). 학습이 더 필요하면 '평가 연장'으로 일자를 미룰 수 있습니다.")
    st.text_area("평가 메모", placeholder="이 액션의 결과·판단을 기록하세요 (예: D+9 실CPA -26%, 성공적 풀 확장 → 유지)",
                 key="ab_memo", label_visibility="collapsed", height=90)
    _bc1, _bc2 = st.columns(2)
    _bc1.button("💾 평가 저장", key="ab_save", use_container_width=True)
    if _bc2.button("⏱ 평가 연장", key="ab_extend", use_container_width=True):
        st.session_state["ab_ext"] = True
    if st.session_state.get("ab_ext"):
        _nd = st.date_input("연장할 평가일 선택", value=(TODAY + pd.Timedelta(days=14)).date(),
                            min_value=(TODAY + pd.Timedelta(days=1)).date(), key="ab_extdate")
        if st.button("✅ 연장 저장", key="ab_extsave", use_container_width=True):
            st.session_state["ab_ext_saved"] = _nd.strftime("%-m월 %-d일")
        if st.session_state.get("ab_ext_saved"):
            st.success(f"평가일이 **{st.session_state['ab_ext_saved']}** 로 연장 저장되었습니다. (기존 {_evd} → 연장)")
        else:
            st.caption("날짜를 선택한 뒤 **연장 저장**을 눌러야 최종 반영됩니다.")

# ============================================================
# 5) 🆕 신규소재
# ============================================================
elif active == TAB_NAMES[3]:
    st.markdown("### 🆕 신규 소재 D+4 모니터링")
    st.caption("첫 노출일이 21일 이내인 광고 자동 감지. D+0~D+3 학습 페이즈 관망 → D+4부터 본인 CPA × 기존 회복 진단.")
    st.button("🔄 신규 소재 API 조회", type="primary", key="new_scan")
    assets = [
        dict(camp="Google Ads 캠페인 1", channel="google", ad_id="358968686309", d=9, cpa=31200, pre=42000, post=38500, rec=True),
        dict(camp="Google Ads 캠페인 2", channel="google", ad_id="365020929439", d=5, cpa=46800, pre=39000, post=44500, rec=False),
        dict(camp="Meta 캠페인 1", channel="meta", adset="광고세트 1", ad="공감형 영상 A", d=2, cpa=35400, pre=41000, post=40200, rec=True),
        dict(camp="TikTok 캠페인 1", channel="tiktok", adset="광고세트 1", ad="양심소개 영상", d=4, cpa=38900, pre=43000, post=40500, rec=True),
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
            if a["channel"] in ("meta", "tiktok"):
                h1.caption(f"광고세트: **{a['adset']}** · 소재: **{a['ad']}**")
            else:
                h1.caption(f"소재 ad_id: `{a['ad_id']}` · YOUTUBE_VIDEO")
            badge = "🟢" if a["d"] < 4 else ("🟢" if a["rec"] else "🔴")
            h2.markdown(f"### {badge} D+{a['d']}")
            # 운영 기간 일자별 성과
            np.random.seed(abs(hash(a["camp"])) % (2 ** 31))
            _n = a["d"] + 1
            _rows = []
            for _i in range(_n):
                _dt = TODAY - pd.Timedelta(days=_n - 1 - _i)
                _clk = int(np.random.uniform(80, 320))
                _imp = int(_clk / np.random.uniform(0.008, 0.02))
                _rch = int(_imp * np.random.uniform(0.6, 0.85))
                _cv = max(1, int(_clk * np.random.uniform(2.0, 5.0) / 100))
                _sp = int(_cv * a["cpa"] * np.random.uniform(0.85, 1.2))
                _rows.append({"날짜": _dt.strftime("%-m월 %-d일"), "소진비용": won(_sp),
                              "노출": f"{_imp:,}", "CPM": won(_sp / _imp * 1000), "도달": f"{_rch:,}",
                              "CTR(%)": f"{_clk/_imp*100:.2f}", "CPC": won(_sp / _clk),
                              "CVR(%)": f"{_cv/_clk*100:.2f}", "CPA": won(_sp / _cv)})
            st.dataframe(pd.DataFrame(_rows), use_container_width=True, hide_index=True)

    st.markdown("#### 📈 신규 소재 CPA 추이 (D+0 → 현재)")
    _f = go.Figure()
    for a in assets:
        nd = a["d"] + 1
        series = [round(a["cpa"] * (1 + 0.012 * (a["d"] - x))) for x in range(nd)]
        _f.add_trace(go.Scatter(x=[f"D+{x}" for x in range(nd)], y=series, mode="lines+markers", name=a.get("ad_id") or a.get("ad")))
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

    st.markdown("#### 📈 월 DB 중복률 추이")
    np.random.seed(110)
    ndays = (pd.Timestamp(TODAY.year, TODAY.month, 1) + pd.offsets.MonthEnd(1)).day  # 해당월 마지막 날(6월=30)
    _blk = int(ndays * 0.4)                                                          # 차단 적용 시점
    trend = [round(max(8, 23 - (0 if x < _blk else (x - _blk) / (ndays - _blk) * 8) + np.random.uniform(-1.2, 1.2)), 1) for x in range(ndays)]
    _f = go.Figure()
    _f.add_trace(go.Scatter(x=list(range(1, ndays + 1)), y=trend, mode="lines", line=dict(color=ACCENT, width=2.5),
                            fill="tozeroy", fillcolor="rgba(99,102,241,0.12)"))
    _f.add_vline(x=_blk, line_dash="dash", line_color=RED, annotation_text="차단 적용")
    _f.update_xaxes(range=[0.5, ndays + 0.5], dtick=5, title="일")
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

    _gcamps = sorted(df[df.channel == "Google Ads"].campaign.unique())
    _sel = st.selectbox("캠페인 선택", ["전체(합산)"] + _gcamps, key="yt_camp",
                        help="YouTube 노출 채널은 Google Ads 디멘드젠 캠페인에만 존재합니다 (메타·틱톡 광고세트는 채널 개념 없음)")
    st.caption("ℹ️ 광고세트(메타·틱톡) 단위로는 노출 채널을 볼 수 없어, **캠페인 단위로** 비교합니다.")
    _is_all = _sel == "전체(합산)"

    # 일별 채널 수 가상 시계열 (총 노출 / 신규 유입 / 전환 우수) — 캠페인별로 분리
    np.random.seed(21 if _is_all else 21 + _gcamps.index(_sel) + 1)
    _d0 = df["date"].min(); _ndays = (TODAY - _d0).days + 1
    _tot = 120 if _is_all else max(30, int(120 / max(1, len(_gcamps)) * np.random.uniform(0.9, 1.4)))
    _yrows = []
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
        f.update_xaxes(tickformat="%-m월 %-d일"); st.plotly_chart(chart(f, 340), use_container_width=True)
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
        k[0].metric("총 노출 채널", f"{bt:,}개", f"{bt-at:+,} vs A")
        k[1].metric("신규 유입 채널", f"{bn:,}개", f"{bn-an:+,} vs A")
        k[2].metric("전환 우수 채널 유지", f"{bg:,}개", f"{bg-ag:+,} vs A")
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

    st.markdown("#### 🔔 LP 변경 감지 (콘텐츠 해시 기반)")
    st.caption("경쟁사 LP의 가격·메인 훅·CTA·폼 텍스트를 추출 → **SHA-256 해시로 지문 생성** → 매일 직전 스냅샷 해시와 비교해 "
               "값이 달라지면 '변경'으로 감지합니다. (※ 노출 점유율 같은 경쟁사 내부 광고 데이터는 스크래핑으로 알 수 없어 다루지 않습니다.)")
    k = st.columns(3)
    k[0].metric("모니터링 경쟁사 LP", "3개")
    k[1].metric("최근 24h 변경 감지", "1건", "경쟁사 A", delta_color="off")
    k[2].metric("감지 방식", "SHA-256 해시 비교")

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

# ============================================================
# 9) 📊 코호트 (지역별 CPA 코호트)
# ============================================================
elif active == TAB_NAMES[7]:
    st.markdown("### 📊 지역별 코호트 분석")
    # ── 코호트 지표 정의 ── 각 지표를 왜 넣었는지는 아래 selectbox 옆 설명/캡션 참조
    METRICS = {
        "CPA(원)":   dict(name="CPA",   suffix="원", title="CPA(원)",   worse_high=True,
                          fmt=lambda v: f"{round(v):,}",   tfmt=lambda v: f"{round(v/1000)}k", zf=",.0f",
                          why="캠페인이 '언제부터 비싸지는가' — 효율의 결과 지표. 단독으론 원인을 못 봐서 중복DB율과 함께 봅니다."),
        "중복DB율(%)": dict(name="중복DB율", suffix="%", title="중복DB율(%)", worse_high=True,
                          fmt=lambda v: f"{round(v)}%",   tfmt=lambda v: f"{round(v)}%", zf=",.0f",
                          why="풀 소진(pool exhaustion)의 결정 신호 = 캠페인 수명. 같은 전화번호가 다시 들어오기 시작 = ML이 같은 오디언스를 재타격 = 새 잠재고객 고갈. 주차가 갈수록 우상향하면 그 캠페인은 수명 끝물 → 재세팅 트리거."),
        "CVR(%)":   dict(name="CVR",   suffix="%", title="CVR(%)",   worse_high=False,
                          fmt=lambda v: f"{v:.1f}%",      tfmt=lambda v: f"{v:.1f}", zf=",.1f",
                          why="풀의 '질'. 중복이 늘기 전에 먼저 빠지는 선행 지표 — 같은 사람에게 또 보여줘서 반응이 떨어지는 단계. CVR↓ → 중복↑ → CPA↑ 순서로 무너집니다."),
        "노출":      dict(name="노출",  suffix="회", title="노출(회)", worse_high=False,
                          fmt=lambda v: f"{round(v):,}",  tfmt=lambda v: f"{round(v/1000)}k", zf=",.0f",
                          why="풀 크기·소진 속도. 후반 주차에 노출이 줄어들면 ML이 더 보여줄 신규 유저가 없다는 뜻 = 풀 바닥. 중복DB율 상승과 짝지어 봅니다."),
    }
    _ms1, _ms2 = st.columns([1, 2])
    msel = _ms1.selectbox("📊 코호트 지표", list(METRICS), index=0, key="coh_metric")
    mc = METRICS[msel]
    _ms2.caption(f"💡 **왜 이 지표?** {mc['why']}")
    st.caption(f"세로축=캠페인(지역), 가로축=투입 후 경과 주차(W+0=시작), 셀={mc['name']} (옅을수록 좋음 → **진할수록 나쁨**). "
               "캠페인마다 시작일이 달라서 행을 시작 순으로 정렬 → **↙ 대각선(점선)이 '같은 달력 시점'** 으로, "
               "시즌·경쟁 같은 외부 영향을 읽을 수 있습니다.")
    def _cwlabel(cw):
        _d = date(2026, 1, 1) + timedelta(days=int(cw) * 7)
        return f"{_d.month}월 {(_d.day - 1) // 7 + 1}주차"
    camps = sorted(df.campaign.unique())
    starts = {c: i * 3 for i, c in enumerate(camps)}        # 시작 시차(가상): 0·3·6·9·12주
    LASTW = (TODAY - pd.Timestamp(2026, 1, 1)).days // 7     # 마지막 달력 주차(6월말까지)
    MAXW = LASTW - min(starts.values()) + 1                  # 최장 운영 캠페인 주차 수
    SEASON = 18                                              # 외부 이벤트(달력 18주차 ≈ 5월 초)
    weeks = [f"W+{w}" for w in range(MAXW)]
    np.random.seed(31)
    z, text, cal, bases = [], [], [], {}
    for c in camps:
        base = np.random.uniform(38000, 50000)              # 캠페인별 기본 CPA
        base_imp = np.random.uniform(45000, 80000)          # 캠페인별 기본 노출
        bases[c] = base
        s = starts[c]; last_w = LASTW - s
        row, crow = [], []
        for w in range(MAXW):
            cw = s + w                                  # 달력 주차
            if w <= last_w:
                cyc = w % 6                             # 6주 주기: 투입→W+1~3 안정→W+4~5 풀 소진→재투입
                season = 1.16 if cw == SEASON else 1.0  # 같은 달력 주차(대각선)에 외부 이벤트
                noise = np.random.uniform(0.96, 1.04)
                if msel == "CPA(원)":
                    factor = 1.0 - 0.06 * min(cyc, 3) + 0.05 * max(0, cyc - 3)
                    v = round(base * factor * season * noise)
                elif msel == "중복DB율(%)":               # 풀 소진: 주차 갈수록 우상향 (W+0 ~17% → 후반 40%+)
                    v = round(min(48, (17 + 1.4 * w + (4 if cw == SEASON else 0)) * noise))
                elif msel == "CVR(%)":                    # 풀 질: 주차 갈수록 하락
                    v = round(max(1.4, (5.2 - 0.13 * w - (0.6 if cw == SEASON else 0)) * noise), 1)
                else:                                     # 노출: 풀 바닥 가까울수록 감소
                    factor = 1.0 + 0.05 * min(cyc, 3) - 0.05 * max(0, cyc - 3) - 0.02 * w
                    v = round(base_imp * max(0.4, factor) / season * noise)
                row.append(v)
            else:
                row.append(None)                        # 미래(아직 운영 안 함)
            crow.append(cw)
        z.append(row); text.append([mc["tfmt"](v) if v is not None else "" for v in row]); cal.append(crow)

    cwavg = {}
    for ci, c in enumerate(camps):
        for w in range(MAXW):
            if z[ci][w] is not None:
                cwavg.setdefault(starts[c] + w, []).append(z[ci][w])
    cw_multi = [cw for cw in sorted(cwavg) if len(cwavg[cw]) >= 2]
    _mean = lambda cw: sum(cwavg[cw]) / len(cwavg[cw])
    if cw_multi:
        _best = (min if mc["worse_high"] else max)(cw_multi, key=_mean)   # 좋은 시기
        _worst = (max if mc["worse_high"] else min)(cw_multi, key=_mean)  # 나쁜 시기
    else:
        _best = _worst = None
    _cc1, _cc2, _cc3 = st.columns([2, 1, 1])
    show_bw = _cc2.checkbox("🏆 베스트·워스트 시기", key="coh_bw")
    show_all = _cc3.checkbox("전체 대각선", key="coh_all")
    _opts = [_cwlabel(cw) for cw in cw_multi]
    _di = cw_multi.index(SEASON) if SEASON in cw_multi else 0
    sel_cw = cw_multi[_opts.index(_cc1.selectbox("동일 시점(대각선) 선택", _opts, index=_di, key="coh_sel"))]

    def _diag(cw):
        _dx, _dy = [], []
        for ci, c in enumerate(camps):
            w = cw - starts[c]
            if 0 <= w < MAXW and z[ci][w] is not None:
                _dx.append(f"W+{w}"); _dy.append(c)
        return _dx, _dy

    fig = go.Figure(go.Heatmap(
        z=z, x=weeks, y=camps, customdata=[[_cwlabel(v) for v in row] for row in cal],
        colorscale=[[0, "rgba(99,102,241,0.06)"], [0.5, "rgba(99,102,241,0.5)"], [1, "rgba(99,102,241,1.0)"]],  # 단일 인디고 + 투명도
        reversescale=not mc["worse_high"],  # 좋은 지표(CVR·노출은 높을수록 좋음)는 반전 → '나쁠수록 진하게' 일관
        text=text, texttemplate="%{text}", textfont=dict(size=10, color="#fafafa"),
        hovertemplate="%{y} · %{x} · %{customdata}<br>" + mc["name"] + " %{z:" + mc["zf"] + "}" + mc["suffix"] + "<extra></extra>",
        colorbar=dict(title=mc["title"])))
    # 전체 대각선(옅게) — 모든 동일 시점
    if show_all:
        for _cw in cw_multi:
            _ax, _ay = _diag(_cw)
            if len(_ax) >= 2:
                fig.add_trace(go.Scatter(x=_ax, y=_ay, mode="lines", line=dict(color="rgba(34,211,238,0.22)", width=1),
                                         showlegend=False, hoverinfo="skip"))
    # 베스트(초록)·워스트(빨강) 시기 동시
    if show_bw and _best is not None:
        _bx, _by = _diag(_best)
        if len(_bx) >= 2:
            fig.add_trace(go.Scatter(x=_bx, y=_by, mode="lines+markers", line=dict(color=GREEN, width=2.5, dash="dot"),
                                     marker=dict(size=8, color=GREEN), name=f"🏆 베스트 {_cwlabel(_best)}"))
        _wx, _wy = _diag(_worst)
        if len(_wx) >= 2:
            fig.add_trace(go.Scatter(x=_wx, y=_wy, mode="lines+markers", line=dict(color=RED, width=2.5, dash="dot"),
                                     marker=dict(size=8, color=RED), name=f"⚠ 워스트 {_cwlabel(_worst)}"))
    # 선택 시점 대각선(강조)
    _sx, _sy = _diag(sel_cw)
    if len(_sx) >= 2:
        fig.add_trace(go.Scatter(x=_sx, y=_sy, mode="lines+markers",
                                 line=dict(color="#22d3ee", width=2.5, dash="dot"),
                                 marker=dict(size=8, color="#22d3ee"), name=f"{_cwlabel(sel_cw)} (선택 시점)"))
    fig.update_layout(font_family="sans-serif", font_color=TEXT, plot_bgcolor=CARD,
                      paper_bgcolor=CARD, height=460, margin=dict(l=10, r=10, t=20, b=10),
                      yaxis=dict(autorange="reversed"),
                      legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0))
    st.plotly_chart(fig, use_container_width=True)

    avg = {c: float(np.mean([v for v in z[i] if v is not None])) for i, c in enumerate(camps)}
    _good = (min if mc["worse_high"] else max)(avg.values())
    _bad = (max if mc["worse_high"] else min)(avg.values())
    k = st.columns(3)
    k[0].metric(f"🟢 가장 좋은 평균 {mc['name']}", mc["fmt"](_good))
    k[1].metric(f"🔴 가장 나쁜 평균 {mc['name']}", mc["fmt"](_bad))
    k[2].metric("🔴 외부 이벤트 시점", _cwlabel(SEASON), f"전 지역 {mc['name']} 악화")
    if msel == "중복DB율(%)":
        st.caption("• 가로(행) = **캠페인 수명** — 중복DB율이 W+0~몇 주차까지 낮게 유지되다 우상향하기 시작하면 그 지점이 '풀 소진 시작' = 재세팅 타이밍   "
                   "• 세로(열) = 같은 경과 주차 지역 비교 (어느 지역 풀이 빨리 마르는가)   "
                   "• ↙ 점선(대각선) = 같은 달력 주차 → 외부 이벤트(차단 해제·경쟁 유입 등)로 전 지역 중복 동반 상승")
    else:
        st.caption(f"• 가로(행) = 캠페인 생애주기(투입→안정→풀 소진)   "
                   f"• 세로(열) = 같은 경과 주차 지역 비교   "
                   f"• ↙ 점선(대각선) = 같은 달력 주차 → 외부 이벤트(여기선 {_cwlabel(SEASON)}에 전 지역 {mc['name']} 동반 악화)")

    st.markdown(f"#### 📈 시기성 — 달력 주차별 전 지역 평균 {mc['name']} (대각선을 직선으로 편 차트)")
    _cws = sorted(cwavg)
    _cavg = [round(sum(cwavg[k]) / len(cwavg[k]), 1) for k in _cws]
    lf = go.Figure()
    lf.add_trace(go.Scatter(x=[_cwlabel(k) for k in _cws], y=_cavg, mode="lines+markers",
                            line=dict(color=AMBER, width=2.5), fill="tozeroy", fillcolor="rgba(245,158,11,0.10)"))
    _ext = max(_cavg) if mc["worse_high"] else min(_cavg)   # 나쁜 쪽 극점
    _pk = _cws[_cavg.index(_ext)]
    lf.add_annotation(x=_cwlabel(_pk), y=_ext, text="외부 이벤트", showarrow=True, arrowhead=2, font=dict(color=AMBER))
    lf.update_yaxes(hoverformat=mc["zf"])
    st.plotly_chart(chart(lf, 260), use_container_width=True)
    st.caption(f"극점(뾰족한 지점) = 외부 이벤트 시점 = 히트맵 대각선이 진해지는({mc['name']} 악화) 지점. "
               "전 지역이 동시에 움직이면 개별 운영 실수가 아니라 시장 전체 이슈(명절·시즌·경쟁).")

    st.divider()
    st.markdown("#### 🔬 캠페인 수명 진단 — CVR · 중복DB율 · CPA 한눈에 겹쳐보기")
    st.caption("히트맵은 한 번에 한 지표만 보여줘서, 캠페인 하나를 골라 **세 지표를 겹쳐** 무너지는 순서와 풀 소진 변곡점을 같이 봅니다.")
    sel_camp = st.selectbox("캠페인(지역) 선택", camps, key="coh_life")
    _s = starts[sel_camp]; _lw = LASTW - _s; _bs = bases[sel_camp]
    _wx = [f"W+{w}" for w in range(_lw + 1)]
    _cvr, _dup, _cpa = [], [], []
    for w in range(_lw + 1):
        cw = _s + w; cyc = w % 6; season = 1.16 if cw == SEASON else 1.0
        _cpa.append(round(_bs * (1.0 - 0.06 * min(cyc, 3) + 0.05 * max(0, cyc - 3)) * season))
        _dup.append(round(min(48, 17 + 1.4 * w + (4 if cw == SEASON else 0))))
        _cvr.append(round(max(1.4, 5.2 - 0.13 * w - (0.6 if cw == SEASON else 0)), 1))
    lf2 = go.Figure()
    lf2.add_trace(go.Scatter(x=_wx, y=_cvr, name="CVR(%)", line=dict(color=GREEN, width=2.5), mode="lines+markers",
                             hovertemplate="%{x} · CVR %{y:.1f}%<extra></extra>"))
    lf2.add_trace(go.Scatter(x=_wx, y=_dup, name="중복DB율(%)", line=dict(color=AMBER, width=2.5), mode="lines+markers",
                             hovertemplate="%{x} · 중복 %{y:.0f}%<extra></extra>"))
    lf2.add_trace(go.Scatter(x=_wx, y=_cpa, name="CPA(원)", line=dict(color=ACCENT, width=2.5), mode="lines+markers",
                             yaxis="y2", hovertemplate="%{x} · CPA %{y:,}원<extra></extra>"))
    _warn = next((w for w in range(_lw + 1) if _dup[w] >= 30), None)   # 중복 30% 첫 돌파 = 풀 소진 경고
    if _warn is not None:
        lf2.add_annotation(x=f"W+{_warn}", y=_dup[_warn], text="중복 30% 돌파 (풀 소진 경고)",
                           showarrow=True, arrowhead=2, arrowcolor=RED, font=dict(color=RED))
    lf2.update_layout(font_family="sans-serif", font_color=TEXT, plot_bgcolor=CARD, paper_bgcolor=CARD,
                      height=330, margin=dict(l=10, r=10, t=20, b=10),
                      yaxis=dict(title="CVR · 중복DB율 (%)"),
                      yaxis2=dict(title="CPA(원)", overlaying="y", side="right", showgrid=False, hoverformat=",.0f"),
                      legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0))
    st.plotly_chart(lf2, use_container_width=True)
    st.caption("✅ 읽는 법: **CVR(초록)이 먼저 꺾이고 → 중복DB율(노랑)이 따라 오르고 → CPA(인디고)가 마지막에 치솟으면** 풀 소진 확정. "
               "빨간 점선(중복 30% 돌파) 전후가 재세팅 검토 구간입니다. (왼쪽 축 = %, 오른쪽 축 = CPA 원)")
