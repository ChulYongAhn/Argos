"""
Argos Services
재사용 가능한 서비스 모듈 패키지
Unity 패키지처럼 각 서비스별로 독립된 폴더 구조
"""

# 각 서비스 임포트
from .SlackService import slack, get_slack
from .GoogleSheetService import record, record_dict, get_sheet, get_recorder

__all__ = [
    # Slack Service
    'slack',
    'get_slack',

    # Google Sheet Service
    'record',
    'record_dict',
    'get_sheet',
    'get_recorder'
]

# 패키지 정보
__version__ = '1.0.0'
__author__ = 'Argos'
__description__ = 'Reusable service packages for any Python project'