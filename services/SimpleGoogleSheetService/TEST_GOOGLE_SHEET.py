"""
SimpleGoogleSheetService 테스트
Send 함수만을 사용한 극도로 단순한 테스트
"""

import sys
import os

# 프로젝트 루트 경로 찾기
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

# .env 파일 경로 명시적 지정
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# 현재 파일의 디렉토리를 Python 경로에 추가
sys.path.insert(0, current_dir)

from simple_google_sheet import Send
from datetime import datetime
import time

def test_send_function():
    """Send 함수 테스트 - 상한가 시트만 사용"""

    print("=" * 50)
    print("🚀 SimpleGoogleSheetService Send 함수 테스트")
    print("=" * 50)

    # 참고: 구글 시트에 "상한가" 시트가 미리 생성되어 있어야 함

    # 상한가 시트 테스트
    print("\n[상한가 시트 테스트]")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    Send("상한가", now, "TEST_에코프로", "+29.95%", "거래량: 1,234,567")
    time.sleep(0.5)

    Send("상한가", now, "TEST_에코프로BM", "+29.90%", "거래량: 987,654")
    time.sleep(0.5)

    Send("상한가", now, "TEST_포스코DX", "+29.85%", "거래량: 456,789")
    time.sleep(0.5)

    Send("상한가", now, "TEST_삼성전자", "+29.80%", "거래량: 2,345,678")

    print("✅ 상한가 테스트 기록 완료")

    print("\n" + "=" * 50)
    print("✨ 테스트 완료!")
    print("구글 시트 '상한가' 시트에서 TEST_ 로 시작하는 항목들을 확인하세요.")
    print("=" * 50)


if __name__ == "__main__":
    # 주의: 실행 전 구글 시트에 "상한가" 시트가 생성되어 있어야 합니다
    test_send_function()