"""配置管理模块"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""

    def __init__(self, base_dir: str = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path(__file__).parent.parent
        self.config_path = self.base_dir / 'config.yaml'

    def config_exists(self) -> bool:
        """检查配置文件是否存在"""
        return self.config_path.exists()

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if not self.config_exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_config(self, config: Dict[str, Any]) -> None:
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        if not self.config_exists():
            return None
        config = self.load_config()
        return config.get('api', {}).get('key')

    def get_keywords(self) -> list:
        """获取关键词列表"""
        if not self.config_exists():
            return []
        config = self.load_config()
        return config.get('keywords', [])

    def get_filters(self) -> Dict[str, Any]:
        """获取筛选条件"""
        if not self.config_exists():
            return {}
        config = self.load_config()
        return config.get('filters', {})

    def get_cost_control(self) -> Dict[str, Any]:
        """获取成本控制配置"""
        if not self.config_exists():
            return {}
        config = self.load_config()
        return config.get('cost_control', {
            'max_articles_per_day': 50,
            'max_interaction_queries': 35,
            'max_wx_index_queries': 10,
            'daily_budget': 10.0
        })

    def estimate_cost(self, num_keywords: int) -> float:
        """估算成本"""
        cost_control = self.get_cost_control()

        # 预估文章数
        estimated_articles = num_keywords * 10
        estimated_articles = min(estimated_articles, cost_control.get('max_articles_per_day', 50))

        # 计算各API成本
        cost_api_39 = estimated_articles * 0.02  # 爆文API
        cost_api_17 = min(estimated_articles, cost_control.get('max_interaction_queries', 35)) * 0.06  # 互动数据
        cost_api_38 = cost_control.get('max_wx_index_queries', 10) * 0.5  # 微信指数

        return cost_api_39 + cost_api_17 + cost_api_38
