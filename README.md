# AI CMO 데모 대시보드 (포트폴리오용)

Claude Code로 직접 만든 실제 광고 분석 대시보드의 **데모 버전**입니다.
표시되는 모든 수치는 **가상(임시) 데이터**이며, 실제 광고주 데이터가 아닙니다.
API 연동 없이 메모리에서 데이터를 생성하므로 조회가 즉시 이뤄집니다.

## 화면
- **성과추이** — 4채널 통합 KPI(ROAS·CPA·전환·CVR) + 일별 차트
- **일자별 상세** — 캠페인 → 광고그룹 → 소재 드릴다운
- **A/B 테스트** — 소재별 ROAS·CPA·전환 비교
- **캠페인 모니터링** — 최근 7일 vs 직전 7일 CPA 이상신호 감지

## 로컬 실행
```bash
pip install -r requirements.txt
python3 -m streamlit run streamlit_app.py
```

## 배포 (Streamlit Community Cloud — 무료, 24시간 접속)
PC가 꺼져 있어도 항상 접속되는 공개 링크를 만드는 방법.

### 1) GitHub에 올리기
```bash
cd toss-demo-dashboard
git init
git add .
git commit -m "feat: AI CMO 데모 대시보드"
git branch -M main
git remote add origin https://github.com/<내아이디>/toss-demo-dashboard.git
git push -u origin main
```
> 이 폴더에는 실데이터·키가 전혀 없으므로 public repo로 올려도 안전합니다.

### 2) 배포
1. https://share.streamlit.io 접속 → GitHub 계정으로 로그인
2. **New app** 클릭
3. Repository: `<내아이디>/toss-demo-dashboard`
4. Branch: `main` / Main file path: `streamlit_app.py`
5. **Deploy** 클릭 → 1~2분 후 완료

### 3) 링크 확보
`https://<앱이름>.streamlit.app` 형태의 링크가 생성됩니다.
이 링크를 포트폴리오 헤드라인에 "▶ 라이브 대시보드 체험하기" 버튼으로 넣으면,
인사담당자가 직접 들어가 필터·드릴다운을 만져볼 수 있습니다.

## 안전성
- 실제 광고주 데이터·API 키·DB 없음 (전부 코드 내 가상 데이터 생성)
- 외부 연동 없음 → 빠르고, 유출 위험 0
