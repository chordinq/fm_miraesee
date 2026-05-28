# ui/widgets/equipped_collection_bar.py — equipped strip for pet / skill / mount tabs
from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.player_model.SkillModel import SkillModel
from ui.theme.colors import RARITY_FRAME
from ui.theme.metrics import (
    EQUIPPED_BAR_HEIGHT,
    EQUIPPED_BAR_SLOT_GAP,
    EQUIPPED_BAR_SLOT_H,
    EQUIPPED_BAR_SLOT_ICON,
    EQUIPPED_BAR_SLOT_W,
)
from ui.services.collection_selection import CollectionSelection
from ui.services.display_level import format_level
from ui.services.pixmap_util import default_device_pixel_ratio
from ui.services.sheet_sprites import mount_icon_pixmap, pet_icon_pixmap, skill_icon_pixmap
from ui.widgets.equipped_ribbon import EquippedRibbon
from ui.widgets.icon_frames import RarityFramedIcon, SkillIconDisc
from ui.widgets.outlined_label import tile_caption_label
from ui.widgets.selectable_widget import SelectableWidget

EquippedKind = Literal["pet", "skill", "mount"]


def _equipped_pets(player: PlayerModel) -> list[PetModel]:
    pets = [p for p in player.pets.pets if p.is_equipped]
    pets.sort(key=lambda p: (p.equip_slot, -int(p.rarity), -p.level))
    return pets


def _equipped_skills(player: PlayerModel) -> list[SkillModel]:
    skills = [s for s in player.skills.skills.values() if s.is_equipped]
    skills.sort(key=lambda s: (s.equip_slot, int(s.rarity), int(s.combat_skill)))
    return skills


def _equipped_mounts(player: PlayerModel) -> list[MountModel]:
    mounts = [m for m in player.mounts.mounts if m.is_equipped]
    mounts.sort(key=lambda m: (-int(m.rarity), -m.level, m.mount_id))
    return mounts


class _EquippedItemSlot(SelectableWidget):
    def __init__(
        self,
        selection: CollectionSelection,
        *,
        icon: QWidget,
        caption: str,
        on_select: Callable[[CollectionSelection], None],
        slot_w: int,
        slot_h: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._selection = selection
        self._icon = icon
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: on_select(self._selection))

        col = QVBoxLayout(self)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        col.addWidget(icon, 0, Qt.AlignmentFlag.AlignHCenter)
        level = tile_caption_label(caption)
        col.addWidget(level, 0, Qt.AlignmentFlag.AlignHCenter)
        self.setFixedSize(slot_w, slot_h)

    def set_selected(self, selected: bool) -> None:  # noqa: D102
        super().set_selected(selected)
        if hasattr(self._icon, "set_selected"):
            self._icon.set_selected(selected)


class EquippedCollectionBar(QWidget):
    """Ribbon + equipped item icons (embedded in collection tab sub-header)."""

    item_selected = Signal(object)

    def __init__(
        self,
        player: PlayerModel,
        kind: EquippedKind,
        *,
        embedded: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._player = player
        self._kind = kind
        self._embedded = embedded
        self._slots: list[_EquippedItemSlot] = []
        self.setObjectName(f"Equipped{kind.title()}Bar")
        self.setFixedHeight(EQUIPPED_BAR_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background: transparent;")

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self._ribbon = EquippedRibbon(self)
        outer.addWidget(self._ribbon, 0, Qt.AlignmentFlag.AlignVCenter)
        self._slots_host = QWidget(self)
        self._slots_host.setStyleSheet("background: transparent;")
        self._slots_layout = QHBoxLayout(self._slots_host)
        self._slots_layout.setContentsMargins(0, 0, 0, 0)
        self._slots_layout.setSpacing(EQUIPPED_BAR_SLOT_GAP)
        self._slots_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        outer.addWidget(
            self._slots_host,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        self.refresh()

    def set_selection(self, selection: CollectionSelection | None) -> None:
        for slot in self._slots:
            sel = slot._selection  # noqa: SLF001
            match = False
            if selection is not None and selection.kind == sel.kind == self._kind:
                if self._kind == "pet" and selection.pet is sel.pet:
                    match = True
                elif self._kind == "skill" and selection.skill is sel.skill:
                    match = True
                elif self._kind == "mount" and selection.mount is sel.mount:
                    match = True
            slot.set_selected(match)

    def refresh(self) -> None:
        self._ribbon.refresh_locale()
        while self._slots_layout.count():
            item = self._slots_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._slots.clear()

        for selection, icon, caption, slot_w, slot_h in self._build_slots():
            slot = _EquippedItemSlot(
                selection,
                icon=icon,
                caption=caption,
                on_select=self._on_item_clicked,
                slot_w=slot_w,
                slot_h=slot_h,
                parent=self._slots_host,
            )
            self._slots_layout.addWidget(slot)
            self._slots.append(slot)
        self.update()

    def _build_slots(self):
        dpr = default_device_pixel_ratio()
        if self._kind == "pet":
            for pet in _equipped_pets(self._player):
                frame = RARITY_FRAME.get(int(pet.rarity), "#4db84a")
                icon = RarityFramedIcon(
                    EQUIPPED_BAR_SLOT_ICON,
                    kind="pet",
                )
                icon.set_content(
                    frame_color=frame,
                    pixmap=pet_icon_pixmap(
                        pet,
                        EQUIPPED_BAR_SLOT_ICON,
                        device_pixel_ratio=dpr,
                    ),
                )
                yield (
                    CollectionSelection(kind="pet", pet=pet),
                    icon,
                    format_level(pet.level),
                    EQUIPPED_BAR_SLOT_W,
                    EQUIPPED_BAR_SLOT_H,
                )
        elif self._kind == "skill":
            for skill in _equipped_skills(self._player):
                frame = RARITY_FRAME.get(int(skill.rarity), "#4db84a")
                icon = SkillIconDisc(EQUIPPED_BAR_SLOT_ICON)
                icon.set_content(
                    tint_color=frame,
                    skill_pixmap=skill_icon_pixmap(
                        skill,
                        EQUIPPED_BAR_SLOT_ICON,
                        device_pixel_ratio=dpr,
                    ),
                )
                yield (
                    CollectionSelection(kind="skill", skill=skill),
                    icon,
                    format_level(skill.level),
                    EQUIPPED_BAR_SLOT_W,
                    EQUIPPED_BAR_SLOT_H,
                )
        else:
            for mount in _equipped_mounts(self._player):
                frame = RARITY_FRAME.get(int(mount.rarity), "#4db84a")
                icon = RarityFramedIcon(
                    EQUIPPED_BAR_SLOT_ICON,
                    kind="mount",
                )
                icon.set_content(
                    frame_color=frame,
                    pixmap=mount_icon_pixmap(
                        mount,
                        EQUIPPED_BAR_SLOT_ICON,
                        device_pixel_ratio=dpr,
                    ),
                )
                yield (
                    CollectionSelection(kind="mount", mount=mount),
                    icon,
                    format_level(mount.level),
                    EQUIPPED_BAR_SLOT_W,
                    EQUIPPED_BAR_SLOT_H,
                )

    def _on_item_clicked(self, selection: CollectionSelection) -> None:
        self.set_selection(selection)
        self.item_selected.emit(selection)

    def paintEvent(self, _event) -> None:  # noqa: N802
        if self._embedded:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1e1e1e"))
        painter.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), 8, 8)
