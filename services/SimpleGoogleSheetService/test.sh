#!/bin/bash

# SimpleGoogleSheetService 테스트 스크립트
echo "📊 SimpleGoogleSheetService 테스트 시작..."
echo "================================"

# 현재 디렉토리 저장
CURRENT_DIR=$(pwd)

# SimpleGoogleSheetService 디렉토리로 이동
cd "$(dirname "$0")"

# Python 테스트 실행
python TEST_GOOGLE_SHEET.py

# 원래 디렉토리로 복귀
cd "$CURRENT_DIR"

echo "================================"
echo "✅ 테스트 완료!"