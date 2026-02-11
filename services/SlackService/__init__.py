"""
Slack Service Package
슬랙 알림 서비스 패키지
"""

from .simple_slack import (
    SimpleSlack,
    get_slack,
    slack
)

__all__ = [
    'SimpleSlack',
    'get_slack',
    'slack'
]

# 패키지 정보
__version__ = '1.0.0'
__author__ = 'Argos'