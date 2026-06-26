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
div[role="radiogroup"] {{ gap:18px; flex-wrap:nowrap; overflow-x:auto; border-bottom:1px solid {BORDER}; margin-bottom:18px; padding-bottom:0; }}
div[role="radiogroup"] > label {{ margin:0 !important; padding:0 2px 10px 2px; border-bottom:2px solid transparent; white-space:nowrap; flex:0 0 auto; }}
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
        is_h = (cr == "영상소재 C")  # 소재 C: CTR↑·CVR↓ 프로파일 (소재 다양성)
        bcvr = np.random.uniform(1.5, 3.2) * (0.5 if is_h else 1.0)
        bcpa = np.random.uniform(40000, 52000)
        q = np.random.uniform(.75, 1.3); broas = np.random.uniform(1.3, 1.8)
        for i, dt in enumerate(dates):
            t = i / (days - 1)
            cvr = bcvr * (1 + 1.3 * t) * np.random.uniform(.8, 1.2)
            cpa = bcpa * (1 - .45 * t) / q * np.random.uniform(.85, 1.15)
            clicks = int(np.random.uniform(70, 380) * q)
            impr = int(clicks / (np.random.uniform(.008, .02) * (1.9 if is_h else 1.0)))
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

# ============================================================
# 🗂 히스토리 챗봇 (데모 — 가상 변경이력 + 임의 답변, 실제 버전과 동일 UI)
# ============================================================
import html as _dh
import re as _dre
import streamlit.components.v1 as _dcomp

_DEMO_HISTORY = [
    {"d": "2026-06-29", "acc": "구글", "c": "Google Ads 캠페인 1", "s": "tCPA 변경 (45,000→42,000원)"},
    {"d": "2026-06-29", "acc": "구글", "c": "Google Ads 캠페인 1", "s": "소재(영상) 교체 ×2"},
    {"d": "2026-06-29", "acc": "메타", "c": "Meta 캠페인 2", "s": "신규 소재 2개 추가"},
    {"d": "2026-06-28", "acc": "구글", "c": "Google Ads 캠페인 2", "s": "일예산 증액 (80만→120만)"},
    {"d": "2026-06-28", "acc": "메타", "c": "Meta 캠페인 1", "s": "유사타겟 6%→4% 변경"},
    {"d": "2026-06-27", "acc": "구글", "c": "Google Ads 캠페인 2", "s": "캠페인 재세팅 (구 OFF→신규 ON)"},
    {"d": "2026-06-27", "acc": "틱톡", "c": "TikTok 캠페인 1", "s": "광고세트 신설 (지역 분리)"},
    {"d": "2026-06-26", "acc": "구글", "c": "Google Ads 캠페인 1", "s": "새벽 시간대(0~5시) OFF 적용"},
    {"d": "2026-06-25", "acc": "메타", "c": "Meta 캠페인 2", "s": "랜딩페이지(LP) v3 교체"},
    {"d": "2026-06-24", "acc": "틱톡", "c": "TikTok 캠페인 1", "s": "앵커 소재 교체"},
    {"d": "2026-06-24", "acc": "구글", "c": "Google Ads 캠페인 2", "s": "관심사 오디언스 추가"},
]
_DEMO_HYPO = [
    {"n": "학습 페이즈 무변경 원칙", "d": "예산·입찰 변경 후 7~14일은 추가 변경 자제. ML 재학습 중 변경은 학습을 리셋시켜 CPA가 출렁인다."},
    {"n": "신규 소재 = 추가 아닌 교체", "d": "소재를 무한정 추가하면 학습이 분산된다. 4~5개를 유지하며 약한 소재만 신규로 교체하는 게 전환 효율 최적."},
    {"n": "유사타겟 4% vs 6%", "d": "넓은 6%는 CPM이 싸 볼륨 확장에 유리, 좁은 4%는 CTR이 높지만 CVR 우위로 이어지지 않음. A/B 후 유의차 없으면 6%로 통합."},
    {"n": "캠페인 재세팅 = ML 리트레이닝", "d": "정점 후 9일 단조 하락(학습 사이클 쇠퇴) 시 구 캠페인 OFF→신규 ON 클린 핸드오프. 재세팅 직후 D+3 정점, D+14 약화 주기."},
    {"n": "새벽 시간대 OFF 기준", "d": "14일 합산 시간대별 CPA로 판단. 단일 일자로 OFF 금지. 새벽 0~5시는 캠페인별 CPA 편차가 커 분리 판단이 필요하다."},
    {"n": "LP 교체 효과는 단독 변경으로만 측정", "d": "LP만 바꿔야 효과를 분리할 수 있다. tCPA·예산과 같은 날 묶으면 측정이 불가능해진다."},
]


def _demo_dates(text):
    out = set()
    for mo, d in _dre.findall(r"(\d{1,2})[/.](\d{1,2})", text):
        out.add(f"2026-{int(mo):02d}-{int(d):02d}")
    for mo, d in _dre.findall(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", text):
        out.add(f"2026-{int(mo):02d}-{int(d):02d}")
    if "오늘" in text:
        out.add("2026-06-29")
    if "어제" in text:
        out.add("2026-06-28")
    if "그제" in text or "엊그제" in text:
        out.add("2026-06-27")
    return out


def _demo_answer(q):
    qd = _demo_dates(q)
    ql = q.lower()
    # 팀원이 챗봇으로 저장한 내용(가상 구글시트) + 기본 가상 이력 병합 (저장분이 최신)
    _saved = st.session_state.get("dcmo_saved", [])
    _srows = [{"d": s["d"], "acc": s["acc"], "c": s["c"],
               "s": (f"{s['action']} — {s['key']}" if s.get("key") else s["action"]),
               "who": s.get("who", ""), "hypo": s.get("hypo", "")} for s in _saved]
    rows = _srows + [dict(r, who="", hypo="") for r in _DEMO_HISTORY]
    if qd:
        rows = [r for r in rows if r["d"] in qd]
    if "구글" in q or "google" in ql:
        rows = [r for r in rows if r["acc"] == "구글"] or rows
    elif "메타" in q or "meta" in ql or "페이스북" in q:
        rows = [r for r in rows if r["acc"] == "메타"] or rows
    elif "틱톡" in q or "tiktok" in ql:
        rows = [r for r in rows if r["acc"] == "틱톡"] or rows
    out = [f"**📋 변경 이력** · {', '.join(sorted(qd))}" if qd else "**📋 최근 변경 이력**"]
    if rows:
        for r in rows[:15]:
            _who = f" `✍{r['who']}`" if r.get("who") else ""
            out.append(f"- **{r['d']}** `{r['acc']}` {r['c']} — {r['s']}{_who}")
    else:
        out.append("_해당 날짜의 변경 이력이 없습니다._")
    # 팀원이 저장한 가설 + 기본 가설
    _team = [{"n": f"[{s['who']}] {s['c']}", "d": s["hypo"]} for s in _saved if s.get("hypo")]
    kws = [w for w in _dre.findall(r"[가-힣A-Za-z0-9]{2,}", q)
           if w not in ("뭐했어", "했어", "알려줘", "히스토리", "내역", "변경", "구글애즈", "세팅", "수정", "액션")]
    rel = [h for h in _DEMO_HYPO if any(k in (h["n"] + h["d"]) for k in kws)] if kws else []
    if not rel:
        rel = _DEMO_HYPO[:3]
    out.append("\n**💡 관련 가설·이유**")
    for h in (_team[:2] + rel)[:5]:
        out.append(f"- **{h['n']}** — {h['d']}")
    out.append("\n› (데모: 가상 데이터 기반 예시 답변입니다)")
    return "\n".join(out)


@st.fragment
def _render_demo_chatbot():
    _min = st.session_state.get("dcmo_min", False)
    _full = st.session_state.get("dcmo_full", False)
    _pw = "260px" if _min else ("82vw" if _full else "400px")
    _ih = 620 if _full else 430
    st.markdown(f"""<style>
    .st-key-dcmo {{ position:fixed !important; right:16px; bottom:16px; width:{_pw}; max-width:calc(100vw - 32px);
        overflow:visible; box-sizing:border-box;
        background:#fff; border:1px solid rgba(0,0,0,.18); border-radius:14px;
        box-shadow:0 8px 30px rgba(0,0,0,.45); padding:4px 14px 10px; z-index:999999; }}
    .st-key-dcmo [data-testid="stHorizontalBlock"] {{ gap:8px !important; flex-wrap:nowrap !important; }}
    .st-key-dcmo [data-testid="stHorizontalBlock"] > div {{ min-width:0 !important; }}
    .st-key-dcmo [data-testid="stCaptionContainer"] * {{ color:#6b7280 !important; }}
    .st-key-dcmo [data-testid="stMarkdownContainer"] * {{ color:#1a1a1a !important; }}
    .st-key-dcmo button {{ background:#eef0f4 !important; color:#1a1a1a !important;
        border:1px solid #c8ccd4 !important; border-radius:8px !important;
        display:flex !important; align-items:center !important; justify-content:center !important; }}
    .st-key-dcmo button > div, .st-key-dcmo button [data-testid="stMarkdownContainer"] {{
        display:flex !important; align-items:center !important; justify-content:center !important; width:100% !important; }}
    .st-key-dcmo button p {{ margin:0 !important; padding:0 !important; line-height:1 !important; text-align:center !important; }}
    .st-key-dcmo button:hover {{ background:#e2e6ec !important; }}
    .st-key-dcmo [data-testid="stTextInput"] input {{ background:#fff !important; color:#1a1a1a !important;
        -webkit-text-fill-color:#1a1a1a !important; border:1px solid #d0d4dc !important; }}
    .st-key-dcmo [data-testid="stTextInput"] input::placeholder {{ color:#9aa0a6 !important; -webkit-text-fill-color:#9aa0a6 !important; }}
    .st-key-dcmo [data-testid="stForm"] {{ border-top:1px solid #eef0f4; padding-top:6px; }}
    </style>""", unsafe_allow_html=True)

    def _md(t):
        t = _dh.escape(t)
        t = _dre.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = _dre.sub(r"`(.+?)`", r"<code>\1</code>", t)
        o = []
        for ln in t.split("\n"):
            s = ln.strip()
            if s.startswith("- "):
                o.append(f'<div class="li">• {s[2:]}</div>')
            elif s:
                o.append(f"<div>{ln}</div>")
            else:
                o.append('<div style="height:5px;"></div>')
        return "".join(o)

    if "dcmo_hist" not in st.session_state:
        st.session_state["dcmo_hist"] = []

    _mode = st.session_state.get("dcmo_mode", "chat")
    with st.container(key="dcmo"):
        if _min:
            h1, h4 = st.columns([5, 1.4])
            with h1:
                st.markdown("**🗂 히스토리 챗봇**")
            with h4:
                if st.button("➕", key="dcmo_tg", help="펼치기"):
                    st.session_state["dcmo_min"] = False
                    st.rerun(scope="fragment")
        else:
            h1, h2, h3, h4 = st.columns([4.4, 1, 1, 1])
            with h1:
                st.markdown("**🗂 히스토리 챗봇**")
            with h2:
                if st.button("📝" if _mode == "chat" else "💬", key="dcmo_mode_b", help="저장/조회 전환"):
                    st.session_state["dcmo_mode"] = "save" if _mode == "chat" else "chat"
                    st.rerun(scope="fragment")
            with h3:
                if st.button("⛶", key="dcmo_full_b", help="전체창"):
                    st.session_state["dcmo_full"] = not _full
                    st.rerun(scope="fragment")
            with h4:
                if st.button("—", key="dcmo_tg", help="최소화"):
                    st.session_state["dcmo_min"] = True
                    st.rerun(scope="fragment")

        # ── 저장 모드: 정형 폼 → 가상 구글시트 저장 (누가/언제/매체/액션/핵심/가설) ──
        if (not _min) and _mode == "save":
            st.caption("📤 가설·액션 저장 → 구글시트 (팀 공유 · 데모)")
            with st.form("dcmo_save", clear_on_submit=True, border=False):
                _w = st.selectbox("작성자", ["김마케터", "이퍼포먼스", "박CMO", "최운영"], key="dcmo_w")
                _cc1, _cc2 = st.columns(2)
                _sd = _cc1.date_input("날짜", value=TODAY, key="dcmo_sd")
                _sacc = _cc2.selectbox("매체", ["구글", "메타", "틱톡"], key="dcmo_sacc")
                _scamp = st.text_input("캠페인", placeholder="예: Google Ads 캠페인 1", key="dcmo_scamp")
                _saction = st.selectbox(
                    "액션 유형 (없으면 직접 입력)",
                    ["예산 변경", "tCPA 변경", "입찰전략 변경", "소재 교체", "소재 추가",
                     "소재 OFF", "캠페인 신설", "캠페인 재세팅", "캠페인 OFF", "광고그룹 변경",
                     "오디언스/관심사 변경", "타겟 지역 변경", "연령 타겟 변경", "LP(랜딩) 변경",
                     "시간대 조정", "빈도캡 설정", "차단(IP/전화)", "키워드 변경", "예산 재배분"],
                    index=None, accept_new_options=True, key="dcmo_sact",
                    placeholder="목록에서 선택하거나 직접 입력…")
                _skey = st.text_input("핵심 내용 (한 줄 요약) *",
                    placeholder="예: tCPA 45,000→42,000원 인하", key="dcmo_skey")
                _shypo = st.text_area("가설 — 왜 이 액션을 했나",
                    placeholder="예: 입찰제약으로 미소진 → tCPA 올려 볼륨 확보", key="dcmo_shypo")
                _save = st.form_submit_button("📤 구글시트에 저장", use_container_width=True)
            if _save:
                if _scamp.strip() and _skey.strip():
                    st.session_state.setdefault("dcmo_saved", []).insert(0, {
                        "who": _w, "d": str(_sd), "acc": _sacc, "c": _scamp.strip(),
                        "action": (_saction or "기타"), "key": _skey.strip(), "hypo": _shypo.strip()})
                    st.toast("✅ **저장되었습니다**  \n📄 구글시트: 마케팅 1팀 광고 운영 히스토리",
                             icon="📥")
                else:
                    st.warning("‘캠페인’과 ‘핵심 내용’은 필수입니다.")
            _sv = st.session_state.get("dcmo_saved", [])
            if _sv:
                st.caption(f"📥 가상 시트 누적 {len(_sv)}건 · 최근:")
                for _e in _sv[:4]:
                    st.markdown(
                        f"<div style='font-size:12.5px;color:#444;'>• <b>{_e['d']}</b> "
                        f"[{_e['acc']}] {_e['c']} — {_e['action']}: {_e['key']} "
                        f"<span style='color:#2b6cff;'>✍{_e['who']}</span></div>",
                        unsafe_allow_html=True)

        if (not _min) and _mode == "chat":
            st.caption("구글애즈·메타·틱톡 변경 히스토리 조회 · 저장은 📝 (데모)")
            _hist = st.session_state["dcmo_hist"]
            if _hist:
                _rows = ""
                for r, t in _hist[-40:]:
                    cc = "u" if r == "user" else "b"
                    _rows += f'<div class="row {cc}"><span class="bub {cc}">{_md(t)}</span></div>'
            else:
                _rows = ('<div class="empty">예) <b>구글애즈 6/29일에 세팅 수정한 히스토리 알려줘</b><br><br>'
                         '· 어제 뭐했어<br>· 메타 뭐 바꿨어<br>· 6/27 액션</div>')
            _chat = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
              body{{margin:0;font-family:-apple-system,system-ui,'Apple SD Gothic Neo',sans-serif;}}
              #c{{height:{_ih}px;overflow-y:auto;padding:10px 6px;box-sizing:border-box;background:#fff;}}
              .row{{margin:7px 0;display:flex;}} .row.u{{justify-content:flex-end;}} .row.b{{justify-content:flex-start;}}
              .bub{{max-width:84%;padding:8px 12px;border-radius:14px;font-size:14px;line-height:1.55;word-break:break-word;}}
              .bub.u{{background:#2b6cff;color:#fff;border-radius:14px 14px 3px 14px;}}
              .bub.b{{background:#f1f3f5;color:#1a1a1a;border-radius:14px 14px 14px 3px;}}
              .bub b{{font-weight:700;}} .li{{margin:2px 0;}}
              code{{background:#e6eaf0;padding:1px 5px;border-radius:4px;font-size:13px;}}
              .empty{{color:#8a909a;font-size:13px;padding:16px 10px;line-height:1.9;}}
            </style></head><body><div id="c">{_rows}</div>
            <script>var c=document.getElementById("c");c.scrollTop=c.scrollHeight;</script></body></html>"""
            _dcomp.html(_chat, height=_ih + 6, scrolling=False)

            with st.form("dcmo_form", clear_on_submit=True, border=False):
                ci, cb = st.columns([5, 1])
                with ci:
                    uq = st.text_input("질문", key="dcmo_q", label_visibility="collapsed",
                                       placeholder="예: 구글애즈 6/29 세팅 수정 히스토리 알려줘")
                with cb:
                    sb = st.form_submit_button("➤", use_container_width=True)
            if sb and uq and uq.strip():
                _hist.append(("user", uq.strip()))
                _hist.append(("assistant", _demo_answer(uq.strip())))
                st.rerun(scope="fragment")
            if _hist and st.button("🗑 대화 초기화", key="dcmo_clr"):
                st.session_state["dcmo_hist"] = []
                st.rerun(scope="fragment")

    _dcomp.html("""<script>(function(){
      const doc=window.parent.document;
      function init(){const p=doc.querySelector('.st-key-dcmo'); if(!p){setTimeout(init,400);return;}
        try{const s=JSON.parse(sessionStorage.getItem('dcmoPos')||'null');
          if(s){p.style.left=s.left;p.style.top=s.top;p.style.right='auto';p.style.bottom='auto';}}catch(e){}
        if(p.dataset.dr==='1')return; p.dataset.dr='1';
        let dg=false,sx,sy,ox,oy;
        p.addEventListener('mousedown',function(e){if(e.target.closest('button,input,textarea,iframe,a'))return;
          dg=true;const r=p.getBoundingClientRect();ox=r.left;oy=r.top;sx=e.clientX;sy=e.clientY;
          p.style.right='auto';p.style.bottom='auto';p.style.left=ox+'px';p.style.top=oy+'px';e.preventDefault();});
        doc.addEventListener('mousemove',function(e){if(!dg)return;
          p.style.left=Math.max(0,Math.min(ox+e.clientX-sx,window.parent.innerWidth-80))+'px';
          p.style.top=Math.max(0,Math.min(oy+e.clientY-sy,window.parent.innerHeight-40))+'px';});
        doc.addEventListener('mouseup',function(){if(!dg)return;dg=false;
          try{sessionStorage.setItem('dcmoPos',JSON.stringify({left:p.style.left,top:p.style.top}));}catch(e){}});
      } init();})();</script>""", height=0)


_render_demo_chatbot()

# ── 모든 date_input 캘린더 팝업을 한글(월/요일)로 치환 ──
_dcomp.html("""<script>
(function(){
  var doc=window.parent.document;
  var M=[["January","1월"],["February","2월"],["March","3월"],["April","4월"],["May","5월"],
         ["June","6월"],["July","7월"],["August","8월"],["September","9월"],["October","10월"],
         ["November","11월"],["December","12월"]];
  var D=[["Sunday","일요일"],["Monday","월요일"],["Tuesday","화요일"],["Wednesday","수요일"],
         ["Thursday","목요일"],["Friday","금요일"],["Saturday","토요일"],
         ["Sun","일"],["Mon","월"],["Tue","화"],["Wed","수"],["Thu","목"],["Fri","금"],["Sat","토"],
         ["Su","일"],["Mo","월"],["Tu","화"],["We","수"],["Th","목"],["Fr","금"],["Sa","토"]];
  function fix(){
    var cal=doc.querySelector('[data-baseweb="calendar"]');
    if(!cal) return;
    var els=cal.querySelectorAll('*');
    for(var n=0;n<els.length;n++){
      var el=els[n];
      if(el.children.length===0 && el.textContent){
        var t=el.textContent, nt=t;
        for(var i=0;i<M.length;i++) nt=nt.split(M[i][0]).join(M[i][1]);
        var tr=t.trim();
        for(var j=0;j<D.length;j++){ if(tr===D[j][0]){ nt=D[j][1]; break; } }
        if(nt!==t) el.textContent=nt;
      }
    }
  }
  new MutationObserver(function(){ setTimeout(fix,15); }).observe(doc.body,{childList:true,subtree:true});
  fix();
})();
</script>""", height=0)

# ── 사이드바 ──
with st.sidebar:
    st.markdown('<div style="font-size:17px;font-weight:700;white-space:nowrap;margin:2px 0 6px;">📊 윤지욱 마케팅 대시보드</div>', unsafe_allow_html=True)
    st.caption("캠페인 성과 모니터링 + AI 시뮬레이션")
    st.button("⚡ API 데이터 동기화", type="primary", use_container_width=True, key="sync")
    st.caption(f"마지막 동기화: {TODAY.strftime('%Y-%m-%d')} 14:30")
    st.caption(f"데이터: {df['date'].min().strftime('%m/%d')} ~ {TODAY.strftime('%m/%d')}")

st.markdown("# 📊 윤지욱 마케팅 대시보드")
st.markdown('<div class="demo-banner">데모 버전 · 표시 수치는 모두 가상 데이터입니다 (실제 광고주 데이터 아님). '
            'Claude Code로 직접 개발한 실제 운영 대시보드의 데모입니다.</div>', unsafe_allow_html=True)

CHS = ["Google Ads", "Meta", "TikTok"]
TAB_NAMES = ["📊 실시간", "📅 일자별", "🎬 크리에이티브", "🔬 A/B", "🆕 신규소재", "🔁 중복DB", "📺 노출 유튜브 채널", "🔍 경쟁사 실시간 스크랩", "📊 코호트", "🎯 KPI"]
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

        st.markdown("##### 🔎 단계별 원인 추적 (캠페인 → 광고그룹 → 소재)")
        st.caption("캠페인을 고르면 그 안의 광고그룹이, 광고그룹을 고르면 그 안의 소재가 단계적으로 펼쳐집니다. 성과가 나빠진 지점을 한 단계씩 좁혀 찾으세요.")

        def _ddtbl(frame, gb, lbl):
            t = metrics(frame.groupby(gb, as_index=False)[["spend", "impressions", "clicks", "conversions", "revenue"]].sum()).sort_values("conversions", ascending=False)
            return pd.DataFrame({
                lbl: t[gb], "비용": t.spend.map(won),
                "노출": t.impressions.map(lambda x: f"{int(x):,}"), "클릭": t.clicks.map(lambda x: f"{int(x):,}"),
                "전환": t.conversions.map(lambda x: f"{int(x):,}"), "CPA": t.CPA.map(won),
                "CTR(%)": t.CTR.map(lambda x: f"{x:.2f}"), "CVR(%)": t.CVR.map(lambda x: f"{x:.2f}"),
                "ROAS(%)": t.ROAS.map(lambda x: f"{int(x):,}%")})

        # 1단계 · 캠페인
        st.markdown("**1단계 · 캠페인**")
        st.dataframe(_ddtbl(d, "campaign", "캠페인"), use_container_width=True, hide_index=True)
        camp_sel = st.multiselect("👉 조회할 캠페인 선택 (비우면 여기까지)", sorted(d.campaign.unique()), default=[], key="dd_camp")

        # 2단계 · 광고그룹 (선택한 캠페인 안)
        if camp_sel:
            d2 = d[d.campaign.isin(camp_sel)].copy()
            d2["_ag"] = d2.campaign + " · " + d2.adgroup
            st.markdown("**2단계 · 광고그룹** — 선택한 캠페인 내부")
            st.dataframe(_ddtbl(d2, "_ag", "광고그룹"), use_container_width=True, hide_index=True)
            ag_sel = st.multiselect("👉 조회할 광고그룹 선택 (비우면 여기까지)", sorted(d2["_ag"].unique()), default=[], key="dd_ag")

            # 3단계 · 소재 (선택한 광고그룹 안)
            if ag_sel:
                d3 = d2[d2["_ag"].isin(ag_sel)].copy()
                d3["_cr"] = d3.campaign + " · " + d3.adgroup + " · " + d3.creative.astype(str)
                st.markdown("**3단계 · 소재** — 선택한 광고그룹 내부")
                st.dataframe(_ddtbl(d3, "_cr", "소재"), use_container_width=True, hide_index=True)
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

        st.markdown("##### 🔎 단계별 원인 추적 A vs B (캠페인 → 광고그룹 → 소재)")
        st.caption("캠페인을 고르면 그 안의 광고그룹이, 광고그룹을 고르면 그 안의 소재가 단계적으로 펼쳐집니다. 전환 변화 ↑ / CPA 변화 ↓ 이면 개선.")

        # 1단계 · 캠페인
        st.markdown("**1단계 · 캠페인**")
        st.dataframe(_cmp(A, B, "campaign", "캠페인"), use_container_width=True, hide_index=True)
        dc_camp = st.multiselect("👉 조회할 캠페인 선택 (비우면 여기까지)", sorted(set(A.campaign) | set(B.campaign)), default=[], key="dc_camp")

        # 2단계 · 광고그룹 (선택한 캠페인 안)
        if dc_camp:
            A2 = A[A.campaign.isin(dc_camp)].copy(); B2 = B[B.campaign.isin(dc_camp)].copy()
            A2["_ag"] = A2.campaign + " · " + A2.adgroup
            B2["_ag"] = B2.campaign + " · " + B2.adgroup
            st.markdown("**2단계 · 광고그룹** — 선택한 캠페인 내부")
            st.dataframe(_cmp(A2, B2, "_ag", "광고그룹"), use_container_width=True, hide_index=True)
            dc_ag = st.multiselect("👉 조회할 광고그룹 선택 (비우면 여기까지)", sorted(set(A2["_ag"]) | set(B2["_ag"])), default=[], key="dc_ag")

            # 3단계 · 소재 (선택한 광고그룹 안)
            if dc_ag:
                A3 = A2[A2["_ag"].isin(dc_ag)].copy(); B3 = B2[B2["_ag"].isin(dc_ag)].copy()
                A3["_cr"] = A3.campaign + " · " + A3.adgroup + " · " + A3.creative.astype(str)
                B3["_cr"] = B3.campaign + " · " + B3.adgroup + " · " + B3.creative.astype(str)
                st.markdown("**3단계 · 소재** — 선택한 광고그룹 내부")
                st.dataframe(_cmp(A3, B3, "_cr", "소재"), use_container_width=True, hide_index=True)

# ============================================================
# 2-2) 🎬 크리에이티브 (소재 분석)
# ============================================================
elif active == TAB_NAMES[2]:
    st.markdown("### 🎬 크리에이티브(소재) 분석")
    st.caption("영상 소재 중심 — 노출·도달·조회·CTR·CVR·CPA·CPM·CPC 등 다양한 지표 + 평균 시청 시간 + 피로도.")

    WATCH = {"영상소재 A": 7.2, "영상소재 B": 8.6, "영상소재 C": 11.4}  # 평균 시청 시간(초)
    VLEN = {"영상소재 A": 15, "영상소재 B": 15, "영상소재 C": 30}         # 영상 길이(초)
    VIEWR = {"영상소재 A": 0.30, "영상소재 B": 0.28, "영상소재 C": 0.42}  # 조회율(조회수/노출)
    FREQ = 1.3  # 빈도

    chsel = st.multiselect("📡 매체", CHS, default=CHS, key="cr_media")
    cmp_mode = st.checkbox("📊 기간 비교 모드 (A vs B)", key="cr_cmp")
    cch = df[df.channel.isin(chsel)].copy()
    cr_list = sorted(cch.creative.unique())

    def _kr2(x): return pd.Timestamp(x).strftime("%-m월 %-d일")

    def _enrich(frame):
        g = metrics(frame.groupby("creative", as_index=False)[["spend", "impressions", "clicks", "conversions", "revenue"]].sum())
        g["도달"] = (g.impressions / FREQ).round(0)
        g["조회수"] = (g.impressions * g.creative.map(VIEWR)).round(0)
        g["빈도"] = FREQ
        g["평균시청"] = g.creative.map(WATCH)
        g["완주율"] = (g.creative.map(WATCH) / g.creative.map(VLEN) * 100).round(0)
        return g

    # --- 기간 선택 ---
    if not cmp_mode:
        c1, c2 = st.columns([1, 1])
        quick = c1.selectbox("기간", ["최근 14일", "최근 30일", "최근 60일", "이번달", "직접 설정"], index=1, key="cr_quick")
        if quick == "직접 설정":
            rng = c2.date_input("직접 설정", value=(TODAY - pd.Timedelta(days=29), TODAY),
                                min_value=df.date.min(), max_value=TODAY, key="cr_range")
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                s, e = pd.Timestamp(rng[0]), pd.Timestamp(rng[1])
            else:
                _d0 = rng[0] if isinstance(rng, (list, tuple)) else rng; s = e = pd.Timestamp(_d0)
        elif quick == "이번달":
            s = TODAY.replace(day=1); e = TODAY; c2.caption(f"📅 {_kr2(s)} ~ {_kr2(e)}")
        else:
            _n = {"최근 14일": 14, "최근 30일": 30, "최근 60일": 60}[quick]
            s = TODAY - pd.Timedelta(days=_n - 1); e = TODAY; c2.caption(f"📅 {_kr2(s)} ~ {_kr2(e)}")
        cd = cch[(cch.date >= s) & (cch.date <= e)].copy()
        prev = cd; prevlabel = f"{_kr2(s)} ~ {_kr2(e)}"
    else:
        cc = st.columns(4)
        a1 = cc[0].date_input("기간 A 시작", value=TODAY - pd.Timedelta(days=59), min_value=df.date.min(), max_value=TODAY, key="cr_a1")
        a2 = cc[1].date_input("기간 A 종료", value=TODAY - pd.Timedelta(days=30), min_value=df.date.min(), max_value=TODAY, key="cr_a2")
        b1 = cc[2].date_input("기간 B 시작", value=TODAY - pd.Timedelta(days=29), min_value=df.date.min(), max_value=TODAY, key="cr_b1")
        b2 = cc[3].date_input("기간 B 종료", value=TODAY, min_value=df.date.min(), max_value=TODAY, key="cr_b2")
        A = cch[(cch.date >= pd.Timestamp(a1)) & (cch.date <= pd.Timestamp(a2))]
        B = cch[(cch.date >= pd.Timestamp(b1)) & (cch.date <= pd.Timestamp(b2))]
        st.caption(f"📅 기간 A: {_kr2(a1)} ~ {_kr2(a2)}   vs   기간 B: {_kr2(b1)} ~ {_kr2(b2)}")
        prev = B; prevlabel = f"기간 B {_kr2(b1)} ~ {_kr2(b2)}"

    # --- 소재 미리보기 (기준 지표 필터 + 🥇 1등) ---
    st.markdown(f"##### 소재 미리보기  ·  기준 기간 {prevlabel}")
    METRICS = {
        "전환": ("conversions", False, lambda v: f"{int(v):,}건"),
        "조회수": ("조회수", False, lambda v: f"{int(v):,}"),
        "노출": ("impressions", False, lambda v: f"{int(v):,}"),
        "도달": ("도달", False, lambda v: f"{int(v):,}"),
        "CTR": ("CTR", False, lambda v: f"{v:.2f}%"),
        "CVR": ("CVR", False, lambda v: f"{v:.2f}%"),
        "ROAS": ("ROAS", False, lambda v: f"{int(v):,}%"),
        "CPA": ("CPA", True, lambda v: won(v)),
        "CPC": ("CPC", True, lambda v: won(v)),
        "CPM": ("CPM", True, lambda v: won(v)),
    }
    msel = st.selectbox("기준 지표 (이 지표로 정렬 · 1등이 맨 앞)", list(METRICS), key="cr_rank")
    mcol, asc, fmtfn = METRICS[msel]
    AVGM = {"CPA", "CPC", "CPM", "CTR", "CVR", "ROAS"}
    _lab = ("평균 " if msel in AVGM else "") + msel
    pg = _enrich(prev).set_index("creative")
    ser = pg[mcol] if (len(pg) and mcol in pg.columns) else pd.Series(dtype=float)
    # 선택 지표 기준 정렬 — 1등이 맨 앞 (CPA·CPC·CPM 등 asc는 낮을수록, 데이터 없으면 뒤로)
    if len(ser):
        _o = ser.replace(0, np.inf).sort_values(ascending=True) if asc else ser.sort_values(ascending=False)
        ranked = [c for c in _o.index if c in cr_list]
    else:
        ranked = []
    ranked += [c for c in cr_list if c not in ranked]
    best_cr = ranked[0] if ranked else None

    pcols = st.columns(len(ranked))
    for col, cr in zip(pcols, ranked):
        val = float(ser.get(cr, 0)) if cr in ser.index else 0.0
        is_best = (cr == best_cr)
        bd = '<div style="position:absolute;top:8px;right:8px;background:#FFB020;color:#191f28;font-size:11px;font-weight:700;padding:2px 7px;border-radius:8px;">🥇 1등</div>' if is_best else ''
        bc = "#FFB020" if is_best else BORDER
        col.markdown(
            f'<div style="position:relative;background:linear-gradient(135deg,#3a4250,#161b22);'
            f'border-radius:12px;height:140px;display:flex;align-items:center;justify-content:center;'
            f'border:1px solid {bc};overflow:hidden;">{bd}'
            f'<div style="width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.16);'
            f'display:flex;align-items:center;justify-content:center;font-size:18px;color:#fff;">▶</div>'
            f'<div style="position:absolute;bottom:8px;left:10px;color:#e6e9ee;font-size:12px;"><b>{cr}</b></div>'
            f'</div>',
            unsafe_allow_html=True)
        col.markdown(f"<div style='text-align:center;font-weight:800;color:#e6e9ee;font-size:15px;margin-top:4px;'>{_lab} {fmtfn(val)}</div>", unsafe_allow_html=True)
        col.caption(f"{VLEN.get(cr,15)}초 · 평균시청 {WATCH.get(cr,8)}s")
    st.caption(f"※ 썸네일은 임시 이미지. '{msel}' 기준 정렬(1등 맨 앞 🥇). CPA·CPC·CPM은 낮을수록 우수.")

    if not cmp_mode:
        # ① 소재별 성과 (다양한 지표 + 표시 지표 선택)
        st.markdown("##### 소재별 성과")
        cg = _enrich(cd).sort_values("conversions", ascending=False)
        full = pd.DataFrame({
            "소재": cg.creative,
            "노출": cg.impressions.map(lambda x: f"{int(x):,}"),
            "도달": cg.도달.map(lambda x: f"{int(x):,}"),
            "빈도": cg.빈도.map(lambda x: f"{x:.1f}"),
            "조회수": cg.조회수.map(lambda x: f"{int(x):,}"),
            "클릭": cg.clicks.map(lambda x: f"{int(x):,}"),
            "CTR(%)": cg.CTR.map(lambda x: f"{x:.2f}"),
            "CPC": cg.CPC.map(won), "CPM": cg.CPM.map(won),
            "비용": cg.spend.map(won), "전환": cg.conversions.map(lambda x: f"{int(x):,}"),
            "CVR(%)": cg.CVR.map(lambda x: f"{x:.2f}"), "CPA": cg.CPA.map(won),
            "ROAS(%)": cg.ROAS.map(lambda x: f"{int(x):,}%"),
            "평균시청(초)": cg.평균시청, "완주율(%)": cg.완주율.astype(int)})
        allc = [c for c in full.columns if c != "소재"]
        sel = st.multiselect("표시 지표 (비우면 전체)", allc,
                             default=["노출", "조회수", "CTR(%)", "CPC", "CPM", "전환", "CVR(%)", "CPA", "ROAS(%)"], key="cr_cols")
        show = ["소재"] + (sel if sel else allc)
        st.dataframe(full[show], use_container_width=True, hide_index=True)

        # ② 일자별 소재 성과 (지표 선택 — 추이 + 피로도)
        st.markdown("##### 일자별 소재 성과")
        dmetric = st.selectbox("지표 선택", ["CTR", "전환", "조회수", "노출", "CPA", "CVR", "CPM", "CPC"], key="cr_daily")
        day = metrics(cd.groupby(["date", "creative"], as_index=False)[["spend", "impressions", "clicks", "conversions", "revenue"]].sum())
        day["조회수"] = (day.impressions * day.creative.map(VIEWR)).round(0)
        day["노출"] = day.impressions
        day["전환"] = day.conversions
        _dcol = dmetric  # 컬럼명 = 표시명 (전환/조회수/노출/CTR/CVR/CPA/CPC/CPM)
        f = go.Figure()
        for cr in cr_list:
            s = day[day.creative == cr].sort_values("date")
            f.add_trace(go.Scatter(x=s.date, y=s[_dcol], name=cr, mode="lines+markers"))
        f.update_xaxes(tickformat="%-m월 %-d일")
        f.update_yaxes(title_text=dmetric)  # 선택 지표를 작게 표기 (예: 전환)
        st.plotly_chart(chart(f, 340), use_container_width=True)
        _hint = "CTR이 추세적으로 하락하면 소재 피로도 신호 → 로테이션 검토." if dmetric == "CTR" else f"선택 기간 동안 소재별 '{dmetric}' 일자 추이."
        st.caption(f"{_hint} (단일 일자 변동은 노이즈)")
        with st.expander("📋 일자별 상세 표 (전체 지표 · 선택 지표 강조)", expanded=True):
            day["도달"] = (day.impressions / FREQ).round(0)
            dd = day.sort_values(["date", "creative"], ascending=[False, True])
            disp = pd.DataFrame({
                "날짜": dd.date.dt.strftime("%-m월 %-d일"), "소재": dd.creative,
                "노출": dd.impressions.astype(int), "도달": dd.도달.astype(int),
                "조회수": dd.조회수.astype(int), "클릭": dd.clicks.astype(int),
                "CTR(%)": dd.CTR.round(2), "CPC": dd.CPC.astype(int), "CPM": dd.CPM.astype(int),
                "비용": dd.spend.astype(int), "전환": dd.conversions.astype(int),
                "CVR(%)": dd.CVR.round(2), "CPA": dd.CPA.astype(int), "ROAS(%)": dd.ROAS.astype(int)})
            _hl = {"CTR": "CTR(%)", "전환": "전환", "조회수": "조회수", "노출": "노출",
                   "CPA": "CPA", "CVR": "CVR(%)", "CPM": "CPM", "CPC": "CPC"}.get(dmetric)
            if _hl and _hl in disp.columns:
                _sty = disp.style.set_properties(subset=[_hl], **{"background-color": "rgba(99,102,241,0.22)", "font-weight": "700"})
                st.dataframe(_sty, use_container_width=True, hide_index=True)
            else:
                st.dataframe(disp, use_container_width=True, hide_index=True)
            st.caption(f"조회 기간 전체 지표를 일자별로. 위에서 선택한 '{dmetric}' 열을 강조 표시.")
    else:
        def _m(frame):
            sp = frame.spend.sum(); im = frame.impressions.sum(); ck = frame.clicks.sum(); cv = frame.conversions.sum()
            return cv, (sp / cv if cv else 0), (cv / ck * 100 if ck else 0)
        st.markdown("##### 소재별 A vs B (전환·CPA·CVR 변화)")
        rows = []
        for cr in cr_list:
            acv, acpa, acvr = _m(A[A.creative == cr]); bcv, bcpa, bcvr = _m(B[B.creative == cr])
            rows.append({"소재": cr,
                         "A 전환": f"{int(acv):,}", "B 전환": f"{int(bcv):,}",
                         "전환 변화": (f"{(bcv/acv-1)*100:+.0f}%" if acv else "-"),
                         "A CPA": (won(acpa) if acpa else "-"), "B CPA": (won(bcpa) if bcpa else "-"),
                         "CPA 변화": (f"{(bcpa/acpa-1)*100:+.0f}%" if acpa else "-"),
                         "A CVR(%)": f"{acvr:.2f}", "B CVR(%)": f"{bcvr:.2f}"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("전환·CPA·CVR이 기간 A → B 사이 어떻게 바뀌었는지 소재별로 비교.")

# ============================================================
# 3) 🔬 A/B테스트
# ============================================================
elif active == TAB_NAMES[3]:
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
    st.markdown('<style>.st-key-abhc [data-testid="stColumn"]{align-self:stretch;}'
                '.st-key-abhc [data-testid="stColumn"]>div{height:100%;}'
                '.st-key-abhc [data-testid="stAlert"],.st-key-abhc [data-testid="stAlertContainer"]{height:100%;}</style>',
                unsafe_allow_html=True)
    with st.container(key="abhc"):
        ca, cb = st.columns(2)
        ca.info(f"**💡 가설**\n\n{hyp}")
        cb.success(f"**🎬 액션**\n\n{act}")

    # 🎬 소재 미리보기 (선택 테스트의 소재 — 임시 썸네일)
    st.markdown("##### 🎬 투입 소재 미리보기")
    _camp_cr = sorted(df[df.campaign == camp].creative.unique())
    _ncols = st.columns(max(1, len(_camp_cr)))
    for _col, _cr in zip(_ncols, _camp_cr):
        _col.markdown(
            f'<div style="position:relative;background:linear-gradient(135deg,#3a4250,#161b22);'
            f'border-radius:12px;height:140px;display:flex;align-items:center;justify-content:center;'
            f'border:1px solid {BORDER};overflow:hidden;">'
            f'<div style="width:46px;height:46px;border-radius:50%;background:rgba(255,255,255,.16);'
            f'display:flex;align-items:center;justify-content:center;font-size:19px;color:#fff;">▶</div>'
            f'<div style="position:absolute;bottom:8px;left:10px;color:#e6e9ee;font-size:12px;">'
            f'<b>{_cr}</b></div></div>',
            unsafe_allow_html=True)
    st.caption("※ 썸네일은 데모용 임시 이미지입니다.")

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
elif active == TAB_NAMES[4]:
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
elif active == TAB_NAMES[5]:
    st.markdown("### 🔁 월간 중복DB 현황")
    st.caption("해당월 전체 DB에서 연락처 중복 측정. 첫 등장은 unique, 이후 등장은 중복으로 카운트.")
    c1, c2, c3 = st.columns([1, 2, 2])
    _bd = c1.date_input("기준일 (달력에서 다른 달도 선택)", value=TODAY.date(), min_value=df.date.min(), max_value=TODAY, key="dup_date")
    c2.multiselect("매체 필터", CHS, default=CHS, key="dup_media")
    c3.info(f"기준월: **{_bd.year}년 {_bd.month}월**")
    np.random.seed(11)
    camps = sorted(df.campaign.unique())
    month_db = {c: int(np.random.uniform(800, 1600)) for c in camps}
    dup_rate = {c: round(np.random.uniform(12, 22), 1) for c in camps}
    tot_db = sum(month_db.values()); tot_dup = sum(int(month_db[c] * dup_rate[c] / 100) for c in camps)
    k = st.columns(5)
    k[0].metric("월 합산 DB", f"{tot_db:,}")
    k[1].metric("중복 DB", f"{tot_dup:,}")
    k[2].metric("월 중복률", f"{tot_dup/tot_db*100:.1f}%")
    k[3].metric(f"{_bd.strftime('%m/%d')} DB", f"{int(tot_db/15):,}")
    k[4].metric(f"{_bd.strftime('%m/%d')} 중복 DB", f"{int(tot_db/15*np.random.uniform(0.1,0.18)):,}")

    st.markdown("#### 📈 월 DB 중복률 추이")
    np.random.seed(110)
    ndays = (pd.Timestamp(_bd.year, _bd.month, 1) + pd.offsets.MonthEnd(1)).day  # 선택월 마지막 날
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
elif active == TAB_NAMES[6]:
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
elif active == TAB_NAMES[7]:
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
elif active == TAB_NAMES[8]:
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


# ============================================================
# 🎯 KPI 탭 — 매체별 월 목표/수집/잔여 + 일별 달력(목표 대비 ±N)
# ============================================================
elif active == TAB_NAMES[9]:
    import calendar as _cal
    _kc1, _kc2 = st.columns([3, 1])
    _kc1.markdown("### 🎯 월별 KPI · DB 수집 현황")
    _months = sorted(df.month.unique(), reverse=True)   # 데이터 있는 월 전체
    _sel_m = _kc2.selectbox("조회 월", _months, index=0, key="kpi_month")

    KPI_GOAL = {"Google Ads": 3850, "Meta": 3950, "TikTok": 2200}   # 매체별 월 목표(가상)
    _ym = _sel_m
    _yy, _mm = int(_sel_m[:4]), int(_sel_m[5:7])
    _ndays = _cal.monthrange(_yy, _mm)[1]
    _mdf = df[df.month == _ym]
    _is_cur = (_sel_m == TODAY.strftime("%Y-%m"))
    _passed = TODAY.day if _is_cur else _ndays          # 과거 월은 말일까지 다 경과
    _tot_goal = sum(KPI_GOAL.values())

    # ── 매체별 카드 (수집 / 목표, 페이스 대비) ──
    _cols = st.columns(len(KPI_GOAL) + 1)
    _tot_got = 0
    for _i, (_ch, _goal) in enumerate(KPI_GOAL.items()):
        _got = int(_mdf[_mdf.channel == _ch].conversions.sum())
        _tot_got += _got
        _pace = round(_goal / _ndays * _passed)         # 오늘까지 도달했어야 할 목표
        _gap = _got - _pace
        _cols[_i].metric(_ch, f"{_got:,} / {_goal:,}",
                         f"{'+' if _gap >= 0 else ''}{_gap:,} (페이스 대비)")
    _rem_all = _tot_goal - _tot_got
    _cols[-1].metric("전체 달성", f"{_tot_got:,} / {_tot_goal:,}",
                     f"{_tot_got / _tot_goal * 100:.0f}% · 잔여 {_rem_all:,}")

    if _is_cur:
        _left_days = max(1, _ndays - _passed)
        st.caption(f"📅 {_yy}년 {_mm}월 · 경과 {_passed}/{_ndays}일 · 월말까지 **{max(0, _rem_all):,}건** 더 필요 "
                   f"→ 남은 {_left_days}일간 하루 약 **{max(0, round(_rem_all / _left_days)):,}건** 수집 페이스")
    else:
        st.caption(f"📅 {_yy}년 {_mm}월 (마감) · 총 **{_tot_got:,}건** 수집 / 목표 {_tot_goal:,}건 · "
                   f"달성률 **{_tot_got / _tot_goal * 100:.0f}%**")

    # ── CPA 목표 대비 표 ──
    _TGT_CPA = 26000   # 목표 CPA(가상). 낮을수록 좋음
    _cpc1, _cpc2 = st.columns([3, 1])
    _cpc1.markdown(f"#### 💰 CPA 목표 대비 (목표 {_TGT_CPA:,}원)")
    _days = list(range(1, _passed + 1))
    _base_day = _cpc2.selectbox("기준일 (이날까지 누적)", _days, index=len(_days) - 1,
                                format_func=lambda d: f"{_mm}월 {d}일",
                                key=f"kpi_cpa_base_{_sel_m}")
    _cpadf = _mdf[_mdf.date.dt.day <= _base_day]   # 기준일까지 누적
    _cpa_rows = []
    for _ch in KPI_GOAL:
        _c = _cpadf[_cpadf.channel == _ch]
        _sp, _cv = _c.spend.sum(), _c.conversions.sum()
        _mcpa = (_sp / _cv) if _cv else 0
        _dcpa = (_c.groupby(_c.date.dt.day).apply(
            lambda x: x.spend.sum() / max(1, x.conversions.sum())).mean()) if _cv else 0
        _gap = _mcpa - _TGT_CPA
        _cpa_rows.append({
            "매체": _ch, "누적 평균 CPA": f"{_mcpa:,.0f}원", "일 평균 CPA": f"{_dcpa:,.0f}원",
            "목표 대비": (f"🔴 +{_gap:,.0f}원 (초과)" if _gap > 0 else f"🟢 {_gap:,.0f}원 (달성)")})
    _asp, _acv = _cpadf.spend.sum(), _cpadf.conversions.sum()
    _acpa = (_asp / _acv) if _acv else 0
    _ag = _acpa - _TGT_CPA
    _cpa_rows.append({
        "매체": "전체", "누적 평균 CPA": f"{_acpa:,.0f}원", "일 평균 CPA": "—",
        "목표 대비": (f"🔴 +{_ag:,.0f}원 (초과)" if _ag > 0 else f"🟢 {_ag:,.0f}원 (달성)")})
    st.dataframe(pd.DataFrame(_cpa_rows), hide_index=True, use_container_width=True)
    st.caption(f"💡 **{_mm}월 {_base_day}일까지 누적** · 목표 **{_TGT_CPA:,}원** 이하 = 달성(🟢). "
               f"누적 평균이 목표를 넘으면(🔴), 남은 기간 일 CPA를 목표 아래로 낮춰 끌어내려야 합니다.")

    # ── 일별 달력 (일목표 대비 ±N) · 상단 '조회 월' 따라 같이 바뀜 ──
    st.markdown(f"#### 📅 {_yy}년 {_mm}월 · 일별 DB 수집 (일목표 대비)")
    _daily_goal = round(_tot_goal / _ndays)
    _dser = _mdf.groupby(_mdf.date.dt.day).conversions.sum().to_dict()
    _first_wd = (date(_yy, _mm, 1).weekday() + 1) % 7      # 일요일=0 기준 시작 칸
    _wd = ["일", "월", "화", "수", "목", "금", "토"]
    _cells = "".join(f'<div class="hd">{d}</div>' for d in _wd)
    _cells += '<div class="cell empty"></div>' * _first_wd
    for _d in range(1, _ndays + 1):
        if _d > _passed:                                  # 미래 날짜 (목표만 표시)
            _cells += (f'<div class="cell fut"><div class="dn">{_d}</div>'
                       f'<div class="gl">목표 {_daily_goal}</div></div>')
            continue
        _cnt = int(_dser.get(_d, 0))
        _diff = _cnt - _daily_goal
        _cls = "pos" if _diff >= 0 else "neg"
        _sign = "+" if _diff >= 0 else ""
        _tcls = " today" if _d == _passed else ""
        _cells += (f'<div class="cell{_tcls}"><div class="dn">{_d}</div>'
                   f'<div class="cnt">{_cnt}</div>'
                   f'<div class="diff {_cls}">{_sign}{_diff}</div>'
                   f'<div class="gl">목표 {_daily_goal}</div></div>')
    _rows_n = (_first_wd + _ndays + 6) // 7
    _cal_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
      body{{margin:0;font-family:-apple-system,system-ui,'Apple SD Gothic Neo',sans-serif;background:{BG};}}
      .cal{{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;padding:2px;}}
      .hd{{color:{MUTED};font-size:12px;font-weight:600;text-align:center;padding:3px 0;}}
      .cell{{background:{CARD};border:1px solid {BORDER};border-radius:9px;min-height:76px;padding:6px 7px;}}
      .cell.empty{{background:transparent;border:none;}}
      .cell.fut{{opacity:.4;}}
      .cell.today{{border-color:{ACCENT};box-shadow:0 0 0 1px {ACCENT};}}
      .dn{{color:{MUTED};font-size:11.5px;font-weight:600;}}
      .cnt{{color:{TEXT};font-size:18px;font-weight:700;line-height:1.15;margin-top:2px;}}
      .diff{{font-size:11px;font-weight:700;margin-top:1px;}}
      .diff.pos{{color:{GREEN};}} .diff.neg{{color:{RED};}}
      .gl{{color:#71717a;font-size:9.5px;margin-top:3px;}}
      .lg{{color:{MUTED};font-size:12px;padding:9px 4px 0;}}
    </style></head><body>
    <div class="cal">{_cells}</div>
    <div class="lg">● 큰 숫자 = 그날 수집 DB · 일목표 <b style="color:{TEXT}">{_daily_goal}건</b> 대비
      <span style="color:{GREEN}">초록 +n(초과)</span> / <span style="color:{RED}">빨강 -n(미달)</span></div>
    </body></html>"""
    _dcomp.html(_cal_html, height=44 + _rows_n * 102 + 48, scrolling=False)
