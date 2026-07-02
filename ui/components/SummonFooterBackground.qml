import QtQuick
import ui 1.0

Item {
	id: root

	property real scaleH: 2
	property real contentPadding: 0
	property url currencyIcon: ""
	property int currencyAmount: 0
	property int gemAmount: 0

	readonly property real scaleW: height > 0 ? width / height * scaleH : scaleH
	readonly property real currencyRowHeight: height / 4
	readonly property real currencyColumnSpacing: currencyRowHeight * 0.08
	readonly property real currencyLeftInset: contentPadding + currencyView.iconOverflow

	RectRounded {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		fillColor: Theme.white
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
	}

	Column {
		anchors.left: parent.left
		anchors.leftMargin: root.currencyLeftInset
		anchors.verticalCenter: parent.verticalCenter
		spacing: root.currencyColumnSpacing

		CurrencyView {
			id: currencyView

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
