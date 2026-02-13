"""
디버그 테스트 - 구글 시트 연결 확인
"""

import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

print("=" * 50)
print("🔍 구글 시트 연결 디버그")
print("=" * 50)

# 1. 환경변수 확인
sheet_id = os.getenv('GOOGLE_SHEET_ID')
print(f"\n1. GOOGLE_SHEET_ID: {sheet_id}")

# 2. credentials.json 경로 확인
credentials_file = os.path.join(
    os.path.dirname(__file__),
    'credentials.json'
)
print(f"2. Credentials 파일: {credentials_file}")
print(f"   파일 존재 여부: {os.path.exists(credentials_file)}")

# 3. 구글 시트 연결 시도
try:
    print("\n3. 구글 시트 연결 시도...")

    # 인증
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file(
        credentials_file,
        scopes=scope
    )

    client = gspread.authorize(creds)
    print("   ✅ 인증 성공")

    # 스프레드시트 열기
    spreadsheet = client.open_by_key(sheet_id)
    print(f"   ✅ 스프레드시트 열기 성공: {spreadsheet.title}")

    # 시트 목록 확인
    print("\n4. 시트 목록:")
    worksheets = spreadsheet.worksheets()
    for ws in worksheets:
        print(f"   - {ws.title}")

    # 상한가 시트 확인
    print("\n5. '상한가' 시트 확인:")
    try:
        worksheet = spreadsheet.worksheet("상한가")
        print(f"   ✅ '상한가' 시트 찾기 성공")

        # 테스트 데이터 추가
        test_data = ["DEBUG_TEST", "테스트", "성공"]
        worksheet.append_row(test_data)
        print(f"   ✅ 테스트 데이터 추가 성공: {test_data}")

    except gspread.exceptions.WorksheetNotFound:
        print("   ❌ '상한가' 시트를 찾을 수 없습니다.")
        print("   구글 스프레드시트에서 '상한가' 시트를 생성해주세요.")

except Exception as e:
    print(f"   ❌ 에러 발생: {type(e).__name__}: {e}")

    # 상세 에러 정보
    import traceback
    print("\n상세 에러 정보:")
    print(traceback.format_exc())

print("\n" + "=" * 50)
print("디버그 완료")
print("=" * 50)