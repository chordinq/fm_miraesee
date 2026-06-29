import QtQuick
import ui 1.0

Item {
	id: root

	property var sessionBridge: null

	readonly property real topMargin: Math.max(8, width * 0.02)
	readonly property real topBarHeight: Math.max(32, height * 0.08)
	readonly property url techPotionIcon: Qt.resolvedUrl("../../../assets/sprites/Currency/techPotions.png")

	Rectangle {
		anchors.fill: parent
		color: Qt.darker(Theme.darkBlue, 1.5)
	}

	MainViewHeader {
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		anchors.leftMargin: root.topMargin
		anchors.rightMargin: root.topMargin
		anchors.topMargin: root.topMargin
		height: root.topBarHeight
		primaryCurrencyIcon: root.techPotionIcon
		primaryCurrencyAmount: root.sessionBridge ? root.sessionBridge.techPotionCount : 0
		rarityCounts: []
	}
}
