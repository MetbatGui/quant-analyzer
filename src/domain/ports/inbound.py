"""도메인 서비스를 실행하기 위한 인바운드 포트(Inbound Ports)입니다.

인바운드 어댑터(예: ConsoleRunner, ApiRunner)는 이 포트를 호출하여
핵심 비즈니스 로직을 실행시킵니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd


class ScreeningUseCasePort(ABC):
    """
    외부(Inbound)에서 핵심 로직을 실행하기 위한
    추상 인터페이스(Port)입니다.
    
    'UseCase'는 사용자의 특정 시나리오(예: '스크리닝 실행')를 의미합니다.
    """

    @abstractmethod
    def run_all_active_strategies(self) -> Dict[str, pd.DataFrame]:
        """
        활성화된 모든 전략을 실행합니다.

        Returns:
            Dict[str, pd.DataFrame]: 
                {전략_이름: [결과 DataFrame]} 딕셔너리.
                DataFrame은 종목명을 인덱스로, 근거 데이터(실적, 성장률)를
                컬럼으로 가집니다.
        """
        pass