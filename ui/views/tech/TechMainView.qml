import QtQuick
import ui 1.0

Item {
	id: root

	property var sessionBridge: null

	readonly property url techPotionIcon: Qt.resolvedUrl("../../../assets/sprites/Currency/techPotions.png")
	readonly property real topMargin: Math.max(8, width * 0.02)
	readonly property real panelCornerRatio: 255 / (512 * 50)
	readonly property real panelCornerRadius: width * panelCornerRatio
	readonly property real summonFooterPadding: Math.max(8, summonFooter.height * 0.12)

	Rectangle {
		anchors.fill: parent
		color: Qt.darker(Theme.darkBlue, 1.5)
	}

	SummonFooterBackground {
		id: summonFooter

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		anchors.leftMargin: root.topMargin
		anchors.rightMargin: root.topMargin
		anchors.bottomMargin: root.topMargin
		contentPadding: root.summonFooterPadding
		panelCornerRadius: root.panelCornerRadius
		currencyIcon: root.techPotionIcon
		currencyAmount: root.sessionBridge ? root.sessionBridge.techPotionCount : 0
		gemAmount: root.sessionBridge ? root.sessionBridge.gemCount : 0
	}
}
