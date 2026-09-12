Shopping Backend

FastAPI와 PostgreSQL을 기반으로 구현한 쇼핑몰 백엔드 프로젝트입니다.

단순 CRUD 구현에 그치지 않고 JWT 인증, 사용자별 주문 접근 권한, 재고
관리, 결제/환불, SQLAlchemy ORM, Alembic 마이그레이션, 요청 단위
트랜잭션, Service/Repository 계층 분리를 직접 구현하는 것을 목표로
했습니다.

주요 기능

회원가입 및 로그인

비밀번호 해시 저장

JWT Access Token 발급

Bearer Token 기반 사용자 인증

사용자 권한 관리

로그인한 사용자의 정보 조회

자신의 주문만 조회·결제·취소·환불 가능

상품 및 재고 관리

상품 등록

주문 생성 시 재고 차감

주문 취소 및 환불 시 재고 복구

주문 관리

주문 생성

내 주문 목록 조회

주문 상세 조회

주문 상태 관리

결제 및 환불

주문 금액을 기준으로 결제 기록 생성

결제 완료 주문 환불

환불 시 Payment 상태 및 재고 복구

데이터베이스

SQLAlchemy ORM

PostgreSQL

Alembic migration

요청 단위 commit / rollback

테스트

Fake Repository를 활용한 OrderService 단위 테스트

주문, 권한, 결제, 취소, 환불 시나리오 검증

Tech Stack

Category           Technology

Language           Python
Web Framework      FastAPI
Database           PostgreSQL
ORM                SQLAlchemy
Migration          Alembic
Validation         Pydantic
Authentication     JWT, HTTP Bearer
Password Hashing   pwdlib
Testing            pytest
Code Quality       Ruff

Architecture

Client
  │
  │ HTTP Request
  ▼
FastAPI
  │
  ├── Pydantic Request Validation
  ├── Depends / Dependency Injection
  └── JWT Authentication
  │
  ▼
Service
  │
  ├── Business Rules
  ├── Authorization
  └── Order / Payment / Stock Flow
  │
  ▼
Repository
  │
  ▼
SQLAlchemy ORM
  │
  ▼
PostgreSQL

API 계층은 HTTP 요청/응답과 예외 변환을 담당하고, Service 계층은
주문·결제·재고·권한 등의 비즈니스 규칙을 담당합니다. Repository 계층은
SQLAlchemy를 이용한 영속성 처리를 담당하도록 분리했습니다.

ERD

erDiagram
    USER ||--o{ ORDER : places
    PRODUCT ||--o{ ORDER : included_in
    ORDER ||--o{ PAYMENT : has

    USER {
        int user_id PK
        string name
        string email UK
        string password_hash
    }

    PRODUCT {
        int product_id PK
        string name
        int price
        int stock
    }

    ORDER {
        int order_id PK
        int user_id FK
        int product_id FK
        int price
        int quantity
        string status
    }

    PAYMENT {
        int payment_id PK
        int order_id FK
        int amount
        string status
    }

Order.price에는 주문 생성 당시의 상품 가격을 저장합니다. 따라서 이후
상품 가격이 변경되어도 기존 주문의 결제 금액은 주문 시점 가격을 기준으로
계산할 수 있습니다.

Authentication & Authorization

로그인에 성공하면 사용자 ID를 sub claim에 담은 JWT Access Token을
발급합니다.

Login
  ↓
JWT Access Token 발급
  ↓
Authorization: Bearer <token>
  ↓
HTTPBearer
  ↓
JWT decode
  ↓
user_id 조회
  ↓
Current User

주문 API에서는 클라이언트가 전달한 사용자 ID를 신뢰하지 않고, JWT에서
인증된 current_user.user_id를 사용합니다.

또한 주문 상세 조회, 결제, 취소, 환불 시 주문의 user_id와 현재
사용자의 ID를 비교하여 다른 사용자의 주문에 접근하는 것을 차단합니다.

Order Flow

주문 생성

사용자 인증
  ↓
User / Product 존재 확인
  ↓
재고 확인
  ↓
주문 시점 상품 가격 저장
  ↓
재고 차감
  ↓
Order 생성

결제

본인 주문 확인
  ↓
결제 가능한 주문 상태 확인
  ↓
총 결제 금액 계산
  ↓
Payment(PAID) 생성
  ↓
Order → PAID

주문 취소

결제 전 PENDING 주문을 취소합니다.

PENDING
  ↓ cancel
CANCELED
  ↓
재고 복구

환불

결제된 주문은 일반 취소와 분리하여 환불 처리합니다.

Order(PAID)
  ↓
PAID Payment 조회
  ↓
Payment → REFUNDED
  ↓
재고 복구
  ↓
Order → CANCELED

이를 통해 결제가 완료된 주문이 Payment 기록 변경 없이 단순 취소되는
상황을 방지했습니다.

Transaction Management

DB Session은 FastAPI dependency를 통해 요청 단위로 관리합니다.

def get_session():
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

각 Repository에서 개별적으로 commit()하지 않고 하나의 요청에서 발생한
여러 DB 변경을 같은 Session으로 처리합니다.

예를 들어 환불 요청에서는 다음 작업이 하나의 요청 흐름에서 수행됩니다.

Payment 상태 변경
+ Product 재고 복구
+ Order 상태 변경
        ↓
      commit

처리 중 예외가 발생하면 rollback()하여 요청 중 수행된 DB 변경을 되돌릴
수 있도록 구성했습니다.

DB에서 생성되는 PK가 commit 이전에 필요한 경우에는 flush()를
사용합니다.

API

Auth

Method   Endpoint         Description               Auth

POST     /auth/signup   회원가입                  No
POST     /auth/login    로그인 및 JWT 발급        No
GET      /me            현재 로그인 사용자 조회   Yes

Product

Method   Endpoint      Description   Auth

POST     /products   상품 생성     No

Order

Method   Endpoint                      Description         Auth

POST     /order                      주문 생성           Yes
GET      /orders                     내 주문 목록 조회   Yes
GET      /orders/{order_id}          내 주문 상세 조회   Yes
DELETE   /orders/{order_id}          결제 전 주문 취소   Yes
POST     /orders/{order_id}/pay      주문 결제           Yes
POST     /orders/{order_id}/refund   결제 주문 환불      Yes

FastAPI 실행 후 /docs에서 Swagger UI를 통해 API를 테스트할 수
있습니다.

HTTP Error Handling

주요 도메인 예외를 API 계층에서 HTTP 상태 코드로 변환합니다.

Status   Example

400      잘못된 주문 상태, 결제 금액 제한
401      로그인 실패, 유효하지 않은 JWT
403      다른 사용자의 주문 접근
404      존재하지 않는 주문·상품·결제
409      이미 존재하는 이메일
422      Request validation 실패

Testing

pytest와 Fake Repository를 사용하여 Service 계층의 비즈니스 로직을
DB와 분리해 테스트했습니다.

현재 테스트 시나리오는 다음을 포함합니다.

주문 생성 성공

재고 부족 주문 차단

존재하지 않는 상품 주문 차단

주문 조회 성공

존재하지 않는 주문 조회

다른 사용자의 주문 접근 차단

결제 성공

중복 결제 차단

다른 사용자의 주문 결제 차단

주문 취소 및 재고 복구

환불 및 Payment 상태/재고 복구

결제 전 주문 환불 차단

python -m pytest -v

Project Structure

shopping_backend/
├── alembic/
│   └── versions/              # DB migration history
├── order/
│   ├── api.py                 # FastAPI endpoints / DI
│   ├── database.py            # Engine, Session, transaction lifecycle
│   ├── models.py              # Domain models
│   ├── orm_models.py          # SQLAlchemy ORM models
│   ├── service.py             # Order business logic
│   ├── user_service.py        # Signup / login logic
│   ├── product_service.py     # Product business logic
│   ├── repository.py          # Order persistence
│   ├── user_repository.py
│   ├── product_repository.py
│   ├── payment_repository.py
│   ├── payment.py             # Payment domain model
│   ├── security.py            # Password hashing / JWT
│   ├── exceptions.py          # Domain exceptions
│   └── decorators.py
├── test/
│   └── test_order_service.py
├── alembic.ini
└── .gitignore

Database Migration

Alembic을 사용하여 DB 스키마 변경 이력을 관리합니다.

현재 migration에는 다음 변경이 포함되어 있습니다.

users / orders 테이블 생성

사용자 email / password hash 추가

email unique constraint 추가

products 테이블 생성

orders-product 관계 연결

payments 테이블 생성

최신 migration 적용:

python -m alembic upgrade head

Local Setup

1. Repository clone

git clone <YOUR_REPOSITORY_URL>
cd shopping_backend

2. Dependencies

프로젝트에서 사용하는 주요 Python 패키지를 설치합니다.

pip install fastapi uvicorn sqlalchemy psycopg[binary] alembic python-dotenv pyjwt pwdlib pytest ruff

3. Environment Variables

프로젝트 루트에 .env 파일을 생성합니다.

DATABASE_URL=postgresql+psycopg://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>
JWT_SECRET_KEY=<YOUR_SECRET_KEY>

실제 .env 파일과 비밀키는 Git에 커밋하지 않습니다.

4. Migration

python -m alembic upgrade head

5. Run

python -m uvicorn order.api:app --reload --port 8001

Swagger UI:

http://127.0.0.1:8001/docs

What I Learned

이 프로젝트를 통해 단순히 FastAPI endpoint를 만드는 것보다, 하나의
요청이 실제 백엔드 내부에서 어떻게 흘러가는지를 중심으로 학습했습니다.

특히 다음 내용을 직접 구현하고 개선했습니다.

FastAPI Depends를 이용한 request-scoped dependency injection

JWT 인증과 사용자별 authorization의 차이

Domain / Service / Repository 책임 분리

SQLAlchemy Session과 ORM change tracking

flush, commit, rollback의 차이

여러 DB 변경을 하나의 transaction으로 묶는 방법

주문 당시 가격을 보존하는 price snapshot

주문 상태에 따른 결제·취소·환불 비즈니스 규칙

Fake Repository를 이용한 Service 단위 테스트

초기에는 메모리 기반 주문/재고/결제 로직으로 시작했지만, 이후
PostgreSQL과 SQLAlchemy를 도입하고 인증·인가 및 트랜잭션 구조까지
확장하면서 실제 웹 백엔드 구조로 발전시켰습니다.

Future Improvements

동시 주문 상황에서 overselling을 방지하기 위한 atomic stock update /
locking

관리자 권한 및 상품 관리 authorization

API response schema 확대

통합 테스트 및 실제 PostgreSQL 기반 E2E 테스트 자동화

배포 환경 구성 및 CI/CD