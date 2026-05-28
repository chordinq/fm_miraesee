# ui/views/skill_summon_results_dialog.py — modal list of skill summon pulls
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.theme.colors import RARITY_COLORS
from ui.theme.builders import muted_button_style, muted_label_style, title_label_style
from ui.services.localization import ui_text
from ui.services.skill_summon import SkillSummonSessionResult, pull_result_line


class SkillSummonResultsDialog(QDialog):
    def __init__(
        self,
        result: SkillSummonSessionResult,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(ui_text("summon_results"))
        self.setModal(True)
        self.setMinimumSize(360, 320)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        if not result.success:
            err = QLabel(result.error or "Error")
            err.setWordWrap(True)
            err.setStyleSheet(muted_label_style())
            root.addWidget(err)
        else:
            header = QLabel(
                f"{ui_text('summon_total')}: {len(result.pulls)} "
                f"(×{result.batch_size} × {result.repeat_count})"
            )
            header.setStyleSheet(title_label_style())
            root.addWidget(header)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            body = QWidget()
            body.setStyleSheet("background: transparent;")
            body_layout = QVBoxLayout(body)
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.setSpacing(4)

            for pull in result.pulls:
                row = QLabel(pull_result_line(pull))
                color = RARITY_COLORS.get(int(pull.rarity), "#e0e0e0")
                row.setStyleSheet(
                    f"color: {color}; font-weight: bold; background: transparent; padding: 2px 0;"
                )
                row.setWordWrap(True)
                body_layout.addWidget(row)

            body_layout.addStretch(1)
            scroll.setWidget(body)
            scroll.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )
            root.addWidget(scroll, 1)

        close_btn = QPushButton(ui_text("close"))
        close_btn.setStyleSheet(muted_button_style())
        close_btn.clicked.connect(self.accept)
        root.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)
