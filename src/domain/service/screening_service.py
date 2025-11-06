"""핵심 스크리닝 비즈니스 로직(Domain Service)을 구현합니다.

이 서비스는 Inbound Port를 구현하고, Outbound Port에 의존하여
모든 계산과 필터링을 오케스트레이션합니다.
"""

from typing import Dict, List, Callable, Optional
import pandas as pd
import numpy as np

# 1. 포트 임포트 (의존성)
from domain.ports.inbound import ScreeningUseCasePort
from domain.ports.outbound import FinancialDataSourcePort, StrategyLoaderPort

# 2. 모델 임포트 (데이터 구조)
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
        
        self._execution_map: Dict[str, Callable[[Criteria], pd.DataFrame]] = { # <--- 타입 힌트 수정
            "QoQ_Growth": self._execute_qoq_growth,
        }

    def run_all_active_strategies(self) -> Dict[str, pd.DataFrame]: # <--- 반환 타입 수정
        """로드된 모든 활성 전략을 실행합니다.
        
        Returns:
            Dict[str, pd.DataFrame]: {전략_이름: [결과 DataFrame]} 딕셔너리.
        """
        results = {}
        for strategy_name, criteria in self.active_strategies.items():
            results[strategy_name] = self._execute_strategy(strategy_name, criteria)
        return results

    def _execute_strategy(self, name: str, criteria: Criteria) -> pd.DataFrame: # <--- 반환 타입 수정
        """디스패치 맵을 사용해 단일 전략을 실행합니다.

        Args:
            name (str): 전략 이름 (로그용).
            criteria (Criteria): 실행할 Criteria 객체.

        Returns:
            pd.DataFrame: 통과된 종목 및 근거 데이터.
        """
        executor = self._execution_map.get(criteria.type)

        if not executor:
            print(f"  🚨 로직 없음: [{name}] 알 수 없는 type ({criteria.type})")
            return pd.DataFrame() # <--- 빈 DataFrame 반환
        
        try:
            return executor(criteria)
        except Exception as e:
            print(f"  🚨 실행 오류: [{name}] {e}")
            return pd.DataFrame() # <--- 빈 DataFrame 반환

    def _execute_qoq_growth(self, criteria: QoQCriteria) -> pd.DataFrame: # <--- 반환 타입 수정
        """QoQCriteria 로직을 오케스트레이션합니다.

        Args:
            criteria (QoQCriteria): 실행할 QoQCriteria 객체.

        Returns:
            pd.DataFrame: 통과된 종목 및 근거 데이터.
        
        Raises:
            ValueError: criteria.metric이 self._metric_map에 없는 경우.
        """
        df = self._get_metric_dataframe(criteria.metric)
        if df is None:
            raise ValueError(f"Metric 없음: '{criteria.metric}'")

        base_values = self._get_quarterly_data(df, criteria.base_quarter)
        target_values = self._get_quarterly_data(df, criteria.target_quarter)

        growth_rate = self._safe_growth_rate(base_values, target_values)

        # _filter... 함수 대신 새로운 결과 빌더 함수 호출
        return self._build_qoq_result_dataframe(
            base=base_values,
            target=target_values,
            rate=growth_rate,
            min_growth=criteria.min_growth_pct,
            metric_name=criteria.metric
        )

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

    def _build_qoq_result_dataframe(
        self,
        base: pd.Series,
        target: pd.Series,
        rate: pd.Series,
        min_growth: float,
        metric_name: str
    ) -> pd.DataFrame:
        """계산된 성장률을 기준으로 필터링하고 결과 DataFrame을 생성합니다.

        Args:
            base (pd.Series): 기준 분기 값.
            target (pd.Series): 비교 분기 값.
            rate (pd.Series): 계산된 성장률.
            min_growth (float): 최소 통과 성장률.
            metric_name (str): 컬럼 이름에 사용할 Metric 이름 (예: "영업이익").

        Returns:
            pd.DataFrame: 통과된 종목의 상세 결과 (인덱스: 종목명).
        """
        passed_mask = (rate >= min_growth)
        
        # 필터링된 데이터로 새 DataFrame 생성
        result_df = pd.DataFrame({
            f"{metric_name}(Base)": base[passed_mask],
            f"{metric_name}(Target)": target[passed_mask],
            "Growth_Rate(%)": (rate[passed_mask] * 100).round(2) # 백분율로 변환
        })
        
        # 성장률 높은 순으로 정렬
        result_df.sort_values(by="Growth_Rate(%)", ascending=False, inplace=True)
        
        return result_df

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