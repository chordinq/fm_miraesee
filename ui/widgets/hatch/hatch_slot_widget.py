# ui/widgets/hatch/hatch_slot_widget.py — single hatch slot visuals (no layout scaling)
from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QWidget

from core.game_logic.player_model.EggModel import EggModel
from ui.services.collection_selection import CollectionSelection
from ui.services.hatch_layout import HatchLayer, build_hatch_layers
from ui.widgets.selectable_widget import SelectableWidget


def _transparent_label(parent: QWidget) -> QLabel:
    label = QLabel(parent)
    label.setStyleSheet("background: transparent;")
    return label


def _pixmap_logical_size(pixmap: QPixmap) -> tuple[int, int]:
    """QLabel geometry is logical px; pixmap may carry HiDPI device pixels."""
    dpr = pixmap.devicePixelRatio()
    if dpr > 1.0:
        return max(1, round(pixmap.width() / dpr)), max(1, round(pixmap.height() / dpr))
    return pixmap.width(), pixmap.height()


def _place_layer(label: QLabel, layer: HatchLayer) -> None:
    pm = layer.pixmap
    lw, lh = _pixmap_logical_size(pm)
    label.setPixmap(pm)
    label.setFixedSize(lw, lh)
    label.move(layer.x, layer.y)
    label.show()


class _HatchSlotScene(QWidget):
    def __init__(
        self,
        egg: EggModel | None,
        *,
        scene_w: int,
        scene_h: int,
        device_pixel_ratio: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(scene_w, scene_h)
        self.setStyleSheet("background: transparent;")
        self._labels: list[QLabel] = []
        self._device_pixel_ratio = device_pixel_ratio
        self.set_egg(
            egg,
            scene_w=scene_w,
            scene_h=scene_h,
            device_pixel_ratio=device_pixel_ratio,
        )

    def set_egg(
        self,
        egg: EggModel | None,
        *,
        scene_w: int,
        scene_h: int,
        device_pixel_ratio: float,
    ) -> None:
        self._device_pixel_ratio = device_pixel_ratio
        for label in self._labels:
            label.deleteLater()
        self._labels.clear()
        self.setFixedSize(scene_w, scene_h)
        layers = build_hatch_layers(
            egg,
            scene_w=scene_w,
            scene_h=scene_h,
            device_pixel_ratio=device_pixel_ratio,
        )
        for layer in layers:
            label = _transparent_label(self)
            _place_layer(label, layer)
            label.raise_()
            self._labels.append(label)
        if layers:
            self._labels[-1].raise_()


class HatchSlotWidget(SelectableWidget):
    """One hatch incubator slot; size is set externally by div spec."""

    def __init__(
        self,
        egg: EggModel | None,
        *,
        scene_w: int,
        scene_h: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._egg = egg
        self._scene_w = scene_w
        self._scene_h = scene_h
        self._selection = (
            CollectionSelection(kind="egg", egg=egg) if egg is not None else None
        )
        if egg is None:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        dpr = self._device_pixel_ratio()
        self._scene = _HatchSlotScene(
            egg,
            scene_w=scene_w,
            scene_h=scene_h,
            device_pixel_ratio=dpr,
            parent=self,
        )
        self.apply_size(scene_w, scene_h)

    def _device_pixel_ratio(self) -> float:
        dpr = self.devicePixelRatioF()
        return dpr if dpr > 0 else 1.0

    def _rebuild_scene(self) -> None:
        self._scene.set_egg(
            self._egg,
            scene_w=self._scene_w,
            scene_h=self._scene_h,
            device_pixel_ratio=self._device_pixel_ratio(),
        )

    def apply_size(self, scene_w: int, scene_h: int) -> None:
        self._scene_w = scene_w
        self._scene_h = scene_h
        self.setFixedSize(scene_w, scene_h)
        self._rebuild_scene()

    def set_egg(self, egg: EggModel | None) -> None:
        self._egg = egg
        self._selection = (
            CollectionSelection(kind="egg", egg=egg) if egg is not None else None
        )
        if egg is None:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._rebuild_scene()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._rebuild_scene()

    def changeEvent(self, event: QEvent) -> None:  # noqa: N802
        super().changeEvent(event)
        if event.type() == QEvent.Type.DevicePixelRatioChange:
            self._rebuild_scene()

    @property
    def egg(self) -> EggModel | None:
        return self._egg

    @property
    def selection(self) -> CollectionSelection | None:
        return self._selection

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if self._egg is None:
            QWidget.mousePressEvent(self, event)
            return
        super().mousePressEvent(event)
