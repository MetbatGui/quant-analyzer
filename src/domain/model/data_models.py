"""재무 데이터(DTO)를 정의하는 도메인 모델입니다.

FinancialDataSourcePort가 외부에서 데이터를 읽어와
이 객체에 담아 도메인 서비스(Service)로 전달합니다.
"""

import pandas as pd
from dataclasses import dataclass


@dataclass(frozen=True)
class FinancialData:
    """모든 재무제표 데이터를 담는 데이터 전송 객체(DTO)입니다.

    Attributes:
        sales (pd.DataFrame): 매출액 (행: 종목, 열: 분기).
        operating_profit (pd.DataFrame): 영업이익 (행: 종목, 열: 분기).
        net_income (pd.DataFrame): 당기순이익 (행: 종목, 열: 분기).
    """
    sales: pd.DataFrame
    operating_profit: pd.DataFrame
    net_income: pd.DataFrame