# JPA 엔티티 분석 — Mock Data Harness 사전 분석

## 0. 분석 범위와 전제

- 기준 소스: `src/main/java/badapodo/sugang/domain`의 JPA 애너테이션과 관련 Repository/Service
- 데이터베이스: `application.yml` 기준 PostgreSQL
- Spring Boot 3.2 기본 물리 네이밍 전략을 전제로, 명시되지 않은 이름은 camelCase → snake_case로 해석했다.
- 운영 설정의 `spring.jpa.hibernate.ddl-auto`는 주석 처리되어 있고 Flyway/Liquibase/DDL 스크립트도 없다. 따라서 아래 내용은 **엔티티가 의도하는 스키마**이며, 현재 운영 DB의 실제 스키마와 일치하는지는 `information_schema` 또는 `pg_dump --schema-only`로 별도 확인해야 한다.
- `BaseEntity`는 `@MappedSuperclass`이므로 독립 엔티티/테이블이 아니다. 모든 엔티티 테이블에 감사 컬럼 4개를 제공한다.
- `Role`은 엔티티가 아니라 `Member.role`에 문자열로 저장되는 enum이다.
- 요청 예시에 있는 `EnrollmentPayload`라는 클래스/엔티티는 현재 프로젝트에 없다. 실제 영속 엔티티는 `Enrollment`이며, API 입력 DTO는 `EnrollmentRequest(courseId)`이다.

## 1. 엔티티 목록

| 엔티티 | 테이블 | PK 컬럼 | 역할 |
|---|---|---|---|
| `Department` | `department` | `id` | 학과 |
| `Member` | `member` | `member_id` | 로그인/회원 정보 |
| `Student` | `student` | `student_id` | 회원과 학과를 연결하는 학생 |
| `Course` | `course` | `id` | 강의 및 정원 상태 |
| `CourseTime` | `course_time` | `id` | 강의 시간표 |
| `Prerequisite` | `prerequisite` | `id` | 학과별 선수과목 규칙 |
| `CompletedCourse` | `completed_course` | `id` | 학생의 이수 과목 |
| `Enrollment` | `enrollment` | `id` | 현재 수강 신청 |

공통 상속 필드(`BaseEntity`):

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 여부 | 비고 |
|---|---|---|---|---|
| `createdBy` | `created_by` | `varchar(255)` | 선택 | `updatable=false`, `@CreatedBy` |
| `createdDate` | `created_date` | `timestamp` | 선택 | `updatable=false`, `@CreatedDate` |
| `lastModifiedBy` | `last_modified_by` | `varchar(255)` | 선택 | `@LastModifiedBy` |
| `lastModifiedDate` | `last_modified_date` | `timestamp` | 선택 | `@LastModifiedDate` |

모든 PK는 `GenerationType.IDENTITY`의 `Long`이다. PostgreSQL에서는 identity/bigserial 계열의 `bigint`로 생성될 것으로 예상된다.

## 2. 엔티티별 필드, 컬럼, 관계 및 제약

### Department (`department`)

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 | 키/제약 |
|---|---|---|---|---|
| `id` | `id` | `bigint` | PK | PK, identity |
| `name` | `name` | `varchar(255)` | 예 | `nullable=false` |

- 연관관계 필드는 없다.
- 역방향 컬렉션도 없으므로 `Student → Department`, `Prerequisite → Department`만 존재하는 단방향 모델이다.
- 학과명에는 unique 제약이 없다. 동일 이름이 허용된다.

### Member (`member`)

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 | 키/제약 |
|---|---|---|---|---|
| `id` | `member_id` | `bigint` | PK | PK, identity |
| `email` | `email` | `varchar(255)` | 예 | `nullable=false`, unique |
| `password` | `password` | `varchar(255)` | 예 | `nullable=false` |
| `name` | `name` | `varchar(255)` | 예 | `nullable=false` |
| `role` | `role` | `varchar(255)` | 예 | `nullable=false`, enum string |

- `role` 허용 Java 값은 `ROLE_USER`, `ROLE_ADMIN`이다. DB `CHECK` 제약은 엔티티에 명시되어 있지 않다.
- `email`에는 단일 컬럼 unique 제약/인덱스가 생성된다.
- `Student`의 역방향 관계는 선언되어 있지 않다.

### Student (`student`)

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 | 키/제약 |
|---|---|---|---|---|
| `id` | `student_id` | `bigint` | PK | PK, identity |
| `department` | `department_id` | `bigint` | 아니요 | FK → `department.id` |
| `member` | `member_id` | `bigint` | 아니요 | FK → `member.member_id` |

- `Student → Department`: 단방향 `ManyToOne`, LAZY.
- `Student → Member`: 단방향 `ManyToOne`, LAZY.
- 두 `@JoinColumn` 모두 `nullable=false`가 없다. 따라서 **JPA 스키마상 NULL 허용**이다. 다만 서비스는 `student.department.id`를 즉시 사용하므로 Mock Data에서는 둘 다 사실상 필수로 채워야 한다.
- 학생-회원 1:1 unique 제약이 없다. 같은 `member_id`를 여러 학생이 참조할 수 있다.
- FK 컬럼에 명시적 인덱스가 없다.

### Course (`course`)

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 | 키/제약 |
|---|---|---|---|---|
| `id` | `id` | `bigint` | PK | PK, identity |
| `title` | `title` | `varchar(255)` | 예 | `nullable=false` |
| `capacity` | `capacity` | `integer` | 예 | `nullable=false` |
| `currentCount` | `current_count` | `integer` | 예 | `nullable=false` |
| `version` | `version` | `bigint` | 애너테이션상 아니요 | `@Version` optimistic lock |

- 관계 필드는 없으며 `CourseTime`과 `Prerequisite`가 단방향으로 `Course`를 참조한다.
- `title`은 unique가 아니다.
- `capacity >= 0`, `0 <= current_count <= capacity` 같은 DB `CHECK` 제약은 없다. 애플리케이션의 `enroll()`만 상한을 검사한다.
- JPA 생성자는 `currentCount=0`으로 초기화하지만 CSV 적재는 생성자를 거치지 않으므로 값을 반드시 제공해야 한다.
- CSV 직접 적재 시 `version=0`을 권장한다. NULL version은 Hibernate의 신규/분리 객체 판정이나 낙관적 락 갱신에 문제를 만들 수 있다.

### CourseTime (`course_time`)

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 | 키/제약 |
|---|---|---|---|---|
| `id` | `id` | `bigint` | PK | PK, identity |
| `course` | `course_id` | `bigint` | 예 | FK → `course.id`, `nullable=false` |
| `dayOfWeek` | `day_of_week` | `varchar(10)` | 예 | `nullable=false`, enum string, length 10 |
| `startTime` | `start_time` | `time` | 예 | `nullable=false` |
| `endTime` | `end_time` | `time` | 예 | `nullable=false` |
| `location` | `location` | `varchar(50)` | 아니요 | length 50 |

- `CourseTime → Course`: 단방향 `ManyToOne`, LAZY.
- 인덱스: `idx_course_time_course_id(course_id)`.
- `day_of_week` 값은 Java `DayOfWeek` 문자열인 `MONDAY` ~ `SUNDAY`여야 한다.
- 시작 < 종료, 30분 단위, 같은 강의 내 시간 중복을 보장하는 DB 제약은 없다.
- 스케줄 비트마스크가 30분 슬롯을 사용하므로 정확한 성능 테스트를 위해 시작/종료 시각은 30분 경계에 맞추는 것이 안전하다.

### Prerequisite (`prerequisite`)

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 | 키/제약 |
|---|---|---|---|---|
| `id` | `id` | `bigint` | PK | PK, identity |
| `course` | `course_id` | `bigint` | 아니요 | FK → `course.id` |
| `preCourse` | `pre_course_id` | `bigint` | 아니요 | FK → `course.id` |
| `department` | `department_id` | `bigint` | 아니요 | FK → `department.id` |

- 세 관계 모두 단방향 `ManyToOne`, LAZY.
- covering index: `idx_prerequisite_covering(course_id, department_id, pre_course_id)`.
- 세 join 컬럼 모두 `nullable=false`가 없어 JPA 스키마상 NULL 허용이지만 Repository 쿼리와 도메인 의미상 Mock Data에서는 모두 필수다.
- `(course_id, department_id, pre_course_id)` unique 제약은 없다. 같은 선수과목 규칙을 중복 적재할 수 있다.
- `course_id = pre_course_id` 또는 선수과목 순환을 막는 제약이 없다.

### CompletedCourse (`completed_course`)

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 | 키/제약 |
|---|---|---|---|---|
| `id` | `id` | `bigint` | PK | PK, identity |
| `studentId` | `student_id` | `bigint` | 예 | `nullable=false`, 논리 참조 |
| `courseId` | `course_id` | `bigint` | 예 | `nullable=false`, 논리 참조 |

- JPA 연관관계가 아닌 scalar ID 필드다. 따라서 **DB FK는 생성되지 않는다**.
- 논리적 참조: `student_id` → `student.student_id`, `course_id` → `course.id`.
- unique: `uk_student_completed_course(student_id, course_id)`.
- 별도 단일 컬럼 인덱스는 없다. 복합 unique 인덱스는 `student_id` 선두 조회에는 활용 가능하다.

### Enrollment (`enrollment`)

| Java 필드 | DB 컬럼 | 예상 타입 | 필수 | 키/제약 |
|---|---|---|---|---|
| `id` | `id` | `bigint` | PK | PK, identity |
| `studentId` | `student_id` | `bigint` | 예 | `nullable=false`, 논리 참조 |
| `courseId` | `course_id` | `bigint` | 예 | `nullable=false`, 논리 참조 |

- JPA 연관관계가 아닌 scalar ID 필드다. 따라서 **DB FK는 생성되지 않는다**.
- 논리적 참조: `student_id` → `student.student_id`, `course_id` → `course.id`.
- unique: `uk_student_course(student_id, course_id)`.
- 이 테이블의 적재 내용과 `course.current_count`가 자동 동기화되지 않는다. CSV 적재기가 두 값을 일관되게 계산해야 한다.

## 3. PK/FK 및 연관관계 방향 요약

```text
Department(id) <──────── Student(department_id)
      ^                         │
      │                         └──── member_id ────> Member(member_id)
      │
      └──────────── Prerequisite(department_id)
                            │              │
              course_id ────┘              └──── pre_course_id
                    │                               │
                    v                               v
                 Course(id) <────────────────── Course(id)
                    ^
                    └──────── CourseTime(course_id)

Student(student_id)  ······ CompletedCourse.student_id  (논리 참조, FK 아님)
Course(id)           ······ CompletedCourse.course_id   (논리 참조, FK 아님)
Student(student_id)  ······ Enrollment.student_id       (논리 참조, FK 아님)
Course(id)           ······ Enrollment.course_id        (논리 참조, FK 아님)
```

모든 실제 객체 연관관계는 자식에서 부모로 향하는 **단방향 `ManyToOne`**이다. 부모 엔티티에는 `OneToMany` 컬렉션이 없다. cascade/orphanRemoval도 전혀 선언되어 있지 않으므로 부모를 먼저 명시적으로 저장해야 한다.

## 4. 데이터 생성 및 CSV 적재 순서

### 실제 의존성 DAG

```text
Department ─┬─> Student ─┬─> CompletedCourse
            │            └─> Enrollment
            └─> Prerequisite

Member ───────> Student

Course ─────┬─> CourseTime
            ├─> Prerequisite (course 및 preCourse 모두)
            ├─> CompletedCourse
            └─> Enrollment
```

`Department`, `Member`, `Course` 사이에는 직접 의존성이 없으므로 셋은 병렬 생성 가능하다. 직렬 CSV 파이프라인이 필요하면 다음 순서가 안전하다.

1. `department`
2. `member`
3. `course`
4. `student`
5. `course_time`
6. `prerequisite`
7. `completed_course`
8. `enrollment`

`CompletedCourse`와 `Enrollment`에는 물리 FK가 없지만 고아 ID를 방지하기 위해 반드시 `Student`와 `Course` 뒤에 적재한다. `EnrollmentPayload`는 현 코드에 없으므로 별도 DB 적재 단계가 아니다.

## 5. CSV 적재 컬럼 순서

아래는 `COPY table (명시적 컬럼 목록) FROM ... CSV HEADER`를 전제로 한 **권장 CSV 헤더**다. DB의 물리 저장 순서에 의존하지 않는다.

| 적재 순서 | 파일/테이블 | 권장 헤더 |
|---:|---|---|
| 1 | `department.csv` | `id,name,created_by,created_date,last_modified_by,last_modified_date` |
| 2 | `member.csv` | `member_id,email,password,name,role,created_by,created_date,last_modified_by,last_modified_date` |
| 3 | `course.csv` | `id,title,capacity,current_count,version,created_by,created_date,last_modified_by,last_modified_date` |
| 4 | `student.csv` | `student_id,department_id,member_id,created_by,created_date,last_modified_by,last_modified_date` |
| 5 | `course_time.csv` | `id,course_id,day_of_week,start_time,end_time,location,created_by,created_date,last_modified_by,last_modified_date` |
| 6 | `prerequisite.csv` | `id,course_id,pre_course_id,department_id,created_by,created_date,last_modified_by,last_modified_date` |
| 7 | `completed_course.csv` | `id,student_id,course_id,created_by,created_date,last_modified_by,last_modified_date` |
| 8 | `enrollment.csv` | `id,student_id,course_id,created_by,created_date,last_modified_by,last_modified_date` |

권장 정책:

- 성능 데이터 간 참조를 결정적으로 만들려면 모든 CSV에 PK를 명시한다.
- 감사 컬럼은 nullable이므로 빈 값(NULL)으로 둘 수 있다. 성능 쿼리가 시간 범위를 사용한다면 현실적인 timestamp를 넣는다.
- PK를 명시 적재한 뒤 각 identity sequence를 `MAX(PK)`보다 큰 값으로 재설정해야 이후 JPA insert와 충돌하지 않는다.
- `COPY` 호출에는 반드시 위 컬럼 목록을 명시한다. 컬럼 목록 없는 `COPY table FROM`은 실제 DDL 컬럼 순서에 결합되므로 피한다.
- CSV의 NULL 표기와 빈 문자열을 구분한다. PostgreSQL `COPY ... CSV`의 NULL 옵션을 명시적으로 통일한다.

## 6. 제약조건 전체 요약

| 종류 | 대상 | 내용 |
|---|---|---|
| PK | 모든 엔티티 | 단일 `Long` identity PK |
| FK | `student` | `department_id` → `department.id`; `member_id` → `member.member_id` |
| FK | `course_time` | `course_id` → `course.id`, NOT NULL |
| FK | `prerequisite` | `course_id`, `pre_course_id` → `course.id`; `department_id` → `department.id` |
| 논리 참조 | `completed_course` | student/course ID이나 물리 FK 없음 |
| 논리 참조 | `enrollment` | student/course ID이나 물리 FK 없음 |
| unique | `member` | `email` |
| unique | `completed_course` | `uk_student_completed_course(student_id, course_id)` |
| unique | `enrollment` | `uk_student_course(student_id, course_id)` |
| index | `course_time` | `idx_course_time_course_id(course_id)` |
| index | `prerequisite` | `idx_prerequisite_covering(course_id, department_id, pre_course_id)` |
| version | `course` | `version` (`@Version`) |

명시된 `CHECK`, cascade delete, orphan removal, 자연키, 복합 PK는 없다.

## 7. Mock Data 생성 시 주의사항

1. **실제 DB 스키마를 먼저 검증한다.** 운영 `ddl-auto`가 비활성 상태이고 migration이 없으므로 엔티티와 DB가 drift했을 수 있다.
2. **논리 참조의 무결성을 Harness가 책임진다.** `completed_course`와 `enrollment`에는 FK가 없어 존재하지 않는 student/course ID도 DB가 받아들인다.
3. **`current_count`를 enrollment와 일치시킨다.** 일반적인 초기 데이터라면 각 course의 `current_count = enrollment 행 수`로 만든다. 정원을 넘기지 않는다.
4. **낙관적 락 version을 초기화한다.** course CSV에는 보통 `version=0`을 넣는다. 동시성 테스트 중 Hibernate가 update할 컬럼이다.
5. **unique 충돌을 피한다.** member email, 학생-과목별 completed/enrollment 조합은 전역적으로 중복되지 않아야 한다.
6. **nullable과 도메인 필수를 구분한다.** `Student`와 `Prerequisite`의 join 컬럼은 DB상 nullable이지만 서비스 로직은 실제 값이 있다고 가정한다. Mock Data에서는 NULL을 만들지 않는 편이 안전하다.
7. **enum은 정확한 대문자 문자열을 사용한다.** role은 `ROLE_USER|ROLE_ADMIN`, 요일은 `MONDAY`~`SUNDAY`다.
8. **시간표 데이터는 비트마스크 규칙에 맞춘다.** 30분 슬롯 기반이며 일주일 336비트를 사용한다. `start_time < end_time`을 지키고 30분 경계 사용을 권장한다.
9. **선수과목 규칙을 유효하게 만든다.** 자기 자신을 선수과목으로 지정하거나 순환 그래프를 만들지 말고, 같은 `(course, department, pre_course)` 중복도 생성하지 않는다.
10. **비밀번호는 BCrypt 해시로 저장한다.** `SecurityConfig`가 `BCryptPasswordEncoder`를 사용하므로 로그인까지 포함한 부하 테스트에서 평문을 넣으면 인증되지 않는다. 단순 수강 서비스 직접 호출 데이터라면 인증 사용 여부를 명확히 분리한다.
11. **identity sequence를 동기화한다.** 명시적 ID를 COPY한 후 sequence 미조정 시 이후 애플리케이션 insert가 PK 충돌을 낼 수 있다.
12. **Redis pre-warm 시점을 통제한다.** 애플리케이션 시작 시 course_time을 읽어 캐시를 예열한다. CSV를 앱 시작 후 적재했다면 캐시 재예열/초기화 없이는 DB와 Redis 스케줄 상태가 다를 수 있다.
13. **부모 삭제를 전제로 하지 않는다.** cascade delete 설정이 없고 실제 FK가 있는 자식 테이블은 부모 삭제를 막을 수 있다. 테스트 데이터 정리는 의존성의 역순으로 수행한다.

권장 정리 순서:

```text
enrollment → completed_course → prerequisite → course_time
→ student → course → member → department
```

`student`가 `member`와 `department`를 모두 참조하므로 마지막 구간에서 `student`를 먼저 제거해야 한다.
