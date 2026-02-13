"""
404 에러 상세 디버그
"""

import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("🔍 구글 시트 404 에러 디버그")
print("=" * 50)

# 1. 시트 ID 확인
sheet_id = os.getenv('GOOGLE_SHEET_ID')
print(f"\n1. 시트 ID: {sheet_id}")
print(f"   URL: https://docs.google.com/spreadsheets/d/{sheet_id}")

# 2. credentials 확인
credentials_file = os.path.join(
    os.path.dirname(__file__),
    'credentials.json'
)
print(f"\n2. Credentials 파일: {credentials_file}")
print(f"   파일 존재: {os.path.exists(credentials_file)}")

# 3. 서비스 계정 이메일 확인
import json
with open(credentials_file) as f:
    cred_data = json.load(f)
    service_email = cred_data.get('client_email')
    print(f"\n3. 서비스 계정 이메일: {service_email}")

# 4. 인증 시도
print("\n4. 구글 API 인증 시도...")
try:
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

    # 5. 스프레드시트 열기 시도
    print(f"\n5. 스프레드시트 열기 시도...")
    try:
        spreadsheet = client.open_by_key(sheet_id)
        print(f"   ✅ 성공! 시트 이름: {spreadsheet.title}")

        # 시트 목록
        print("\n6. 시트 목록:")
        for ws in spreadsheet.worksheets():
            print(f"   - {ws.title}")

    except gspread.exceptions.SpreadsheetNotFound as e:
        print(f"   ❌ 스프레드시트를 찾을 수 없음!")
        print(f"   에러: {e}")
        print("\n   🔧 해결 방법:")
        print(f"   1. 이 URL을 브라우저에서 열어보세요:")
        print(f"      https://docs.google.com/spreadsheets/d/{sheet_id}")
        print(f"\n   2. 구글 시트에서 '공유' 버튼 클릭")
        print(f"   3. 이 이메일 추가: {service_email}")
        print(f"   4. '편집자' 권한 부여")
        print(f"   5. '보내기' 클릭")

    except Exception as e:
        print(f"   ❌ 다른 에러: {type(e).__name__}: {e}")

except Exception as e:
    print(f"   ❌ 인증 실패: {e}")

print("\n" + "=" * 50)