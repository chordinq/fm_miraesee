pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property var petController: null
	property var petCollectionModel: null
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
		primaryCurrencyIcon: root.petController ? root.petController.summonSpriteImage : ""
		primaryCurrencyAmount: root.petController ? root.petController.eggshellCount : 0
		rarityCounts: root.petCollectionModel ? root.petCollectionModel.eggRarityCounts : []
		rarityIconType: "egg"
		ascensionLevel: root.petController ? root.petController.ascensionLevel : 0
	}

	EggSummonResult {
		anchors.top: topBar.bottom
		anchors.bottom: summonFooter.top
		anchors.left: parent.left
		anchors.leftMargin: root.topMargin
		anchors.topMargin: root.topMargin
		anchors.bottomMargin: root.topMargin
		anchors.right: root.summonResultWidthRatio >= 1 ? parent.right : undefined
		anchors.rightMargin: root.summonResultWidthRatio >= 1 ? root.topMargin : undefined
		width: root.summonResultWidthRatio >= 1
			? undefined
			: parent.width * root.summonResultWidthRatio
		results: root.petController ? root.petController.summonResults : []
		ascensionLevel: root.petController ? root.petController.ascensionLevel : 0
	}

	Row {
		id: bottomColumn

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: summonFooter.verticalCenter
		spacing: root.summonBarSpacing

		BulkSummonToggleView {
			height: root.summonButtonHeight
			summonController: root.petController
		}

		EggSummonButton {
			width: root.summonButtonWidth
			height: root.summonButtonHeight
			summonCount: root.petController ? root.petController.summonCount : 1
			cost: root.petController ? root.petController.summonCost : 0
			spriteImage: root.petController ? root.petController.summonSpriteImage : ""
			fillColor: root.petController && root.petController.canAffordSummon
				? Theme.blue
				: Theme.lightGrey
			enabled: root.petController && root.petController.canAffordSummon
			onClicked: {
				if (root.petController)
					root.petController.performSummon()
			}
		}

		SummonUpgradeStatusView {
			height: root.summonButtonHeight
			summonController: root.petController
		}
	}
}
