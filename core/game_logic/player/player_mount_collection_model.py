from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from ...random_pcg import RandomPCG
from ..enums import AscendableType, Rarity
from ..stats import SecondaryStats
from ..stats.secondary_stat_helper import SecondaryStatHelper
from .ascension_model import AscensionModel
from .summon_model import SummonModel

if TYPE_CHECKING:
	from .player_model import PlayerModel


@dataclass(frozen=True)
class MountId:
	rarity: Rarity
	id: int


class PlayerMountModel:
	def __init__(
		self,
		guid: str,
		mount_id: MountId,
		secondary_stats: SecondaryStats,
	) -> None:
		self.guid = guid
		self.mount_id = mount_id
		self.secondary_stats = secondary_stats
		self.level = 0
		self.experience = 0
		self.is_equipped = False
		self.is_locked = False

	@staticmethod
	def get_total_level_xp(
		player: PlayerModel,
		mount: PlayerMountModel,
		level: int,
	) -> int:
		from ..stats.experience_helper import _level_info_entries, total_level_xp

		upgrade_config = player.game_config.mount_upgrade_library.get(mount.mount_id.rarity)
		if upgrade_config is None:
			raise ValueError(f"No mount upgrade config for rarity: {mount.mount_id.rarity!r}")
		return total_level_xp(_level_info_entries(upgrade_config), level)

	def get_total_xp(
		self,
		player: PlayerModel,
		level: int | None = None,
		xp: int | None = None,
	) -> int:
		if level is None and xp is None:
			return self.get_total_level_xp(player, self, self.level) + self.experience
		if level is None or xp is None:
			raise TypeError("get_total_xp requires both level and xp, or neither")
		return self.get_total_level_xp(player, self, level) + xp

	@staticmethod
	def calculate_level_and_xp(
		player: PlayerModel,
		mount: PlayerMountModel,
		total_xp: int,
	) -> tuple[int, int]:
		from ..stats.experience_helper import _level_info_entries, calculate_level_and_xp

		upgrade_config = player.game_config.mount_upgrade_library.get(mount.mount_id.rarity)
		if upgrade_config is None:
			raise ValueError(f"No mount upgrade config for rarity: {mount.mount_id.rarity!r}")
		return calculate_level_and_xp(_level_info_entries(upgrade_config), total_xp)


class PlayerMountCollectionModel:
	def __init__(self) -> None:
		self.player_mount_models: list[PlayerMountModel] = []
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Mounts)

	def ascend(self) -> None:
		self.player_mount_models.clear()
		self.summon_model.reset()
		self.ascension_model.ascend()


def create_mount(
	player: PlayerModel,
	mount_id: MountId,
	rng: RandomPCG,
	secondary_stats: SecondaryStats | None = None,
) -> PlayerMountModel:
	game_config = player.game_config
	guid = rng.next_guid()
	ascension_level = player.player_mount_collection_model.ascension_model.current_level
	library = game_config.secondary_stat_pet_unlock_library

	if ascension_level < 1:
		unlock_row = library.get(mount_id.rarity)
	else:
		unlock_row = list(library.values())[-1] if library else None

	if unlock_row is None:
		raise ValueError(f"Missing SecondaryStatPetUnlockLibrary entry for {mount_id.rarity!r}")

	stat_count = int(unlock_row["NumberOfSecondStats"])
	if secondary_stats is None:
		secondary_stats = SecondaryStatHelper.generate_secondary_stats(stat_count, rng)

	return PlayerMountModel(guid, mount_id, secondary_stats)


def create_mount_from_ids(
	player: PlayerModel,
	mount_ids: Sequence[MountId],
	rng: RandomPCG,
	secondary_stats: SecondaryStats | None = None,
) -> PlayerMountModel:
	if not mount_ids:
		raise ValueError("mount_ids must not be empty")
	chosen = rng.choice(list(mount_ids))
	return create_mount(player, chosen, rng, secondary_stats)
