# 검증 정책

도메인 데이터 검증 실패 시 CSV/SQL/payload 생성으로 넘어가지 않는다. 검증 결과는 `output/reports/validation_report.md`에 기록한다.

검증 범위는 row 수, PK/unique 중복, schema-map의 필수 컬럼, 물리·논리 FK, 인기 강의 비율, 시간 범위, 선수과목 이수 가능성이다.

payload는 별도로 총 건수, hotspot 비율, 시간 분포, scenario 비율, ID 존재 여부, expected status 매핑을 검증하며 결과는 `output/reports/payload_report.md`에 기록한다. 비율 허용 오차는 반올림으로 생기는 1건 이내이고, hotspot/시간 분포는 요구사항의 ±2% 이내다.

