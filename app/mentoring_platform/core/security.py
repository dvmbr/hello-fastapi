from pwdlib import PasswordHash


class PasswordHasher:
    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

        # 더미 해시를 생성하여 존재하지 않는 사용자에 대한 인증 시에도 일정한 시간 지연을 유지합니다. (타이밍 공격 방지, 한번만 생성)
        self._dummy_hash = self._hasher.hash("dummy_password")

    def hash(self, plain_password: str) -> str:
        """평문 비밀번호를 해시로 변환합니다."""
        return self._hasher.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """평문 비밀번호와 해시된 비밀번호를 비교하여 일치 여부를 반환합니다."""
        return self._hasher.verify(plain_password, hashed_password)

    def check_needs_rehash(self, hashed_password: str) -> bool:
        """해시된 비밀번호가 현재 해싱 알고리즘과 설정에 맞지 않는 경우 True를 반환합니다."""
        return self._hasher.check_needs_rehash(hashed_password)

    def verify_dummy(self, plain_password: str) -> None:
        """존재하지 않는 사용자에 대한 인증 시에도 일정한 시간 지연을 유지하기 위해 더미 해시를 검증합니다."""
        try:
            self._hasher.verify(plain_password, self._dummy_hash)
        except Exception:
            pass  # 검증 실패 시 예외가 발생하지만, 이를 무시하여 일정한 시간 지연을 유지합니다.


# 전역적으로 사용할 PasswordHasher 인스턴스를 생성합니다. (singleton 패턴)
password_hasher = PasswordHasher()
