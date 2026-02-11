"""
Google Sheet Service Package
구글 시트 기록 서비스 패키지
"""

# 범용 구글 시트 (Simple)
from .simple_google_sheet import (
    SimpleGoogleSheet,
    get_sheet,
    record,
    record_dict
)

# Argos 전용 레코더
from .google_sheet_recorder import (
    GoogleSheetRecorder,
    get_recorder
)

__all__ = [
    # 범용
    'SimpleGoogleSheet',
    'get_sheet',
    'record',
    'record_dict',

    # 전용
    'GoogleSheetRecorder',
    'get_recorder'
]

# 패키지 정보
__version__ = '1.0.0'
__author__ = 'Argos'