"""
SimpleGoogleSheetService - 극도로 단순한 구글 시트 기록 서비스
외부에서는 Send 함수만 사용
"""

import gspread
from google.oauth2.service_account import Credentials
import os
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class _GoogleSheetManager:
    """내부 구글 시트 관리 클래스 (싱글톤)"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_GoogleSheetManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """구글 시트 초기화"""
        # 매번 .env 다시 확인
        sheet_id = os.getenv('GOOGLE_SHEET_ID')

        # 이미 초기화되었고 sheet_id가 같으면 스킵
        if self._initialized and hasattr(self, 'sheet_id') and self.sheet_id == sheet_id:
            return

        self.sheet_id = sheet_id
        self.credentials_file = os.path.join(
            os.path.dirname(__file__),
            'credentials.json'
        )
        self.client = None
        self.spreadsheet = None
        self.enabled = False

        if not self.sheet_id:
            print("❌ 구글 시트 ID가 없습니다. .env 파일에 GOOGLE_SHEET_ID를 설정하세요.")
            return

        if not os.path.exists(self.credentials_file):
            print(f"❌ 인증 파일이 없습니다: {self.credentials_file}")
            return

        try:
            self._connect()
            self.enabled = True
            self._initialized = True
            print(f"✅ 구글 시트 연결 성공")
        except Exception as e:
            print(f"❌ 구글 시트 연결 실패: {type(e).__name__}: {str(e)}")

    def _connect(self):
        """구글 시트 API 연결"""
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=scope
        )

        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(self.sheet_id)

    def send_data(self, sheet_name: str, *data: str) -> bool:
        """시트에 데이터 전송"""
        if not self.enabled:
            return False

        try:
            # 시트 찾기
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                print(f"❌ 시트 '{sheet_name}'이 존재하지 않습니다. 먼저 시트를 생성해주세요.")
                return False

            # 데이터를 문자열로 변환
            row_data = [str(item) for item in data]

            # 마지막 행에 추가
            worksheet.append_row(row_data)

            # 성공 로그
            data_str = " | ".join(row_data)
            print(f"✅ [{sheet_name}] 시트에 기록: {data_str}")
            return True

        except Exception as e:
            print(f"❌ 데이터 추가 실패: {e}")
            return False


def Send(sheet_name: str, *data: str) -> bool:
    """
    구글 시트에 데이터를 보내는 유일한 public 함수

    Args:
        sheet_name: 시트 이름 (미리 생성되어 있어야 함)
        *data: 기록할 문자열 데이터들

    Returns:
        bool: 성공 시 True, 실패 시 False

    Examples:
        Send("거래내역", "매수", "삼성전자", "70,000", "100주")
        Send("상한가", "에코프로", "+29.95%", "거래량: 1,234,567")
        Send("코인거래", "BTC", "매수", "140,000,000", "0.001")
    """
    if not data:
        print("❌ 기록할 데이터가 없습니다.")
        return False

    # .env 다시 로드 (경로 문제 해결)
    from dotenv import load_dotenv
    load_dotenv()

    # 싱글톤 리셋 (F5 문제 해결)
    _GoogleSheetManager._instance = None
    _GoogleSheetManager._initialized = False

    # 싱글톤 인스턴스 가져오기
    manager = _GoogleSheetManager()

    # 데이터 전송
    return manager.send_data(sheet_name, *data)


# 테스트 코드
if __name__ == "__main__":
    print("SimpleGoogleSheetService 테스트")
    print("=" * 50)

    # Send 함수만 사용
    Send("거래내역", "매수", "삼성전자", "70,000", "100주")
    Send("상한가", "에코프로", "+29.95%", "거래량: 1,234,567")
    Send("코인거래", "BTC", "매수", "140,000,000", "0.001")

    print("\n✅ 구글 시트에서 확인하세요!")