import QtQuick
import ui 1.0

Item {
	id: root

	property real contentPadding: 0
	property real panelCornerRadius: -1
	property url currencyIcon: ""
	property int currencyAmount: 0
	property int gemAmount: 0

	readonly property real panelAspectW: 8
	readonly property real panelAspectH: 1
	readonly property real cornerRadiusPx: panelCornerRadius >= 0
		? panelCornerRadius
		: Math.min(width, height) * (255 / (512 * 50))
	readonly property real panelCornerRatioW: width > 0 ? cornerRadiusPx / width : 0
	readonly property real panelCornerRatioH: height > 0 ? cornerRadiusPx / height : 0
	readonly property real currencyInnerHeight: Math.max(0, height - 2 * contentPadding)
	readonly property real currencyIconSizeRatio: 1.5
	readonly property real currencyIconOverflowY: (currencyIconSizeRatio - 1) * 0.5
	readonly property real currencyVisualGapRatio: 0.2
	readonly property real currencyRowHeight: Math.max(
		0,
		currencyInnerHeight / (2 + 2 * currencyIconOverflowY + currencyVisualGapRatio)
	)
	readonly property real currencyColumnSpacing:
		currencyRowHeight * (currencyVisualGapRatio + 2 * currencyIconOverflowY)
	readonly property real currencyIconOverflow: currencyRowHeight * currencyIconSizeRatio * 0.5
	readonly property real currencyLeftInset: contentPadding + currencyIconOverflow

	height: width > 0 ? width * panelAspectH / panelAspectW : 0

	RectRounded {
		anchors.fill: parent
		cornerRatioW: root.panelCornerRatioW
		cornerRatioH: root.panelCornerRatioH
		fillColor: Theme.white
	}

	Column {
		anchors.left: parent.left
		anchors.leftMargin: root.currencyLeftInset
		anchors.verticalCenter: parent.verticalCenter
		spacing: root.currencyColumnSpacing

		CurrencyView {
			visible: root.currencyIcon !== ""
			height: root.currencyRowHeight
			iconSource: root.currencyIcon
			amount: root.currencyAmount
		}

		GemCurrencyView {
			height: root.currencyRowHeight
			amount: root.gemAmount
		}
	}
}
