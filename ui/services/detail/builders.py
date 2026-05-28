from __future__ import annotations

from core.game_logic.pet_egg_hatch import predict_hatch
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.ItemModel import ItemModel
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.player_model.SkillModel import SkillModel

from ui.services.detail.types import DETAIL_ICON_SIZE, DetailContent
from ui.services.display_level import format_level
from ui.services.item_sprites import item_icon_pixmap
from ui.services.localization import (
    combat_skill_display_name,
    egg_label,
    item_display_name,
    item_type_display_name,
    mount_display_name,
    pet_display_name,
    rarity_display_name,
    skill_display_name,
)
from ui.services.pixmap_util import default_device_pixel_ratio
from ui.services.sheet_sprites import (
    egg_icon_pixmap,
    mount_icon_pixmap,
    pet_icon_pixmap,
    skill_icon_pixmap,
)
from ui.services.stat_display import (
    item_detail_stat_lines,
    pet_detail_stat_lines,
    stat_lines_for,
)
from ui.theme.colors import AGE_COLORS, RARITY_COLORS, RARITY_FRAME


def _rarity_title(rarity, name: str) -> str:
    return f"[{rarity_display_name(rarity)}] {name}"


def _rarity_color(rarity) -> str:
    return RARITY_COLORS.get(int(rarity), "#e0e0e0")


def content_for_pet(pet: PetModel, player: PlayerModel | None = None) -> DetailContent:
    dpr = default_device_pixel_ratio()
    return DetailContent(
        title=_rarity_title(pet.rarity, pet_display_name(pet)),
        level_text=format_level(pet.level),
        pixmap=pet_icon_pixmap(pet, DETAIL_ICON_SIZE, device_pixel_ratio=dpr),
        frame_color=RARITY_FRAME.get(int(pet.rarity), "#4db84a"),
        icon_kind="pet",
        title_color=_rarity_color(pet.rarity),
        equipped=False,
        stat_lines=pet_detail_stat_lines(
            pet.rarity,
            pet.pet_id,
            pet.secondary_stats,
            dump_level=pet.level,
            player=player,
        ),
    )


def content_for_egg(egg: EggModel, player: PlayerModel | None = None) -> DetailContent:
    dpr = default_device_pixel_ratio()
    pred = predict_hatch(egg, player)
    preview = PetModel(pred.pet_idx, pred.rarity)
    return DetailContent(
        title=_rarity_title(pred.rarity, pet_display_name(preview)),
        subtitle=egg_label(),
        pixmap=pet_icon_pixmap(preview, DETAIL_ICON_SIZE, device_pixel_ratio=dpr),
        frame_color=RARITY_FRAME.get(int(pred.rarity), "#4db84a"),
        icon_kind="pet",
        title_color=_rarity_color(pred.rarity),
        stat_lines=pet_detail_stat_lines(
            pred.rarity,
            pred.pet_idx,
            pred.secondary_stats,
            dump_level=0,
            player=player,
        ),
        hint="",
        is_hatch_preview=True,
    )


def content_for_mount(mount: MountModel) -> DetailContent:
    dpr = default_device_pixel_ratio()
    return DetailContent(
        title=_rarity_title(mount.rarity, mount_display_name(mount)),
        level_text=format_level(mount.level),
        pixmap=mount_icon_pixmap(mount, DETAIL_ICON_SIZE, device_pixel_ratio=dpr),
        frame_color=RARITY_FRAME.get(int(mount.rarity), "#4db84a"),
        icon_kind="mount",
        title_color=_rarity_color(mount.rarity),
        equipped=False,
        stat_lines=stat_lines_for(mount.secondary_stats, dump_level=mount.level),
    )


def content_for_skill(skill: SkillModel) -> DetailContent:
    dpr = default_device_pixel_ratio()
    return DetailContent(
        title=_rarity_title(skill.rarity, skill_display_name(skill)),
        level_text=format_level(skill.level),
        pixmap=skill_icon_pixmap(skill, DETAIL_ICON_SIZE),
        frame_color=RARITY_FRAME.get(int(skill.rarity), "#4db84a"),
        icon_kind="skill",
        title_color=_rarity_color(skill.rarity),
        equipped=False,
        subtitle=combat_skill_display_name(skill.combat_skill),
    )


def content_for_item(item: ItemModel) -> DetailContent:
    dpr = default_device_pixel_ratio()
    age = int(item.age)
    age_color = AGE_COLORS.get(age, "#e0e0e0")
    return DetailContent(
        title=item_display_name(item),
        level_text=format_level(item.level),
        pixmap=item_icon_pixmap(item, DETAIL_ICON_SIZE, device_pixel_ratio=dpr),
        frame_color=age_color,
        icon_kind="equipment",
        title_color=age_color,
        level_color=age_color,
        subtitle=item_type_display_name(item.item_type),
        stat_lines=item_detail_stat_lines(
            item.secondary_stats,
            dump_level=item.level,
        ),
    )
