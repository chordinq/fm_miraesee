import QtQuick
import ui 1.0

Item {
	id: root

	property var sessionBridge: null

	readonly property real summonAspect: SummonButtonMetrics.aspect
	readonly property real targetSummonHeight: height * 0.1
	readonly property real summonBarSpacing: targetSummonHeight * 0.2
	readonly property real summonButtonWidth: Math.min(
		targetSummonHeight * summonAspect,
		(width - summonBarSpacing * 3) * 0.5
	)
	readonly property real summonButtonHeight: summonButtonWidth / summonAspect
	readonly property real summonFooterPadding: Math.max(8, height * 0.015)
	readonly property real summonFooterHeight:
		root.summonButtonHeight + root.summonFooterPadding * 2
	readonly property url techPotionIcon: Qt.resolvedUrl("../../../assets/sprites/Currency/techPotions.png")

	Rectangle {
		anchors.fill: parent
		color: Qt.darker(Theme.darkBlue, 1.5)
	}

	SummonFooterBackground {
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		height: root.summonFooterHeight
		contentPadding: root.summonFooterPadding
		currencyIcon: root.techPotionIcon
		currencyAmount: root.sessionBridge ? root.sessionBridge.techPotionCount : 0
		gemAmount: root.sessionBridge ? root.sessionBridge.gemCount : 0
	}
}
