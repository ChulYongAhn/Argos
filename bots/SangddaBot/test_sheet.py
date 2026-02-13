#!/usr/bin/env python
"""구글 시트 기록 테스트"""

import os
import sys
from datetime import datetime

# Argos 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.GoogleSheetService import SimpleGoogleSheet
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_google_sheet():
    """구글 시트 연결 및 기록 테스트"""
    print("="*60)
    print("구글 시트 테스트")
    print("="*60)

    sheet_id = os.getenv('GOOGLE_SHEET_ID_3')
    if not sheet_id:
        print("❌ GOOGLE_SHEET_ID_3 환경변수가 설정되지 않았습니다.")
        return

    print(f"📋 시트 ID: {sheet_id}")

    # credentials.json 경로
    cred_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'services', 'GoogleSheetService', 'credentials.json'
    )

    # 테스트용 시트명
    sheet_name = datetime.now().strftime('%Y년%m월')
    print(f"📅 시트명: {sheet_name}")

    try:
        # 구글 시트 서비스 초기화
        sheet_service = SimpleGoogleSheet(
            sheet_id=sheet_id,
            credentials_file=cred_path,
            sheet_name=sheet_name
        )

        if not sheet_service.enabled:
            print("❌ 구글 시트 연결 실패")
            return

        print(f"✅ 구글 시트 연결 성공: {sheet_service.spreadsheet.title}")

        # 워크시트 가져오기
        worksheet = sheet_service.worksheet
        print(f"📊 워크시트: {worksheet.title}")

        # 테스트 데이터 추가
        print("\n📝 테스트 데이터 추가...")

        # 헤더 확인
        all_values = worksheet.get_all_values()
        if not all_values:
            # 헤더 추가
            headers = ['날짜', '종목이름', '등락률', 'D-1', 'D-2', 'D-3', 'D-4', 'D-5', 'D-6', 'D-7', 'D-8', 'D-9', 'D-10']
            worksheet.append_row(headers)
            worksheet.format('1:1', {'textFormat': {'bold': True}})
            print("✅ 헤더 추가 완료")

        # 테스트 데이터 추가
        test_data = [
            datetime.now().strftime('%Y-%m-%d'),
            '테스트종목',
            '+30.00%',
            '+1.5%', '-2.3%', '+0.8%', '-1.2%', '+3.4%',
            '-0.5%', '+2.1%', '-1.8%', '+0.3%', '-0.7%'
        ]

        worksheet.append_row(test_data)
        print(f"✅ 테스트 데이터 추가 완료: {test_data[1]}")

        # 추가된 데이터 확인
        all_values = worksheet.get_all_values()
        print(f"\n📊 현재 시트의 행 개수: {len(all_values)}개")

        # 마지막 행 출력
        if len(all_values) > 1:
            last_row = all_values[-1]
            print(f"📝 마지막 행: {last_row[:3]}...")  # 처음 3개 컬럼만

        # 시트 URL
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        print(f"\n🔗 구글 시트 URL: {sheet_url}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)

if __name__ == "__main__":
    test_google_sheet()
