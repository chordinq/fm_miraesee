# ui/widgets/item_detail_panel.py — pet / egg hatch preview / mount / skill / equipment info
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.theme.colors import BG, FG, FG_MUTED
from ui.theme.fonts import OUTLINE_FILL
from ui.widgets.outlined_label import detail_title_label, tile_caption_label
from ui.theme.metrics import (
    DETAIL_ICON_FRAME_SIZE,
    DETAIL_ICON_STACK_W,
    EQUIPPED_BADGE_DETAIL,
)
from ui.paint.item_icons import (
    paint_equipment_icon,
    paint_mount_icon,
    paint_pet_icon,
    paint_skill_icon,
)
from ui.services.detail_content import DetailContent, DetailIconKind
from ui.widgets.equipped_badge import EquippedBadge


class _DetailIconFrame(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(DETAIL_ICON_FRAME_SIZE, DETAIL_ICON_FRAME_SIZE)
        self._frame_color = "#4db84a"
        self._pixmap: QPixmap | None = None
        self._icon_kind: DetailIconKind = "pet"
        self._apply_background_attr()

    def _apply_background_attr(self) -> None:
        translucent = self._icon_kind == "skill"
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, translucent)

    def set_content(
        self,
        *,
        frame_color: str,
        pixmap: QPixmap | None,
        icon_kind: DetailIconKind = "pet",
    ) -> None:
        self._frame_color = frame_color
        self._pixmap = pixmap
        self._icon_kind = icon_kind
        self._apply_background_attr()
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        dpr = self.devicePixelRatioF()
        if self._icon_kind == "skill":
            paint_skill_icon(
                painter,
                self.rect(),
                tint_color=self._frame_color,
                skill_pixmap=self._pixmap,
                device_pixel_ratio=dpr,
            )
        elif self._icon_kind == "mount":
            paint_mount_icon(
                painter,
                self.rect(),
                frame_color=self._frame_color,
                pixmap=self._pixmap,
                device_pixel_ratio=dpr,
            )
        elif self._icon_kind == "equipment":
            paint_equipment_icon(
                painter,
                self.rect(),
                frame_color=self._frame_color,
                pixmap=self._pixmap,
                device_pixel_ratio=dpr,
            )
        else:
            paint_pet_icon(
                painter,
                self.rect(),
                frame_color=self._frame_color,
                pixmap=self._pixmap,
                device_pixel_ratio=dpr,
            )


class _DetailIconStack(QWidget):
    """Icon frame centered in a wider stack so Equipped badge is not clipped."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(DETAIL_ICON_STACK_W, DETAIL_ICON_FRAME_SIZE)
        self._frame = _DetailIconFrame(self)
        self._badge = EquippedBadge(self)
        self._layout_children()

    def _layout_children(self) -> None:
        icon_x = (DETAIL_ICON_STACK_W - DETAIL_ICON_FRAME_SIZE) // 2
        self._frame.move(icon_x, 0)
        if self._badge.isVisible():
            self._badge.place(EQUIPPED_BADGE_DETAIL)
            self._badge.raise_()
        self._frame.raise_()

    def set_content(
        self,
        *,
        frame_color: str,
        pixmap: QPixmap | None,
        equipped: bool,
        icon_kind: DetailIconKind = "pet",
    ) -> None:
        self._frame.set_content(
            frame_color=frame_color,
            pixmap=pixmap,
            icon_kind=icon_kind,
        )
        self._badge.refresh_text()
        if equipped:
            self._badge.show()
        else:
            self._badge.hide()
        self._layout_children()


class ItemDetailPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ItemDetailPanel")
        self.setMinimumWidth(260)
        self.setStyleSheet(f"QWidget#ItemDetailPanel {{ background-color: {BG}; }}")

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(4)
        left.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self._icon = _DetailIconStack()
        left.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignHCenter)
        self._level = tile_caption_label()
        left.addWidget(self._level, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addLayout(left, 0)

        right = QVBoxLayout()
        right.setSpacing(6)
        right.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._title = detail_title_label()
        right.addWidget(self._title, 0, Qt.AlignmentFlag.AlignLeft)

        self._subtitle = QLabel("")
        self._subtitle.setStyleSheet(
            f"color: {FG_MUTED}; font-size: 11pt; background: transparent;"
        )
        right.addWidget(self._subtitle)

        self._stats_host = QVBoxLayout()
        self._stats_host.setSpacing(4)
        right.addLayout(self._stats_host)

        self._hint = QLabel("")
        self._hint.setWordWrap(True)
        self._hint.setStyleSheet(
            f"color: {FG_MUTED}; font-size: 10pt; font-style: italic; background: transparent;"
        )
        right.addWidget(self._hint)

        root.addLayout(right, 1)

        self._stat_labels: list[QLabel] = []
        self.clear()

    def _clear_stats(self) -> None:
        while self._stats_host.count():
            item = self._stats_host.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._stat_labels.clear()

    def clear(self) -> None:
        self._title.setText("")
        self._subtitle.setText("")
        self._subtitle.hide()
        self._level.setText("")
        self._level.set_fill_color(OUTLINE_FILL)
        self._level.hide()
        self._hint.setText("")
        self._hint.hide()
        self._icon.set_content(frame_color="#2a3040", pixmap=None, equipped=False)
        self._clear_stats()

    def show_content(self, content: DetailContent | None) -> None:
        self.clear()
        if content is None:
            self._hint.setText("Select an item")
            self._hint.show()
            return

        self._icon.set_content(
            frame_color=content.frame_color,
            pixmap=content.pixmap,
            equipped=content.equipped,
            icon_kind=content.icon_kind,
        )
        if content.level_text:
            self._level.setText(content.level_text)
            self._level.set_fill_color(content.level_color or OUTLINE_FILL)
            self._level.show()
        if content.subtitle:
            self._subtitle.setText(content.subtitle)
            self._subtitle.show()
        self._title.setText(content.title)
        self._title.set_fill_color(content.title_color)
        if content.hint:
            self._hint.setText(content.hint)
            self._hint.show()

        self._clear_stats()
        if content.stat_lines:
            for line in content.stat_lines:
                lbl = QLabel(line.text)
                if line.primary:
                    lbl.setStyleSheet(
                        f"color: {FG}; font-size: 13pt; font-weight: bold; "
                        "background: transparent;"
                    )
                else:
                    lbl.setStyleSheet(
                        f"color: {FG_MUTED}; font-size: 12pt; font-weight: bold; "
                        "background: transparent;"
                    )
                self._stats_host.addWidget(lbl)
                self._stat_labels.append(lbl)
