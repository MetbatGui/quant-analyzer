"""퀀트 분석기 애플리케이션의 메인 실행 파일(Entrypoint)입니다.

이 파일은 헥사고널 아키텍처의 모든 구성 요소를 조립(Assemble)하고
의존성을 주입(Inject)하는 역할을 합니다.

실행 방법 (프로젝트 루트 '2_Quant_Analyzer'에서):
$ python src/main.py
"""

# --- 1. 경로 설정 ---
# (pwd를 기준으로 한 상대 경로)
STRATEGIES_DIR = "strategies/active"
DATA_FILE_PATH = "data/재무데이터_통합_최종.xlsx"


# --- 2. 모든 구성 요소 임포트 ---

# Outbound Adapters (외부 구현체)
from adapters.outbound.excel_data_source import ExcelFinancialDataSource
from adapters.outbound.toml_strategy_loader import TomlStrategyLoader

# Domain Service (핵심 로직)
from domain.service.screening_service import QuantScreeningService

# Inbound Adapter (실행기)
from adapters.inbound.console_runner import ConsoleRunner


def main():
    """애플리케이션을 조립하고 실행합니다."""
    
    print("[Main] 애플리케이션 조립 시작...")

    # --- 3. Outbound 어댑터 생성 (외부 의존성) ---
    try:
        data_source_adapter = ExcelFinancialDataSource(file_path=DATA_FILE_PATH)
        strategy_loader_adapter = TomlStrategyLoader(active_strategies_path=STRATEGIES_DIR)
        
    except Exception as e:
        print(f"🚨 [Main] Outbound 어댑터 초기화 실패: {e}")
        return

    # --- 4. Domain Service 생성 (핵심 로직) ---
    try:
        quant_service = QuantScreeningService(
            data_source=data_source_adapter,
            strategy_loader=strategy_loader_adapter
        )
    except Exception as e:
        print(f"🚨 [Main] Domain Service 초기화 실패 (데이터/전략 로드 오류): {e}")
        return

    # --- 5. Inbound 어댑터 생성 (실행기) ---
    console_runner = ConsoleRunner(screening_service=quant_service)

    # --- 6. 애플리케이션 실행 ---
    console_runner.run()


if __name__ == "__main__":
    main()