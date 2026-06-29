import QtQuick
import ui 1.0

PopupView {
	id: root

	widthScale: 52
	heightScale: 52
	dimBackdrop: true

	readonly property real actionButtonScaleW: 3.5
	readonly property real actionButtonScaleH: 1.75
	readonly property real actionButtonWidthRatio: 0.37
	readonly property real actionButtonWidth: panelWidth * actionButtonWidthRatio
	readonly property real actionButtonHeight: actionButtonWidth * (actionButtonScaleH / actionButtonScaleW)
	readonly property real actionButtonFontWidthRatio: 0.17
	readonly property real actionButtonFontPixelSize: actionButtonWidth * actionButtonFontWidthRatio
	readonly property real actionRowSpacing: panelWidth * 0.05
	readonly property real actionBottomMarginRatio: 0.08
	readonly property real statusBottomMarginRatio: 0.02
	readonly property real statusSpacingRatio: 0.008
}
