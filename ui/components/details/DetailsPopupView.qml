import QtQuick
import ui 1.0

PopupView {
	id: root

	panelUnitsW: 50
	panelUnitsH: 50
	dimBackdrop: true
	bakeLayout: true

	readonly property real layoutUnit: layoutBaseWidth * (panelUnitsW - 2) / panelUnitsW

	readonly property real actionButtonAspectW: 3.5
	readonly property real actionButtonAspectH: 1.75
	readonly property real actionButtonWidthRatio: 0.382
	readonly property real actionButtonWidth: layoutUnit * actionButtonWidthRatio
	readonly property real actionButtonHeight: actionButtonWidth * (actionButtonAspectH / actionButtonAspectW)
	readonly property real actionButtonFontWidthRatio: 0.17
	readonly property real actionButtonFontPixelSize: actionButtonWidth * actionButtonFontWidthRatio
	readonly property real actionRowSpacing: layoutUnit * 0.05
	readonly property real actionBottomMarginRatio: 0.1
}
