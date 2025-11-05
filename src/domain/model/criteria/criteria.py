from abc import ABC, abstractmethod

class Criteria(ABC):
    """모든 스크리닝 전략(Criteria)이 상속받아야 하는 추상 베이스 클래스입니다."""

    @property
    @abstractmethod
    def type(self) -> str:
        """이 Criteria의 유형을 반환합니다.

        ScreeningService가 이 type을 보고 어떤 계산 로직을 실행할지 결정합니다.

        Returns:
            str: Criteria의 유형 (예: 'QoQ_Growth', 'TTM_Filter' 등).
        """
        pass