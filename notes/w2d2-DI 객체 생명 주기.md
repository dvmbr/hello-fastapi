# w2d2-DI 객체 생명 주기

**절대 하면 안되는 짓**

```python
session = AssyncSession(engine) # 이렇게 전역변수로 세션을 만들어서 쓰면 안됨. (세션은 요청마다 새로 만들어야 함)

@router.get("/members")
async def get_members():
    result = await session.execute(select(Member)) # 모든 요청이 같은 세션 공유하게 됨
    members = result.scalars().all()
    return members
```

- 동시 요청시 충돌 -> 여러 요청이 같은 세션 공유 -> 트랜잭션 충돌, 데이터 무결성 문제, 커넥션 고갈 등 심각한 문제 발생 가능
- 커넥션 고갈 -> 세션이 커넥션 풀에서 반환되지 않음 -> 결국 모든 커넥션이 고갈되어 새로운 요청 처리 불가
- 메모리 누수 -> 세션이 계속 생성되고 반환되지 않으면 메모리 사용량 증가 -> 서버 다운 가능성

**세션은 요청마다 새로 만들어서 사용해야 함**

## yield로 세션 관리하기

돈을 이체하는 작업 (Transaction)에서 `yield`는 작업 전후 처리를 자동으로 해주는 역할.

```python
async def get_session() -> AsyncSession:
  session = Session() # 세션 생성 (예: 스마트 뱅킹 앱 에서 돈 이체를 시작하려고 이체 금액을 입력하는 창이 뜨는 것)
  try:
    yield session # 세션을 사용하는 작업 수행 (예: 돈 이체)
    session.commit() # 작업이 성공적으로 완료되면 트랜잭션 커밋
  except Exception as e:
    session.rollback() # 작업 중 예외가 발생하면 트랜잭션 롤백
    raise e
  finally:
    session.close() # 세션 정리 (예: 스마트 뱅킹 앱에서 돈 이체가 끝나서 이체 확인 화면이 뜨는 것)
```

- `yield`는 작업(이체 등) 중간에 세션을 반환하여 라우터에서 사용할 수 있게 해줌 -> 작업이 끝나면 자동으로 트랜잭션을 커밋하거나 롤백하고 세션을 정리해줌 -> 코드가 간결해지고 안전

```python
async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
```

- `async with` 블록이 끝나면 세션이 자동으로 닫히므로, 커넥션이 반환되고 메모리 누수 방지
- `yield`를 사용하여 세션을 반환하면, FastAPI가 요청이 끝날 때 자동으로 세션을 정리해줌 -> 코드가 간결해지고 안전

**요청동안만 세션이 유지되고, 요청이 끝나면 자동으로 정리됨**

### yield의 작동 방식

```python
def simple_generator():
    print("Before yield")
    yield "Hello"
    print("After yield")

gen = simple_generator()
value = next(gen)  # "Before yield" 출력, "Hello" 반환
next(gen)  # "After yield" 출력, StopIteration 발생
```

- `yield`는 함수의 실행을 일시 중지하고 값을 반환 -> 다음에 `next()`가 호출되면 중단된 지점부터 실행 재개
- FastAPI에서는 `yield`를 사용하여 의존성 주입에서 리소스를 관리 -> 요청이 끝나면 자동으로 정리

---

```python
async def get_session():
  print("세션 생성") # 요청 시작 시 출력
  async with AsyncSession(engine) as session:
    yield session # 라우터에 세션 전달
  print("세션 정리") # 요청이 끝나면 출력 -> 세션이 자동으로 닫히고 커넥션이 반환됨
```

- 요청이 들어올 때마다 "세션 생성" 출력 -> 요청이 끝날 때마다 "세션 정리" 출력 -> 세션이 올바르게 관리되고 있음을 확인할 수 있음
- `yield`를 사용하여 세션을 반환하면, FastAPI가 요청이 끝날 때 자동으로 세션을 정리해줌 -> 코드가 간결해지고 안전
- `yield` 이후는 cleanup 코드. 비즈니스 로직을 넣으면 안됨. (세션이 닫히기 전에 실행되므로, 세션을 사용하는 코드가 들어가면 에러 발생)

**위험한 코드 예시**

```python
async def get_session():
  print("세션 생성")
  async with AsyncSession(engine) as session:
    async with session.begin(): # 트랜잭션 시작
      yield session # 라우터에 세션 전달
      # 트랜잭션 커밋은 yield 이후에 자동으로 처리됨 -> 트랜잭션이 커밋되기 전에 코드가 실행되면 에러 발생 가능
      print("트랜잭션 커밋") # 이 코드는 트랜잭션이 커밋된 후에 실행되어야 함 -> yield 이후에 작성하면 안됨
```

- 트랜잭션이 커밋되기 전에 "트랜잭션 커밋"이 출력될 수 있음 -> 트랜잭션이 커밋되기 전에 코드가 실행되면 에러 발생 가능 -> 트랜잭션이 커밋된 후에 실행되어야 하는 코드는 `yield` 이후에 작성하면 안됨
- 데이터 무결성 문제, 트랜잭션 충돌, 예외 처리 문제 등 심각한 문제가 발생할 수 있음

### yield 이후 규칙

**해도 되는 것**

- session.close()와 같은 리소스 정리 코드
- 로그 출력, 모니터링 이벤트 기록 등 트랜잭션과 무관한 코드
  **하면 안되는 것**
- 세션을 사용하는 코드 (예: session.execute(), session.commit() 등) -> 세션이 닫히기 전에 실행되므로 에러 발생 가능
- 외부 api 호출, 데이터베이스 쿼리 등 트랜잭션이 커밋되기 전에 실행되어서는 안되는 코드
- 비즈니스 로직
- 데이터 변경 코드

## Transaction

- 트랜잭션이란 데이터베이스에서 일련의 작업을 하나의 단위로 묶어서 처리하는 것을 의미 -> 모든 작업이 성공적으로 완료되거나, 하나라도 실패하면 전체 작업이 롤백되어 이전 상태로 돌아감
- 트랜잭션을 사용하면 데이터 무결성을 보장할 수 있음 -> 예를 들어, 은행 계좌 간의 돈 이체 작업에서 트랜잭션을 사용하면, 돈이 출금되는 작업과 입금되는 작업이 하나의 트랜잭션으로 묶여서 처리됨 -> 출금 작업이 성공적으로 완료되고 입금 작업이 실패하면 전체 트랜잭션이 롤백되어 출금 작업도 취소됨 -> 데이터 무결성 보장
- 트랜잭션은 일반적으로 데이터베이스에서 지원하는 기능이지만, SQLAlchemy와 같은 ORM에서도 트랜잭션을 관리할 수 있는 기능을 제공 -> SQLAlchemy에서는 `session.begin()`을 사용하여 트랜잭션을 시작하고, `session.commit()`을 사용하여 트랜잭션을 커밋하며, `session.rollback()`을 사용하여 트랜잭션을 롤백할 수 있음

### commit과 rollback

- `session.commit()`: 트랜잭션을 커밋하여 데이터베이스에 변경 사항을 영구적으로 저장 -> 트랜잭션이 성공적으로 완료되었음을 나타냄
- 예를 들어, 은행에서 돈을 이체하는 작업에서 트랜잭션을 사용한다고 가정 -> 출금 작업과 입금 작업이 하나의 트랜잭션으로 묶여서 처리됨 -> 출금 작업이 성공적으로 완료되고 입금 작업이 성공적으로 완료되면 `session.commit()`을 호출하여 트랜잭션을 커밋 -> 내 계좌에서 돈이 출금되고 상대방 계좌에 돈이 입금됨 -> 트랜잭션이 성공적으로 완료되었음을 나타냄
- `session.rollback()`: 트랜잭션을 롤백하여 데이터베이스를 이전 상태로 되돌림 -> 트랜잭션이 실패했음을 나타냄
- 예를 들어, 은행에서 돈을 이체하는 작업에서 트랜잭션을 사용한다고 가정 -> 출금 작업과 입금 작업이 하나의 트랜잭션으로 묶여서 처리됨 -> 출금 작업이 성공적으로 완료되고 입금 작업이 실패하면 `session.rollback()`을 호출하여 트랜잭션을 롤백 -> 내 계좌에서 돈이 출금되지 않고 상대방 계좌에도 돈이 입금되지 않음 -> 트랜잭션이 실패했음을 나타냄
- 트랜잭션이 커밋되기 전에 예외가 발생하면 자동으로 롤백됨 -> 트랜잭션이 커밋되기 전에 코드가 실행되면 에러 발생 가능

### session.begin()

```python
class OrderService:
  async def create(self, payload: OrderCreate) -> Order:
    async with self.session.begin(): # commit 1
      ... # 주문 생성 로직

class InventoryService:
  async def reserve(self, order: Order) -> None:
    async with self.session.begin(): # commit 2
      ... # 재고 관리 로직

# 라우터에서 여러 서비스 호출
@router.post("/orders")
async def create_order(payload: OrderCreate):
  order = await order_service.create(payload) # commit 1 -> 성공
  await inventory_service.reserve(order) # commit 2 -> 실패

  # 주문은 생성됐는데 재고는 안줄어듦
```

- 이렇게 서비스레이어에서 각각 트랜잭션을 관리하면, 주문은 생성됐는데 재고는 줄어들지 않는 상황이 발생할 수 있음 -> 데이터 무결성 문제
- `session.begin()`을 사용하여 트랜잭션을 시작하는 컨텍스트 매니저를 사용하면, `with` 블록이 끝날 때 자동으로 트랜잭션을 커밋하거나 롤백할 수 있음 -> 코드가 간결해지고 안전 -> 주문 생성과 재고 관리가 하나의 트랜잭션으로 묶여서 처리됨 -> 주문 생성과 재고 관리가 모두 성공적으로 완료되거나, 하나라도 실패하면 전체 트랜잭션이 롤백되어 이전 상태로 돌아감 -> 데이터 무결성 보장

```python
@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
  payload: OrderCreate,
  session: AsyncSession = Depends(get_session)
  order_service: OrderService = Depends(get_order_service),
  inventory_service: InventoryService = Depends(get_inventory_service)
):
  async with session.begin(): # 주문 생성과 재고 관리가 하나의 트랜잭션으로 묶여서 처리됨
    order = await order_service.create(payload) # 주문 생성 로직
    await inventory_service.reserve(order) # 재고 관리 로직

    # 주문 생성과 재고 관리가 모두 성공적으로 완료어야 commit
    # 하나라도 실패하면 전체 트랜잭션이 롤백되어 이전 상태로 돌아감 -> 데이터 무결성 보장

  return order # commit 이후에 반환
```

- 트랜잭션 범위가 명확해짐
- 어떤 작업들이 하나의 트랜잭션인지 라우터에서 바로 확인 가능

## DI

- DI(Dependency Injection)는 객체 간의 의존 관계를 외부에서 주입하여 관리하는 디자인 패턴 -> 객체의 생성과 의존성 관리를 프레임워크나 컨테이너에 맡김으로써 코드의 결합도를 낮추고 유연성을 높이는 방법
- FastAPI에서는 `Depends`를 사용하여 DI를 구현 -> 라우터 함수의 매개변수에 `Depends`를 사용하여 의존성을 주입 -> FastAPI가 요청이 들어올 때마다 필요한 의존성을 자동으로 생성하고 주입 -> 코드가 간결해지고 테스트하기 쉬워짐

### 권한 체크 체이닝

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

# 1단계: 토큰 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 2단계: 현재 유저 조회
async def get_current_user(
  token: str = Depends(oauth2_scheme),
  session: AsyncSession = Depends(get_session),
) -> User:
  payload = decode_token(token)  # JWT 검증 (이후 Day에서 구현)
  user = await session.get(User, payload["sub"])
  if not user:
    raise HTTPException(401, "유저를 찾을 수 없어요")
  return user

# 3단계: 활성 유저만 허용
async def get_active_user(
  user: User = Depends(get_current_user),
) -> User:
  if not user.is_active:
    raise HTTPException(403, "비활성화된 계정이에요")
  return user

# 4단계: 관리자만 허용
async def get_admin_user(
  user: User = Depends(get_active_user),
) -> User:
  if not user.is_admin:
    raise HTTPException(403, "관리자 권한이 필요해요")
  return user
```

- `get_current_user`는 토큰을 추출하여 유저를 조회 -> `get_active_user`는 현재 유저가 활성 상태인지 체크 -> `get_admin_user`는 활성 유저 중에서 관리자 권한이 있는지 체크 -> 라우터에서 `Depends(get_admin_user)`를 사용하여 관리자 권한이 필요한 엔드포인트를 쉽게 구현할 수 있음
- 권한 체크가 필요한 엔드포인트에서는 `Depends(get_admin_user)`를 사용하여 관리자 권한이 필요한 엔드포인트를 쉽게 구현할 수 있음 -> 권한 체크 로직이 명확하게 분리되고 재사용 가능 -> 코드가 간결해지고 유지보수성이 향상됨
- DI를 사용하여 권한 체크 체이닝을 구현하면, 각 단계의 책임이 명확해지고 코드가 간결해짐 -> 권한 체크 로직이 명확하게 분리되고 재사용 가능 -> 코드가 간결해지고 유지보수성이 향상됨

## 전역 의존성

- fastAPI는 전역 의존성을 지원한다.

```python
app = FastAPI(dependencies=[Depends(get_current_user)]) # 이렇게 하면 모든 엔드포인트에서 get_current_user가 자동으로 호출되어 인증된 유저 정보가 주입됨
```

- 이렇게 하면 모든 엔드포인트에서 `get_current_user`가 자동으로 호출되어 인증된 유저 정보가 주입됨 -> 인증이 필요한 엔드포인트에서는 별도의 `Depends(get_current_user)`를 작성할 필요 없음 -> 코드가 간결해지고 유지보수성이 향상됨
- 하지만 모든 엔드포인트에서 인증이 필요한 경우에만 사용해야 함 -> 인증이 필요 없는 엔드포인트에서는 불필요한 인증 로직이 실행될 수 있음
- 전역 의존성을 사용할 때는 주의해야 할 점이 있음 -> 모든 엔드포인트에서 해당 의존성이 필요하지 않을 수 있음 -> 인증이 필요 없는 엔드포인트에서는 불필요한 인증 로직이 실행될 수 있음 -> 성능 저하 및 보안 문제 발생 가능 -> 전역 의존성은 모든 엔드포인트에서 해당 의존성이 필요한 경우에만 사용하는 것이 좋음
- 따라서 공통이라고 느껴질수록 한번 더 고민해보기.
- 예를 들어, `get_current_user`는 대부분의 엔드포인트에서 필요하지만, 인증이 필요 없는 엔드포인트도 존재할 수 있음 -> 이런 경우에는 전역 의존성으로 설정하기보다는 각 엔드포인트에서 필요한 경우에만 `Depends(get_current_user)`를 사용하는 것이 좋음 -> 코드가 명확해지고 불필요한 인증 로직이 실행되는 것을 방지할 수 있음
