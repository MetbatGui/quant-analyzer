"""FinancialDataSourcePort(Outbound Port)를 구현한
엑셀(Excel) 어댑터입니다.
"""

import pandas as pd
from domain.ports.outbound import FinancialDataSourcePort
from domain.model.data_models import FinancialData

class ExcelFinancialDataSource(FinancialDataSourcePort):
    """
    로컬 엑셀 파일에서 재무 데이터를 로드하는 
    FinancialDataSourcePort의 구현체(Adapter)입니다.
    """
    
    _SHEET_MAP = {
        "sales": "매출액",
        "operating_profit": "영업이익",
        "net_income": "당기순이익",
    }

    def __init__(self, file_path: str):
        """
        Args:
            file_path (str): 읽어올 '재무데이터_통합_최종.xlsx' 파일의 경로.
        """
        self.file_path = file_path
        print(f"[Adapter] ExcelDataSource 초기화. 대상 파일: {self.file_path}")

    def load_financial_data(self) -> FinancialData:
        """엑셀 파일에서 시트 3개를 로드하여 FinancialData 객체로 반환합니다.

        Returns:
            FinancialData: 3개의 DataFrame이 포함된 데이터 객체.
        
        Raises:
            FileNotFoundError: 엑셀 파일을 찾을 수 없는 경우.
            Exception: 시트 로딩 중 오류가 발생한 경우.
        """
        try:

            all_sheets = pd.read_excel(
                self.file_path, 
                sheet_name=None,
                index_col=0,
                engine='openpyxl'
            )

            return FinancialData(
                sales=all_sheets[self._SHEET_MAP["sales"]],
                operating_profit=all_sheets[self._SHEET_MAP["operating_profit"]],
                net_income=all_sheets[self._SHEET_MAP["net_income"]]
            )
        
        except FileNotFoundError:
            print(f"🚨 [Adapter] 엑셀 파일 없음: {self.file_path}")
            raise
        except KeyError as e:
            print(f"🚨 [Adapter] 엑셀 시트 이름 오류: {e} 시트를 찾을 수 없습니다.")
            print(f"  (필요한 시트: {list(self._SHEET_MAP.values())})")
            raise
        except Exception as e:
            print(f"🚨 [Adapter] 엑셀 로드 중 알 수 없는 오류: {e}")
            raise