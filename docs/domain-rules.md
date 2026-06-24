# Mock Data 도메인 규칙

- 모든 데이터는 seed를 통해 재현 가능해야 한다.
- `member.email`, `(completed_course.student_id, course_id)`, `(enrollment.student_id, course_id)`는 중복되지 않는다.
- 학생과 선수과목 규칙의 nullable FK는 DB 선언과 무관하게 항상 채운다.
- 강의 시간은 월~금, 09:00~18:00의 30분 경계에 생성하며 시작 시각은 종료 시각보다 빠르다.
- 선수과목은 더 작은 강의 ID만 참조해 자기 참조와 순환을 방지한다.
- 선수과목이 지정된 강의를 정상 신청할 수 있도록 해당 학과 학생 일부의 `completed_course`에 요구 과목을 포함한다.
- 인기 강의는 전체 강의의 정확히 `hotspot_course_ratio`만큼이며 별도 목록을 Context에 보관한다.
- DB 기준 데이터와 API 요청 payload는 분리한다. 초기 `enrollment.csv`는 빈 데이터이며 `course.current_count`는 0이다.
- `CREDIT_LIMIT`은 현 엔티티에 학점 필드가 없으므로 기본 비율은 0이다. 비율을 활성화하면 payload 라벨만 생성되며 실제 서버 판정 가능 여부는 별도 확인한다.

