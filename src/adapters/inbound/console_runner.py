"""ScreeningUseCasePort(Inbound Port)를 호출하는
콘솔(Console) 어댑터입니다.
"""

from typing import Dict, List
from domain.ports.inbound import ScreeningUseCasePort

class ConsoleRunner:
    """
    콘솔 환경에서 UseCase(핵심 로직)를 실행시키고
    결과를 터미널에 출력하는 Inbound Adapter입니다.
    """
    def __init__(self, screening_service: ScreeningUseCasePort):
        """
        Args:
            screening_service (ScreeningUseCasePort): 실행할
                핵심 서비스(Inbound Port)를 주입받습니다.
        """
        self.screening_service = screening_service
        print("[Adapter] ConsoleRunner 초기화. UseCase가 주입되었습니다.")

    def run(self):
        """스크리닝을 실행하고 결과를 콘솔에 출력합니다."""
        print("\n" + "="*30)
        print("🚀 퀀트 스크리닝 실행을 시작합니다...")
        print("="*30)

        # 1. Inbound Port를 호출하여 핵심 로직 실행
        results = self.screening_service.run_all_active_strategies()

        print("\n" + "="*30)
        print("🏁 모든 전략 실행 완료. 최종 결과:")
        print("="*30)
        
        # 2. 결과 출력 (프레젠테이션 로직)
        self._print_results(results)

    def _print_results(self, results: Dict[str, List[str]]):
        """스크리닝 결과를 콘솔에 예쁘게 출력합니다."""
        
        if not results:
            print("\n실행된 전략이 없거나 결과가 없습니다.")
            return

        for strategy_name, stocks in results.items():
            print(f"\n--- [전략: {strategy_name}] ---")
            if not stocks:
                print("  -> 통과한 종목 없음")
            else:
                print(f"  -> 총 {len(stocks)}개 종목 통과:")
                for i, stock in enumerate(stocks):
                    print(f"    {i+1}. {stock}")