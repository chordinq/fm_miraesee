# models/EquipmentModel.py
from configs.enums import ItemType
from models.ItemModel import ItemModel

class EquipmentModel:
    def __init__(self):
        # 장착된 아이템 (ItemType -> ItemModel)
        self.equipped_items = {itype: None for itype in ItemType}
        
        # HiddenItemLevels: ItemType -> Age -> Level
        self.hidden_levels = {itype: {} for itype in ItemType}
        
        # ItemRoundRobin: ItemType -> Age -> [idx_1, idx_2, ...] (비트마스크를 리스트로 복원하여 저장)
        self.round_robin = {itype: {} for itype in ItemType}

    def equip_item(self, item: ItemModel):
        """특정 부위에 아이템을 장착합니다."""
        self.equipped_items[item.item_type] = item

    def get_equipped_item(self, item_type: ItemType) -> ItemModel:
        """해당 부위에 장착된 아이템을 반환합니다."""
        return self.equipped_items.get(item_type)

    def set_hidden_level(self, item_type: ItemType, age: int, level: int):
        self.hidden_levels[item_type][age] = level

    def set_round_robin(self, item_type: ItemType, age: int, indices: list):
        self.round_robin[item_type][age] = indices