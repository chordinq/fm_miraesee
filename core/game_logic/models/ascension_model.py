from ..enums import AscendableType, AscensionLevel
from config import ASCENSION_CONFIGS_LIBRARY

class AscensionModel:
    def __init__(
        self, 
        ascendable_type: AscendableType, 
        current_level: int = AscensionLevel.None_.value
    ) -> None:
        self.ascendable_type = ascendable_type
        self.current_level = current_level

    def ascend(self) -> None:
        self.current_level += 1

    def descend(self) -> None:
        self.current_level = max(0, self.current_level - 1)

    def get_ascension_configs(self) -> dict | None:
        return ASCENSION_CONFIGS_LIBRARY.get(self.ascendable_type.name)

    def is_maxed(self) -> bool:
        configs = self.get_ascension_configs() or {}
        return self.current_level >= len(configs.get("AscensionConfigPerLevel", []))

    def get_level_stats(self) -> list[dict]:
        if self.current_level == AscensionLevel.None_.value:
            return []

        configs = self.get_ascension_configs()
        level_configs = configs.get("AscensionConfigPerLevel", [])

        index = self.current_level - 1
        
        if 0 <= index < len(level_configs):
            return level_configs[index].get("StatContributions", [])
            
        return []
