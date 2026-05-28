# ui/widgets/skill_summon_bar.py — skill tab summon controls (batch, repeat, level)
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from configs import SKILL_SUMMON_CONFIG
from ui.theme.colors import COLLECTION_BG
from ui.theme.metrics import SKILL_SUMMON_BAR_HEIGHT, SKILL_SUMMON_REPEAT_OPTIONS
from ui.theme.builders import (
    muted_label_style,
    summon_batch_button_style,
    summon_combo_style,
    summon_main_button_style,
    summon_progress_style,
)
from ui.services.localization import ui_text
from features.session import Session
from ui.services.skill_summon import (
    available_batch_sizes,
    run_skill_summon_session,
    summon_batch_cost,
    summon_level_progress,
    summon_ticket_balance,
)
from ui.views.skill_summon_results_dialog import SkillSummonResultsDialog


class SkillSummonBar(QWidget):
    """Bottom strip: repeat (top-left), batch size, summon button, summon level progress."""

    summon_finished = Signal()

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self.setObjectName("SkillSummonBar")
        self.setFixedHeight(SKILL_SUMMON_BAR_HEIGHT)
        self.setStyleSheet(f"QWidget#SkillSummonBar {{ background-color: {COLLECTION_BG}; }}")

        self._batch_sizes: list[int] = []
        self._batch_index = 0

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 6, 12, 6)
        root.setSpacing(10)

        left = QVBoxLayout()
        left.setSpacing(4)

        repeat_row = QHBoxLayout()
        repeat_row.setSpacing(6)
        repeat_lbl = QLabel(ui_text("summon_repeat"))
        repeat_lbl.setStyleSheet(muted_label_style())
        self._repeat_combo = QComboBox()
        self._repeat_combo.setStyleSheet(summon_combo_style())
        for n in SKILL_SUMMON_REPEAT_OPTIONS:
            self._repeat_combo.addItem(str(n), n)
        repeat_row.addWidget(repeat_lbl)
        repeat_row.addWidget(self._repeat_combo)
        left.addLayout(repeat_row)

        batch_row = QHBoxLayout()
        batch_row.setSpacing(6)
        batch_lbl = QLabel(ui_text("summon_batch"))
        batch_lbl.setStyleSheet(muted_label_style())
        self._batch_btn = QPushButton("×5")
        self._batch_btn.setStyleSheet(summon_batch_button_style())
        self._batch_btn.clicked.connect(self._cycle_batch)
        batch_row.addWidget(batch_lbl)
        batch_row.addWidget(self._batch_btn)
        left.addLayout(batch_row)

        root.addLayout(left)

        summon_col = QVBoxLayout()
        summon_col.setSpacing(2)
        self._summon_btn = QPushButton()
        self._summon_btn.setStyleSheet(summon_main_button_style())
        self._summon_btn.clicked.connect(self._on_summon)
        summon_col.addWidget(self._summon_btn)
        root.addLayout(summon_col)

        root.addStretch(1)

        right = QVBoxLayout()
        right.setSpacing(4)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._level_lbl = QLabel()
        self._level_lbl.setStyleSheet(muted_label_style())
        self._progress = QProgressBar()
        self._progress.setStyleSheet(summon_progress_style())
        self._progress.setTextVisible(True)
        self._progress.setFixedWidth(100)
        right.addWidget(self._level_lbl, 0, Qt.AlignmentFlag.AlignRight)
        right.addWidget(self._progress, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(right)

        self.refresh()

    def refresh(self) -> None:
        player = self._session.player
        self._batch_sizes = available_batch_sizes(player)
        if self._batch_index >= len(self._batch_sizes):
            self._batch_index = 0
        batch = self._current_batch()
        self._batch_btn.setText(f"×{batch}")
        self._batch_btn.setEnabled(len(self._batch_sizes) > 1)

        cost = summon_batch_cost(player, batch)
        tickets = summon_ticket_balance(player)
        repeat = self._repeat_count()
        total_cost = cost * repeat
        self._summon_btn.setText(f"{ui_text('summon')} ×{batch}\n{total_cost}")
        self._summon_btn.setToolTip(
            f"{SKILL_SUMMON_CONFIG.currency_type.name}: {cost} / pull, "
            f"total {total_cost} ({tickets} owned)"
        )
        self._summon_btn.setEnabled(tickets >= total_cost)

        lv, cur, req = summon_level_progress(player)
        self._level_lbl.setText(lv)
        self._progress.setMaximum(max(req, 1))
        self._progress.setValue(min(cur, req))
        self._progress.setFormat(f"{cur}/{req}")

    def _current_batch(self) -> int:
        if not self._batch_sizes:
            return 5
        return self._batch_sizes[self._batch_index]

    def _repeat_count(self) -> int:
        data = self._repeat_combo.currentData()
        return int(data) if data is not None else 1

    def _cycle_batch(self) -> None:
        if len(self._batch_sizes) <= 1:
            return
        self._batch_index = (self._batch_index + 1) % len(self._batch_sizes)
        self.refresh()

    def _on_summon(self) -> None:
        batch = self._current_batch()
        repeat = self._repeat_count()
        result = run_skill_summon_session(
            self._session.player,
            batch_size=batch,
            repeat_count=repeat,
        )
        dlg = SkillSummonResultsDialog(result, self)
        dlg.exec()
        if result.success and result.pulls:
            self.summon_finished.emit()
        self.refresh()
