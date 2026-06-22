"""
Streamlit Community Cloud 데모가 비활성으로 잠들지 않게 주기적으로 방문(깨움)한다.
GitHub Actions(.github/workflows/keep-alive.yml)에서 6시간마다 실행.
- 일반 방문이면 트래픽이 갱신되어 sleep 카운터가 리셋됨
- 혹시 이미 잠들어 있으면 'wake up' 버튼을 눌러 깨운다
"""
import sys
from playwright.sync_api import sync_playwright

URL = "https://marketing-dashboard-demo-br6gpdt4i2yrshdygxanp8.streamlit.app/"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)

        # 이미 잠들어 있으면 깨우기
        try:
            btn = page.get_by_text("get this app back up", exact=False)
            if btn.count() > 0:
                btn.first.click()
                print("App was asleep — clicked wake button.")
                page.wait_for_timeout(45000)   # 다시 기동될 때까지 대기
            else:
                print("App already awake.")
        except Exception as e:
            print("wake check skipped:", e)

        page.wait_for_timeout(3000)
        print("Pinged OK · title:", (page.title() or "(no title)"))
        browser.close()
    print("keep-alive done")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 핑 실패해도 워크플로를 빨갛게 만들지 않음(다음 주기에 재시도)
        print("keep-alive warning:", e)
        sys.exit(0)
