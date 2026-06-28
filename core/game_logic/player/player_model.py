from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any
from . import player_item_stats as pmi
from .player_currency_model import PlayerCurrencyModel
from .player_equipment_model import PlayerEquipmentModel
from ..enums import ItemType
from .player_forge_model import PlayerForgeModel
from .player_mount_collection_model import PlayerMountCollectionModel
from .player_pet_collection_model import PlayerPetCollectionModel
from .player_power_model import PlayerPowerModel
from .player_sets_model import PlayerSetsModel
from .player_skill_collection_model import PlayerSkillCollectionModel
from .player_skin_collection_model import PlayerSkinCollectionModel
from .player_techtree_model import PlayerTechTreeModel

if TYPE_CHECKING:
	from ..shared_game_config import SharedGameConfig


class PlayerModel:
	def __init__(self, game_config: SharedGameConfig | Any | None = None) -> None:
		self._game_config = game_config
		self.player_currency_model = PlayerCurrencyModel()
		self.player_forge_model = PlayerForgeModel()
		self.player_equipment_model = PlayerEquipmentModel()
		self.player_skill_collection_model = PlayerSkillCollectionModel()
		self.player_power_model = PlayerPowerModel()
		self.player_techtree_model = PlayerTechTreeModel()
		self.player_pet_collection_model = PlayerPetCollectionModel()
		self.player_mount_collection_model = PlayerMountCollectionModel()
		self.player_skin_collection_model = PlayerSkinCollectionModel()
		self.sets_model = PlayerSetsModel()
		self._server_time_seconds: int = 0
		self._wall_clock_server_time: bool = False

	def get_server_time(self) -> int:
		"""IL: PlayerModel.get_ServerTime — sim clock, or wall clock after dump load."""
		if self._wall_clock_server_time:
			return int(time.time())
		return self._server_time_seconds

	def enable_wall_clock_server_time(self) -> None:
		self._wall_clock_server_time = True

	def advance_server_time(self, seconds: int) -> None:
		self._wall_clock_server_time = False
		self._server_time_seconds += seconds

	@property
	def game_config(self) -> Any:
		if self._game_config is not None:
			return self._game_config
		from ..stats.pet_stats import load_pet_stats_config

		return load_pet_stats_config()

	@property
	def is_ranged(self) -> bool:
		weapon = self.player_equipment_model.weapon
		if weapon is None:
			return False
		if weapon.item_id.Type != ItemType.Weapon:
			return False
		config = self._game_config
		if config is None:
			return False
		weapon_info = getattr(config, "weapons", {}).get(weapon.item_id)
		if weapon_info is None:
			return False
		return bool(weapon_info.get("IsRanged", False))


PlayerModel.get_total_stats = pmi.get_total_stats
PlayerModel.calculate_total_stats = pmi.calculate_total_stats
PlayerModel.get_base_stats = pmi.get_base_stats
PlayerModel.get_all_secondary_stats = pmi.get_all_secondary_stats
PlayerModel.get_ascension_stats = pmi.get_ascension_stats
PlayerModel.get_base_item_stats = pmi.get_base_item_stats
PlayerModel.get_resolved_item_stats = pmi.get_resolved_item_stats
