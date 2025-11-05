from dataclasses import dataclass

from domain.model.criteria.criteria import Criteria


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