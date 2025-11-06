"""StrategyLoaderPort(Outbound Port)를 구현한
TOML 파일 어댑터입니다.
"""

import glob
import os
from typing import Dict
import tomllib

from domain.ports.outbound import StrategyLoaderPort
from domain.model.criteria import Criteria, QoQCriteria


class TomlStrategyLoader(StrategyLoaderPort):
    """
    TOML 파일 시스템으로부터 'active' 전략을 로드하는 
    StrategyLoaderPort의 구현체(Adapter)입니다.
    """
    def __init__(self, active_strategies_path: str):
        """
        Args:
            active_strategies_path (str): 'strategies/active' 폴더 경로.
        """
        self.active_path = active_strategies_path
        print(f"[Adapter] TomlStrategyLoader 초기화. Active 경로: {self.active_path}")

    def load_active_strategies(self) -> Dict[str, Criteria]:
        """'active' 폴더에서 TOML을 스캔하여 Criteria 객체 딕셔너리를 생성합니다.

        Returns:
            Dict[str, Criteria]: {전략_이름: Criteria_객체} 딕셔너리.
        """
        strategies = {}
        search_path = os.path.join(self.active_path, "*.toml")
        
        for file_path in glob.glob(search_path):
            strategy_name = os.path.basename(file_path).replace('.toml', '')
            
            try:
                with open(file_path, "rb") as f:
                    config = tomllib.load(f)
                
                criteria = self._parse_criteria_config(config)
                strategies[strategy_name] = criteria

            except Exception as e:
                print(f"🚨 [Adapter] '{strategy_name}' (Active) 전략 로드 실패: {e}")
                
        print(f"[Adapter] {len(strategies)}개의 Active 전략 로드 완료.")
        return strategies

    def _parse_criteria_config(self, config: Dict) -> Criteria:
        """TOML config 딕셔너리를 적절한 Criteria 객체로 파싱합니다.
        
        Args:
            config (Dict): tomllib.load()로 읽어온 딕셔너리.

        Returns:
            Criteria: 파싱된 Criteria 객체 (예: QoQCriteria).
        
        Raises:
            ValueError: 알 수 없는 Criteria type이거나 'criteria' 키가 없는 경우.
        """
        criteria_data = config.get('criteria')
        if not criteria_data:
            raise ValueError("TOML에 'criteria' 섹션이 없습니다.")
            
        criteria_type = criteria_data.get('type')

        if criteria_type == 'QoQ_Growth':
            return QoQCriteria(
                metric=criteria_data['metric'],
                base_quarter=criteria_data['base_quarter'],
                target_quarter=criteria_data['target_quarter'],
                min_growth_pct=criteria_data['min_growth_pct']
            )
        
        raise ValueError(f"알 수 없는 Criteria type ({criteria_type})")