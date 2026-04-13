from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.mentoring_platform.models.member import Member
from app.mentoring_platform.core.security import password_hasher
from app.mentoring_platform.schemas.auth import MemberRegister, MemberUpdate


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def verify_password(self, plain_password: str, member: Member) -> bool:
        """평문 비밀번호와 해시된 비밀번호를 비교하여 일치 여부를 반환합니다."""
        return password_hasher.verify(plain_password, member.password)

    async def authenticate(self, email: str, password: str) -> Member | None:
        """이메일과 비밀번호를 사용하여 사용자를 인증합니다. 인증에 성공하면 Member 객체를 반환하고, 실패하면 None을 반환합니다."""

        member = await self.get_by_email(email)
        if not member:
            # 존재하지 않는 사용자에 대한 인증 시에도 일정한 시간 지연을 유지하기 위해 더미 해시를 검증합니다.
            password_hasher.verify_dummy(password)
            return None

        if not self.verify_password(password, member):
            # 비밀번호가 일치하지 않는 상황
            return None

        return member

    async def create_member(self, payload: MemberRegister) -> Member:
        member = Member(
            email=payload.email,
            password=password_hasher.hash(payload.password),
            name=payload.name,
            role=payload.role,
            age=payload.age,
        )

        self.session.add(member)
        await self.session.flush()  # ID를 포함한 새 객체의 상태를 데이터베이스에 반영합니다.
        await self.session.refresh(member)  # 새 객체의 상태를 새로 고칩니다.

        return member

    async def get_by_id(self, member_id: int) -> Member | None:
        member = await self.session.get(Member, member_id)
        return member

    async def get_by_email(self, email: str) -> Member | None:
        result = await self.session.execute(select(Member).where(Member.email == email))
        return result.scalar_one_or_none()

    async def update(self, member: Member, payload: MemberUpdate) -> Member:
        updated_member = payload.model_dump(
            exclude_unset=True
        )  # 업데이트할 필드만 포함된 딕셔너리를 생성합니다.

        for field, value in updated_member.items():
            if field == "password" and value is not None:
                value = password_hasher.hash(
                    value
                )  # 실제 구현에서는 해싱된 비밀번호를 저장해야 합니다.
            setattr(
                member, field, value
            )  # 업데이트된 필드 값을 멤버 객체에 설정합니다.

        await self.session.flush()  # 변경 사항을 데이터베이스에 반영합니다.
        await self.session.refresh(member)  # 객체의 상태를 새로 고칩니다.

        return member

    async def delete(self, member: Member) -> list[Member]:
        await self.session.delete(member)
        await self.session.flush()  # 삭제 작업을 데이터베이스에 반영합니다.

    async def list(
        self,
        name: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[Member]:
        statement = select(Member)
        if name:
            statement = statement.where(Member.name.ilike(f"%{name}%"))
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        result = await self.session.execute(statement)
        members = result.scalars().all()
        return members
