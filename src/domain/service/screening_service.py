"""핵심 스크리닝 비즈니스 로직(Domain Service)을 구현합니다.

이 서비스는 Inbound Port를 구현하고, Outbound Port에 의존하여
모든 계산과 필터링을 오케스트레이션합니다.
"""

from typing import Dict, List, Callable, Optional
import pandas as pd
import numpy as np

from domain.ports.inbound import ScreeningUseCasePort
from domain.ports.outbound import FinancialDataSourcePort, StrategyLoaderPort
from domain.model.criteria import Criteria, QoQCriteria
from domain.model.data_models import FinancialData


class QuantScreeningService(ScreeningUseCasePort):
    """
    ScreeningUseCasePort(Inbound Port)의 구현체이자
    핵심 비즈니스 로직을 담당하는 도메인 서비스입니다.
    """

    def __init__(
        self,
        data_source: FinancialDataSourcePort,
        strategy_loader: StrategyLoaderPort
    ):
        """서비스를 초기화하고 의존성을 주입합니다.

        Args:
            data_source (FinancialDataSourcePort): 재무 데이터를 로드할 Outbound Port.
            strategy_loader (StrategyLoaderPort): 전략을 로드할 Outbound Port.
        """
        self.data_source = data_source
        self.strategy_loader = strategy_loader

        self.financial_data: FinancialData = self.data_source.load_financial_data()
        self.active_strategies: Dict[str, Criteria] = self.strategy_loader.load_active_strategies()

        self._metric_map: Dict[str, pd.DataFrame] = {
            "영업이익": self.financial_data.operating_profit,
            "매출액": self.financial_data.sales,
            "당기순이익": self.financial_data.net_income,
        }
        
        self._execution_map: Dict[str, Callable[[Criteria], List[str]]] = {
            "QoQ_Growth": self._execute_qoq_growth,
        }

    def run_all_active_strategies(self) -> Dict[str, List[str]]:
        """로드된 모든 활성 전략을 실행합니다.
        
        Returns:
            Dict[str, List[str]]: {전략_이름: [통과된 종목 리스트]} 딕셔너리.
        """
        results = {}
        for strategy_name, criteria in self.active_strategies.items():
            results[strategy_name] = self._execute_strategy(strategy_name, criteria)
        return results

    def _execute_strategy(self, name: str, criteria: Criteria) -> List[str]:
        """디스패치 맵을 사용해 단일 전략을 실행합니다.

        Args:
            name (str): 전략 이름 (로그용).
            criteria (Criteria): 실행할 Criteria 객체.

        Returns:
            List[str]: 통과된 종목명 리스트.
        """
        executor = self._execution_map.get(criteria.type)

        if not executor:
            print(f"  🚨 로직 없음: [{name}] 알 수 없는 type ({criteria.type})")
            return []
        
        try:
            return executor(criteria)
        except Exception as e:
            print(f"  🚨 실행 오류: [{name}] {e}")
            return []

    def _execute_qoq_growth(self, criteria: QoQCriteria) -> List[str]:
        """QoQCriteria 로직을 오케스트레이션합니다.

        Args:
            criteria (QoQCriteria): 실행할 QoQCriteria 객체.

        Returns:
            List[str]: 통과된 종목명 리스트.
        
        Raises:
            ValueError: criteria.metric이 self._metric_map에 없는 경우.
        """
        df = self._get_metric_dataframe(criteria.metric)
        if df is None:
            raise ValueError(f"Metric 없음: '{criteria.metric}'")

        base_values = self._get_quarterly_data(df, criteria.base_quarter)
        target_values = self._get_quarterly_data(df, criteria.target_quarter)

        growth_rate = self._safe_growth_rate(base_values, target_values)

        return self._filter_stocks_by_growth(growth_rate, criteria.min_growth_pct)

    def _get_metric_dataframe(self, metric: str) -> Optional[pd.DataFrame]:
        """매핑을 통해 Metric에 해당하는 DataFrame을 반환합니다.

        Args:
            metric (str): 찾고자 하는 재무 지표 이름 (예: "영업이익").

        Returns:
            Optional[pd.DataFrame]: 해당 지표의 DataFrame 또는 None.
        """
        return self._metric_map.get(metric)

    def _get_quarterly_data(self, df: pd.DataFrame, quarter: str) -> pd.Series:
        """DataFrame에서 특정 분기(열)의 데이터를 추출합니다.

        Args:
            df (pd.DataFrame): 원본 데이터프레임.
            quarter (str): 추출할 분기 이름 (컬럼명).

        Returns:
            pd.Series: 해당 분기의 데이터.

        Raises:
            KeyError: DataFrame에 해당 분기(컬럼)가 없는 경우.
        """
        if quarter not in df.columns:
            raise KeyError(f"분기(열) 없음: {quarter}")
        return df[quarter]

    def _filter_stocks_by_growth(self, rate: pd.Series, min_growth: float) -> List[str]:
        """계산된 성장률을 기준으로 종목을 필터링합니다.
        
        NaN 값은 비교 시 False로 처리되어 자동 탈락합니다.

        Args:
            rate (pd.Series): 계산된 성장률 (인덱스: 종목명).
            min_growth (float): 최소 통과 성장률.

        Returns:
            List[str]: 통과된 종목명 리스트.
        """
        passed_mask = (rate >= min_growth)
        return rate[passed_mask].index.tolist()

    def _safe_growth_rate(self, base: pd.Series, target: pd.Series) -> pd.Series:
        """안전한 분기 성장률을 계산합니다. (NaN/0/음수 처리)

        - (흑자): (target / base) - 1
        - (흑자전환): base <= 0 이고 target > 0 이면 'np.inf' (무한 성장)
        - (그 외): 'np.nan' (계산 불가, 필터 시 탈락)

        Args:
            base (pd.Series): 기준 분기 값 (V1).
            target (pd.Series): 비교 분기 값 (V2).

        Returns:
            pd.Series: 계산된 성장률. (인덱스: 종목명)
        """
        growth = (target / base) - 1
        
        conditions = [
            (base > 0),
            (base <= 0) & (target > 0),
        ]
        choices = [
            growth,
            np.inf,
        ]
        
        safe_growth = np.select(conditions, choices, default=np.nan)
        return pd.Series(safe_growth, index=base.index)