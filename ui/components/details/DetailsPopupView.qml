import QtQuick
import ui 1.0

PopupView {
	id: root

	widthScale: 50
	heightScale: 50
	dimBackdrop: true
	bakeLayout: true

	readonly property real layoutUnit: layoutBaseWidth * (widthScale - 2) / widthScale

	readonly property real actionButtonScaleW: 3.5
	readonly property real actionButtonScaleH: 1.75
	readonly property real actionButtonWidthRatio: 0.382
	readonly property real actionButtonWidth: layoutUnit * actionButtonWidthRatio
	readonly property real actionButtonHeight: actionButtonWidth * (actionButtonScaleH / actionButtonScaleW)
	readonly property real actionButtonFontWidthRatio: 0.17
	readonly property real actionButtonFontPixelSize: actionButtonWidth * actionButtonFontWidthRatio
	readonly property real actionRowSpacing: layoutUnit * 0.05
	readonly property real actionBottomMarginRatio: 0.1
}
