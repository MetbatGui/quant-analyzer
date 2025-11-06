import os
import pandas as pd
from typing import Dict
from domain.ports.outbound import ResultPersistencePort

class CsvResultPersistenceAdapter(ResultPersistencePort):
    """
    스크리닝 결과를 로컬 CSV 파일로 저장하는
    ResultPersistencePort의 구현체(Adapter)입니다.
    """
    def __init__(self, output_directory: str):
        """
        Args:
            output_directory (str): CSV 파일을 저장할 폴더 경로.
        """
        self.output_dir = output_directory
        print(f"[Adapter] CsvResultPersistence 초기화. 저장 경로: {self.output_dir}")
        
        # (폴더가 없으면 생성)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_results(self, results: Dict[str, pd.DataFrame]):
        """결과 딕셔너리를 순회하며 CSV 파일로 저장합니다."""
        
        print(f"[Adapter] {len(results)}개의 결과 CSV 파일로 저장 시작...")
        for strategy_name, result_df in results.items():
            
            # 파일명 생성 (예: op_qoq_growth_23q1_q2.csv)
            filename = f"{strategy_name}.csv"
            file_path = os.path.join(self.output_dir, filename)
            
            try:
                # DataFrame을 CSV로 저장 (index=True로 종목명 포함)
                result_df.to_csv(file_path, index=True, encoding='utf-8-sig')
                print(f"  -> 저장 완료: {file_path}")
                
            except Exception as e:
                print(f"  🚨 저장 실패: {filename} ({e})")