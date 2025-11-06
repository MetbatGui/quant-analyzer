"""퀀트 분석기 애플리케이션의 메인 실행 파일(Entrypoint)입니다.
...
"""

# --- 1. 경로 설정 ---
STRATEGIES_DIR = "strategies/active"
DATA_FILE_PATH = "data/재무데이터_통합_최종.xlsx"
# (NEW) Excel 저장 경로
XLSX_OUTPUT_FILE = "output/results/quant_screening_results.xlsx" 


# --- 2. 모든 구성 요소 임포트 ---
from adapters.outbound.excel_data_source import ExcelFinancialDataSource
from adapters.outbound.toml_strategy_loader import TomlStrategyLoader
# (CHANGE) CSV 대신 Excel 어댑터 임포트
from adapters.outbound.excel_result_persistence import ExcelResultPersistenceAdapter

from domain.service.screening_service import QuantScreeningService
from adapters.inbound.console_runner import ConsoleRunner


def main():
    """애플리케이션을 조립하고 실행합니다."""
    
    print("[Main] 애플리케이션 조립 시작...")

    # --- 3. Outbound 어댑터 생성 (외부 의존성) ---
    try:
        data_source_adapter = ExcelFinancialDataSource(file_path=DATA_FILE_PATH)
        strategy_loader_adapter = TomlStrategyLoader(active_strategies_path=STRATEGIES_DIR)
        
        # (CHANGE) CSV 어댑터 대신 Excel 어댑터 생성
        persistence_adapter = ExcelResultPersistenceAdapter(
            output_file_path=XLSX_OUTPUT_FILE
        )
        
    except Exception as e:
        print(f"🚨 [Main] Outbound 어댑터 초기화 실패: {e}")
        return

    # --- 4. Domain Service 생성 (핵심 로직) ---
    # (이 부분은 전혀 수정할 필요가 없습니다)
    try:
        quant_service = QuantScreeningService(
            data_source=data_source_adapter,
            strategy_loader=strategy_loader_adapter
        )
    except Exception as e:
        print(f"🚨 [Main] Domain Service 초기화 실패 (데이터/전략 로드 오류): {e}")
        return

    # --- 5. Inbound 어댑터 생성 (실행기) ---
    # (이 부분도 'persistence_adapter'가 포트 타입이라 수정할 필요가 없습니다)
    console_runner = ConsoleRunner(
        screening_service=quant_service,
        persistence_adapter=persistence_adapter
    )

    # --- 6. 애플리케이션 실행 ---
    console_runner.run()


if __name__ == "__main__":
    main()