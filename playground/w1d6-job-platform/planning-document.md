# 채용 플랫폼 기획 문서

본 문서는 연습용 채용 플랫폼 서비스 기획에 대한 개요를 설명합니다.
백엔드 개발자 관점에서 서비스의 주요 기능과 요구사항을 정의하는 것을 목표로 합니다.

## 질문

- 누가 사용하나?
- 뭘 할 수 있나?
- 어떤 데이터 모델이 필요한가?

## 핵심 개념 (Entity)

1. 구직자 정보
2. 채용 담당자 정보
3. 회사 정보
4. 채용 공고 정보
5. 지원 정보

### 시나리오

1. 구직자:

- 계정을 만든다.
- 회사 목록을 조회한다.
- 채용 공고를 탐색한다.
- 원하는 공고에 지원한다.

2. 채용 담당자:

- 회사 정보를 등록/관리한다.
- 채용 공고를 올린다.
- 지원자 목록을 조회한다.

### 데이터 모델링

- 회원(MEMBERS): 구직자 계정 정보
- 채용 담당자(MEMBERS): 회사 관리자 계정 정보 (회원과 구분)
- 회사(COMPANIES): 채용 공고를 올리는 회사 정보
- 채용 공고(JOB_POSTS): 회사가 올리는 채용 공고 정보
- 지원(APPLICATIONS): 구직자가 채용 공고에 지원한 정보

_고려할 점_: 회원과 채용 담당자는 MEMBERS 테이블 + role 컬럼으로 통합.

### 결과:

- MEMBERS: 사용자
- COMPANIES: 회사 정보
- JOB_POSTS: 채용 공고
- APPLICATIONS: 지원 정보

## 관계 정의 (Relationship)

- COMPANIES가 JOB_POSTS를 소유한다.
  - COMPANIES 1 : JOB_POSTS N
  - JOB_POSTS.company_id (FK) -> COMPANIES.id
- MEMBERS가 APPLICATIONS를 소유한다.
  - MEMBERS 1 : APPLICATIONS N
  - APPLICATIONS.member_id (FK) -> MEMBERS.id
- JOB_POSTS가 APPLICATIONS를 소유한다.
  - JOB_POSTS 1 : APPLICATIONS N
  - APPLICATIONS.job_post_id (FK) -> JOB_POSTS.id
- MEMBERS가 JOB_POSTS에 지원한다.
  - MEMBERS N : JOB_POSTS N (다대다)
  - APPLICATIONS가 조인 테이블 역할을 하며, member_id와 job_post_id를 FK로 가짐

## 부가 기능 추가

기본 기능만 했을 때는 MEMBERS, COMPANIES, JOB_POSTS, APPLICATIONS 4개의 테이블로 충분하지만, 부가 기능을 추가하면서 더 많은 테이블이 필요할 수 있다.

- 태그 기능: JOB_POSTS에 여러 기술 스택, 직무, 카테고리 등의 태그를 붙이는 기능
  - JOB_POSTS N : TAGS N (다대다)
  - JOB_POST_TAGS 조인 테이블 필요
  - JOB_POST_TAGS.job_post_id (FK) -> JOB_POSTS.id
  - JOB_POST_TAGS.tag_id (FK) -> TAGS.id
- 소셜 로그인 기능: MEMBERS가 여러 소셜 계정을 연결하는 기능
  - MEMBERS 1 : SOCIAL_ACCOUNTS N (일대다)
  - SOCIAL_ACCOUNTS.member_id (FK) -> MEMBERS.id

_결과_: 7개의 테이블 필요

1. MEMBERS
2. COMPANIES
3. JOB_POSTS
4. SOCIAL_ACCOUNTS
5. TAGS
6. JOB_POST_TAGS
7. APPLICATIONS

## 제약조건

### MEMBERS

- `email`은 고유해야 한다. (UNIQUE)
- `age`는 18세 이상이어야 한다. (CHECK)
- `role`은 'job_seeker', 'recruiter', 'admin' 중 하나여야 한다. (CHECK)

### COMPANIES

- `business_number`은 고유해야 한다. (UNIQUE)

### JOB_POSTS

- `status`는 'OPEN', 'CLOSED', 'PAUSED' 중 하나여야 한다. (CHECK)

### APPLICATIONS

- `status`는 'APPLIED', 'REVIEWING', 'REJECTED', 'ACCEPTED' 중 하나여야 한다. (CHECK)
- `member_id`와 `job_post_id`의 조합은 고유해야 한다. (UNIQUE: 한 구직자가 같은 채용 공고에 여러 번 지원할 수 없도록)

### COMPANIES - JOB_POSTS 관계

- `ON DELETE CASCADE` 옵션을 설정하여, 회사가 삭제될 때 해당 회사의 채용 공고도 함께 삭제되도록 설정하는 것이 적절할 수 있다. 이렇게 하면 데이터 무결성을 유지할 수 있고, 회사가 삭제된 후에도 관련 없는 채용 공고가 남아있지 않도록 할 수 있다.

## 정규화

### 1NF

- 모든 컬럼이 원자값을 가져야 한다. (예: JOB_POSTS 테이블에서 하나의 컬럼에 여러 태그를 저장하는 대신, 별도의 TAGS 테이블과 조인 테이블을 만들어 다대다 관계로 표현)

### 2NF

- 모든 비키 컬럼은 기본 키 전체에 완전 함수 종속이어야 한다.
  (JOB_POST_TAGS에 job_title 또는 tag_name 같은 컬럼을 추가하면 job_title은 job_post_id 키에만, tag_name은 tag_id 키에만 종속되는 부분 함수 종속이 생겨 2NF 위반이 된다. 따라서 조인 테이블에는 관계 정보만 저장하고, job_title은 JOB_POSTS에, tag_name은 TAGS에 저장한다.)

### 3NF

- 비키 컬럼 간 이행적 종속이 없어야 한다. (예: APPLICATIONS에 member_email이나 job_title을 저장하면 각각 member_id, job_post_id를 통해 결정되는 이행적 종속이 발생하므로 3NF에 맞지 않는다. 따라서 회원 정보는 MEMBERS, 공고 정보는 JOB_POSTS에 두고 APPLICATIONS에는 관계 정보만 저장한다.)

## 결론

- 기본적으로 4개의 테이블로 시작하지만, 부가 기능을 추가하면서 총 7개의 테이블이 필요하다.
- 각 테이블과 컬럼에 적절한 제약조건을 설정하여 데이터 무결성을 유지한다.
- 정규화 원칙을 적용하여 데이터 중복을 최소화하고, 데이터 무결성을 높인다.
