#!/bin/bash

# SlackService 테스트 스크립트
echo "🚀 SlackService 테스트 시작..."
echo "================================"

# 현재 디렉토리 저장
CURRENT_DIR=$(pwd)

# SlackService 디렉토리로 이동
cd "$(dirname "$0")"

# Python 테스트 실행
python TEST_SLACK.py

# 원래 디렉토리로 복귀
cd "$CURRENT_DIR"

echo "================================"
echo "✅ 테스트 완료!"