# 국민참여 사진 기반 안전지도 프로토타입

이 코드는 다음 흐름을 구현한 Flask 기반 예제입니다.

- 국민이 사진 업로드
- 사진 EXIF에서 GPS 좌표 추출
- 지도에 신고 위치 표시
- 관리자 화면에서 접수/검토/조치완료/포상 점수 관리

## 기능

1. 사진 업로드 신고
2. EXIF GPS 자동 추출
3. 좌표 기반 주소 변환(역지오코딩)
4. 신고 상세 보기
5. 안전지도 보기(Leaflet + OpenStreetMap)
6. 관리자 처리 상태 변경 및 포인트 부여

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate  # Windows는 .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

브라우저에서 아래 주소 접속:

- 메인: http://127.0.0.1:5000/
- 신고 등록: http://127.0.0.1:5000/report/new
- 지도: http://127.0.0.1:5000/map
- 관리자: http://127.0.0.1:5000/admin

## 참고

- 사진에 GPS EXIF가 없으면 수동 좌표 입력으로 보완할 수 있습니다.
- 역지오코딩은 OpenStreetMap Nominatim API를 사용합니다.
- 실제 운영 시에는 로그인, 권한 관리, 파일 검증, 개인정보 처리, 기관 연계 API, 포상 정책 로직 등을 추가해야 합니다.
