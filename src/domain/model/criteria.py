"""스크리닝 전략(Criteria)을 정의하는 도메인 모델입니다.

이 모듈은 모든 전략의 기반이 되는 추상 베이스 클래스(Criteria)와
개별 전략(예: QoQCriteria)을 구현하는 구체적인 데이터 클래스들을
포함합니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


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


@dataclass(frozen=True)
class QoQCriteria(Criteria):
    """특정 두 분기(QoQ)를 비교하는 전략을 정의합니다.

    Attributes:
        metric (str): 계산할 지표 (예: "매출액", "영업이익").
        base_quarter (str): 기준 분기 (예: "2023/1Q").
        target_quarter (str): 비교 분기 (예: "2023/2Q").
        min_growth_pct (float): 최소 성장률 (예: 1.0 -> 100%).
    """

    metric: str
    base_quarter: str
    target_quarter: str
    min_growth_pct: float

    @property
    def type(self) -> str:
        """Criteria 유형을 'QoQ_Growth'로 반환합니다.

        Returns:
            str: Criteria의 고유 유형.
        """
        return "QoQ_Growth"