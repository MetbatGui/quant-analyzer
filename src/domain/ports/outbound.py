"""도메인 서비스가 외부 데이터/기능을 요청하기 위한 아웃바운드 포트(Outbound Ports)입니다.

아웃바운드 어댑터(예: ExcelDataSource, TomlStrategyLoader)는
이 포트를 구현(implement)하여 실제 데이터를 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict
from domain.model.criteria import Criteria
from domain.model.data_models import FinancialData


class FinancialDataSourcePort(ABC):
    """외부에서 원본 재무 데이터를 로드하기 위한 포트입니다."""

    @abstractmethod
    def load_financial_data(self) -> FinancialData:
        """
        데이터 소스(예: 엑셀)에서 모든 재무제표를 로드하여
        FinancialData 객체로 반환합니다.
        
        Returns:
            FinancialData: 매출액, 영업이익, 당기순이익 DataFrame을 포함한 객체.
        """
        pass


class StrategyLoaderPort(ABC):
    """외부(예: TOML 파일)에서 전략(Criteria)을 로드하기 위한 포트입니다."""

    @abstractmethod
    def load_active_strategies(self) -> Dict[str, Criteria]:
        """
        활성화된 모든 전략을 로드합니다.

        Returns:
            Dict[str, Criteria]: {전략_이름: Criteria_객체} 딕셔너리.
        """
        pass