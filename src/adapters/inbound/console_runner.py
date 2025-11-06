"""ScreeningUseCasePort(Inbound Port)를 호출하는
콘솔(Console) 어댑터입니다.
"""

from typing import Dict, List
import pandas as pd
from domain.ports.inbound import ScreeningUseCasePort
from domain.ports.outbound import ResultPersistencePort # <-- (1) 신규 포트 임포트

class ConsoleRunner:
    """
    콘솔 환경에서 UseCase(핵심 로직)를 실행시키고
    결과를 터미널에 출력하는 Inbound Adapter입니다.
    """
    def __init__(
        self, 
        screening_service: ScreeningUseCasePort,
        persistence_adapter: ResultPersistencePort # <--- (2) '저장 포트' 주입
    ):
        """
        Args:
            screening_service (ScreeningUseCasePort): 핵심 서비스(Inbound Port).
            persistence_adapter (ResultPersistencePort): 결과 저장용(Outbound Port).
        """
        self.screening_service = screening_service
        self.persistence_adapter = persistence_adapter # <--- (3) 저장 어댑터 할당
        print("[Adapter] ConsoleRunner 초기화. UseCase 및 Persistence가 주입되었습니다.")

    def run(self):
        """스크리닝을 실행하고 결과를 콘솔에 출력합니다."""
        print("\n" + "="*30)
        print("🚀 퀀트 스크리닝 실행을 시작합니다...")
        print("="*30)

        # 1. Inbound Port를 호출하여 핵심 로직 실행
        results = self.screening_service.run_all_active_strategies()

        # 2. (NEW) 결과 저장 - Outbound Port 호출
        try:
            self.persistence_adapter.save_results(results)
        except Exception as e:
            print(f"🚨 [Adapter] 결과 저장 중 오류 발생: {e}")

        print("\n" + "="*30)
        print("🏁 모든 전략 실행 완료. 최종 결과:")
        print("="*30)
        
        # 3. 결과 출력 (프레젠테이션 로직)
        self._print_results(results)

    def _print_results(self, results: Dict[str, pd.DataFrame]):
        """스크리닝 결과를 콘솔에 예쁘게 출력합니다."""
        
        if not results:
            print("\n실행된 전략이 없거나 결과가 없습니다.")
            return

        for strategy_name, result_df in results.items():
            print(f"\n--- [전략: {strategy_name}] ---")
            
            if result_df.empty:
                print("  -> 통과한 종목 없음")
            else:
                print(f"  -> 총 {len(result_df)}개 종목 통과:")
                
                # DataFrame을 문자열로 이쁘게 출력 (Pandas 기능)
                with pd.option_context('display.width', 1000, 'display.max_rows', None):
                    print(result_df.to_string())