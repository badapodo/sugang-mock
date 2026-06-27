# Mock Data Harness

JPA 엔티티 계약에 맞는 PostgreSQL 적재 CSV와 k6 수강신청 payload를 재현 가능하게 생성하고, 검증·분석·보고서·그래프까지 자동 생성한다.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py --scenario config/scenario.yaml --schema config/schema-map.yaml --seed 42
```

생성 결과는 `output/csv`, `output/sql`, `output/reports`, `output/charts`에 저장된다. DB 적재는 프로젝트 루트에서 다음처럼 실행한다.

`enrollment.csv`에는 독립 실패 시나리오를 위한 seed enrollment가 포함된다.

- `TIME_CONFLICT`: 요청 학생에게 겹치는 시간표의 기존 enrollment를 부여한다.
- `DUPLICATE`: 요청과 동일한 student/course enrollment를 미리 부여한다.
- `CAPACITY_OVER`: 대상 course를 테스트 시작 전에 정원까지 채운다.
- `PREREQUISITE_FAIL`: completed course 상태만으로 실패하며 seed enrollment에 의존하지 않는다.

성공, duplicate, time conflict, capacity over, prerequisite fail은 서로 겹치지 않는 student pool을 사용하며 실패 대상 course는 성공 course pool에서 제외된다.

성능 테스트 설계의 핵심 차트는 payload timeline, course request rank, hotspot competition, prerequisite validation, generated test scenario coverage, timeslot heatmap, course capacity utilization이다. 보조 분포 차트는 `output/charts/appendix`에 생성된다. 모든 차트 하단에는 해당 차트가 검증하는 목적이 자동으로 포함된다.

CSV 생성 없이 기존 산출물만 다시 시각화할 수도 있다.

```bash
.venv/bin/python scripts/generate_charts.py --output output --scenario config/scenario.yaml
```

```bash
psql "$DATABASE_URL" -f output/sql/load.sql
```

`load.sql`은 psql의 client-side `\copy`를 사용하므로 CSV 파일이 PostgreSQL 서버가 아니라 실행 머신에 있어도 된다.
