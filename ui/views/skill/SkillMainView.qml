pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property var skillController: null
	property real summonResultWidthRatio: 1.0

	readonly property real summonAspect: 4 / 2
	readonly property real bottomMargin: Math.max(8, height * 0.04)
	readonly property real topMargin: Math.max(8, width * 0.02)
	readonly property real topBarHeight: Math.max(32, height * 0.08)
	readonly property real targetSummonHeight: height * 0.1
	readonly property real summonBarSpacing: targetSummonHeight * 0.2
	readonly property real summonButtonWidth: Math.min(
		targetSummonHeight * summonAspect,
		(width - summonBarSpacing * 3) * 0.5
	)
	readonly property real summonButtonHeight: summonButtonWidth / summonAspect
	readonly property real topActionRowSpacing: targetSummonHeight * 0.12
	readonly property real summonFooterPadding: Math.max(8, height * 0.015)
	readonly property real summonFooterHeight:
		root.summonButtonHeight + root.summonFooterPadding * 2

	Rectangle {
		anchors.fill: parent
		color: Qt.darker(Theme.darkBlue, 1.5)
	}

	SummonFooterBackground {
		id: summonFooter

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		height: root.summonFooterHeight
	}

	MainViewHeader {
		id: topBar

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		anchors.leftMargin: root.topMargin
		anchors.rightMargin: root.topMargin
		anchors.topMargin: root.topMargin
		height: root.topBarHeight
		primaryCurrencyIcon: root.skillController ? root.skillController.summonSpriteImage : ""
		primaryCurrencyAmount: root.skillController ? root.skillController.ticketCount : 0
		secondaryCurrencyIcon: root.skillController ? root.skillController.warPointsSpriteImage : ""
		secondaryCurrencyAmount: root.skillController ? root.skillController.totalWarPoints : 0
		rarityCounts: root.skillController && root.skillController.skillCollection
			? root.skillController.skillCollection.rarityCounts
			: []
		rarityIconType: "skill"
		ascensionLevel: root.skillController ? root.skillController.ascensionLevel : 0
	}

	SkillSummonResult {
		anchors.top: topBar.bottom
		anchors.bottom: summonFooter.top
		anchors.left: parent.left
		anchors.leftMargin: root.topMargin
		anchors.topMargin: root.topMargin
		anchors.bottomMargin: root.topActionRowSpacing
		anchors.right: root.summonResultWidthRatio >= 1 ? parent.right : undefined
		anchors.rightMargin: root.summonResultWidthRatio >= 1 ? root.topMargin : undefined
		width: root.summonResultWidthRatio >= 1
			? undefined
			: parent.width * root.summonResultWidthRatio
		results: root.skillController ? root.skillController.summonResults : []
		ascensionLevel: root.skillController ? root.skillController.ascensionLevel : 0
	}

	Row {
		id: bottomColumn

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: summonFooter.verticalCenter
		spacing: root.summonBarSpacing

		BulkSummonToggleView {
			height: root.summonButtonHeight
			summonController: root.skillController
		}

		SkillSummonButton {
			width: root.summonButtonWidth
			height: root.summonButtonHeight
			summonCount: root.skillController ? root.skillController.summonCount : 5
			cost: root.skillController ? root.skillController.summonCost : 0
			spriteImage: root.skillController ? root.skillController.summonSpriteImage : ""
			fillColor: root.skillController && root.skillController.canAffordSummon
				? Theme.blue
				: Theme.lightGrey
			enabled: root.skillController && root.skillController.canAffordSummon
			onClicked: {
				if (root.skillController)
					root.skillController.performSummon()
			}
		}

		SummonUpgradeStatusView {
			height: root.summonButtonHeight
			summonController: root.skillController
		}
	}
}
