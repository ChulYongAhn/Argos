"""
심플 구글 시트 레코더 - 어떤 프로젝트에서도 수정 없이 사용 가능
가변 인자를 받아서 시트에 기록
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Optional, Any
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class SimpleGoogleSheet:
    """범용 구글 시트 레코더"""

    def __init__(self, sheet_id: Optional[str] = None,
                 credentials_file: Optional[str] = None,
                 sheet_name: str = "데이터"):
        """
        초기화

        Args:
            sheet_id: 구글 시트 ID (없으면 .env에서 GOOGLE_SHEET_ID 읽음)
            credentials_file: 인증 파일 경로 (없으면 .env에서 GOOGLE_CREDENTIALS_FILE 읽음)
            sheet_name: 사용할 시트 이름 (기본: "데이터")
        """
        self.sheet_id = sheet_id or os.getenv('GOOGLE_SHEET_ID')
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.sheet_name = sheet_name

        if not self.sheet_id:
            print("⚠️ 구글 시트 ID가 없습니다. .env 파일에 GOOGLE_SHEET_ID를 설정하세요.")
            self.enabled = False
            return

        try:
            self.client = self._authenticate()
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            self.worksheet = self._get_or_create_sheet()
            self.enabled = True
            print(f"✅ 구글 시트 연결 성공: {self.spreadsheet.title}")
        except Exception as e:
            print(f"❌ 구글 시트 연결 실패: {e}")
            self.enabled = False

    def _authenticate(self):
        """구글 시트 API 인증"""
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=scope
        )

        return gspread.authorize(creds)

    def _get_or_create_sheet(self):
        """시트 가져오기 또는 생성"""
        try:
            return self.spreadsheet.worksheet(self.sheet_name)
        except:
            # 시트가 없으면 생성
            return self.spreadsheet.add_worksheet(
                title=self.sheet_name,
                rows=10000,
                cols=26  # A-Z 컬럼
            )

    def record(self, *args: Any) -> bool:
        """
        가변 인자를 받아서 시트에 기록

        Args:
            *args: 기록할 데이터들 (자동으로 타임스탬프 추가)

        Returns:
            성공 여부

        Examples:
            >>> sheet.record("매수", "비트코인", 140000000)
            >>> sheet.record("로그", "시스템 시작")
            >>> sheet.record("A", "B", "C", "D", "E")  # 원하는 만큼
        """
        if not self.enabled:
            return False

        try:
            # 타임스탬프 자동 추가
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 모든 인자를 문자열로 변환
            row_data = [timestamp] + [str(arg) for arg in args]

            # 시트에 추가
            self.worksheet.append_row(row_data)

            print(f"📝 시트 기록: {' | '.join(row_data[1:])}")
            return True

        except Exception as e:
            print(f"❌ 기록 실패: {e}")
            return False

    def record_dict(self, data: dict) -> bool:
        """
        딕셔너리를 시트에 기록 (헤더 자동 관리)

        Args:
            data: 기록할 딕셔너리

        Returns:
            성공 여부

        Examples:
            >>> sheet.record_dict({"종목": "비트코인", "가격": 140000000, "수량": 0.001})
        """
        if not self.enabled:
            return False

        try:
            # 타임스탬프 추가
            data = {"시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **data}

            # 현재 헤더 가져오기
            all_values = self.worksheet.get_all_values()

            if not all_values:
                # 헤더가 없으면 생성
                headers = list(data.keys())
                self.worksheet.append_row(headers)
                # 헤더 굵게
                self.worksheet.format('1:1', {'textFormat': {'bold': True}})
            else:
                headers = all_values[0]

                # 새로운 키가 있으면 헤더 업데이트
                new_keys = [k for k in data.keys() if k not in headers]
                if new_keys:
                    headers.extend(new_keys)
                    # 헤더 행 업데이트
                    cell_list = self.worksheet.range(f'A1:{chr(65+len(headers)-1)}1')
                    for i, cell in enumerate(cell_list):
                        cell.value = headers[i] if i < len(headers) else ""
                    self.worksheet.update_cells(cell_list)

            # 데이터를 헤더 순서에 맞춰 정렬
            row_data = [str(data.get(header, "")) for header in headers]
            self.worksheet.append_row(row_data)

            print(f"📝 시트 기록 (딕셔너리)")
            return True

        except Exception as e:
            print(f"❌ 기록 실패: {e}")
            return False

    def get_sheet_url(self) -> str:
        """구글 시트 URL 반환"""
        if not self.enabled:
            return ""
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"

    def clear_sheet(self) -> bool:
        """시트 내용 전체 삭제 (헤더 제외)"""
        if not self.enabled:
            return False

        try:
            # 첫 번째 행(헤더) 제외하고 삭제
            self.worksheet.delete_rows(2, self.worksheet.row_count)
            print("🗑️ 시트 내용 삭제 완료")
            return True
        except:
            return False


# 전역 인스턴스
_sheet = None


def get_sheet(sheet_id: Optional[str] = None) -> SimpleGoogleSheet:
    """구글 시트 싱글톤 인스턴스 반환"""
    global _sheet
    if _sheet is None:
        _sheet = SimpleGoogleSheet(sheet_id)
    return _sheet


def record(sheet_id: str, *args: Any) -> bool:
    """
    간편 기록 함수 - 시트 ID를 첫 번째 인자로 받음

    Args:
        sheet_id: 구글 시트 ID (필수)
        *args: 기록할 데이터들

    Examples:
        >>> import os
        >>> sheet_id = os.getenv('GOOGLE_SHEET_ID')
        >>> record(sheet_id, "매수", "비트코인", 140000000)
        >>> record(sheet_id, "시스템", "시작")
        >>> record(sheet_id, "A", "B", "C", "D", "E", "F")
    """
    sheet = SimpleGoogleSheet(sheet_id=sheet_id)
    return sheet.record(*args)


def record_dict(sheet_id: str, data: dict) -> bool:
    """
    딕셔너리 간편 기록 함수 - 시트 ID를 첫 번째 인자로 받음

    Args:
        sheet_id: 구글 시트 ID (필수)
        data: 기록할 딕셔너리

    Examples:
        >>> import os
        >>> sheet_id = os.getenv('GOOGLE_SHEET_ID')
        >>> record_dict(sheet_id, {"종목": "비트코인", "가격": 140000000})
    """
    sheet = SimpleGoogleSheet(sheet_id=sheet_id)
    return sheet.record_dict(data)


# 테스트
if __name__ == "__main__":
    print("심플 구글 시트 테스트")
    print("=" * 50)

    # 방법 1: 함수로 바로 사용 (가변 인자)
    record("테스트1", "데이터A", "데이터B", "데이터C")
    record("매수", "비트코인", 140000000, 0.001)
    record("매도", "이더리움", 5000000, 0.1, "익절")

    # 방법 2: 딕셔너리로 기록
    record_dict({
        "종목": "리플",
        "거래": "매수",
        "가격": 3500,
        "수량": 100,
        "메모": "테스트"
    })

    # 방법 3: 클래스로 사용
    sheet = SimpleGoogleSheet()
    sheet.record("클래스", "직접", "사용", "예시")

    print(f"\n📱 시트 URL: {sheet.get_sheet_url()}")
    print("✅ 구글 시트에서 확인하세요!")