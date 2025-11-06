"""ResultPersistencePort(Outbound Port)를 구현한
Excel (.xlsx) 파일 저장 어댑터입니다.

(openpyxl 라이브러리가 필요합니다: pip install openpyxl)
"""

import os
import pandas as pd
from typing import Dict
from domain.ports.outbound import ResultPersistencePort

class ExcelResultPersistenceAdapter(ResultPersistencePort):
    """
    스크리닝 결과를 단일 .xlsx 파일의 여러 시트로 저장하는
    ResultPersistencePort의 구현체(Adapter)입니다.
    """
    def __init__(self, output_file_path: str):
        """
        Args:
            output_file_path (str): 저장할 .xlsx 파일의 전체 경로.
        """
        self.output_file_path = output_file_path
        self.output_dir = os.path.dirname(output_file_path)
        print(f"[Adapter] ExcelResultPersistence 초기화. 저장 파일: {self.output_file_path}")
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"[Adapter] 생성된 출력 폴더: {self.output_dir}")

    def save_results(self, results: Dict[str, pd.DataFrame]):
        """결과 딕셔너리를 단일 Excel 파일의 여러 시트로 저장합니다."""
        
        print(f"\n[Adapter] {len(results)}개의 결과 Excel 파일로 저장 시작...")
        
        try:
            # (1) ExcelWriter 객체 생성
            with pd.ExcelWriter(self.output_file_path, engine='openpyxl') as writer:
                
                for strategy_name, result_df in results.items():
                    
                    # (2) 시트 이름 생성 (파일 이름과 달리 31자 제한 고려)
                    # (간단히 앞 30자만 사용)
                    sheet_name = strategy_name[:30] 
                    
                    # (3) 각 DataFrame을 별도 시트에 저장
                    # (index=True: 종목명(인덱스)을 첫 번째 열로 저장)
                    result_df.to_excel(
                        writer, 
                        sheet_name=sheet_name, 
                        index=True
                    )
                    print(f"  -> '{sheet_name}' 시트 저장 완료.")
                    
            print(f"  -> 저장 완료: {self.output_file_path}")
            
        except Exception as e:
            print(f"  🚨 저장 실패: {self.output_file_path} ({e})")