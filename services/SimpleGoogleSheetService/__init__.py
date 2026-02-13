"""
SimpleGoogleSheetService - 극도로 단순한 구글 시트 서비스
외부에서는 Send 함수만 사용
"""

from .simple_google_sheet import Send

__all__ = ['Send']

# 패키지 정보
__version__ = '2.0.0'
__author__ = 'Argos'