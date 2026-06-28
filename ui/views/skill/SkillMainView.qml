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
	readonly property int summonOptionCount: skillController
		? skillController.summonCountOptions.length
		: 3
	readonly property real targetSummonHeight: height * 0.12
	readonly property real summonBarSpacing: targetSummonHeight * 0.06
	readonly property real summonCountButtonSize: targetSummonHeight * 0.72
	readonly property real summonButtonWidth: Math.min(
		targetSummonHeight * summonAspect,
		(width - summonCountButtonSize * summonOptionCount - summonBarSpacing * (summonOptionCount + 1)) * 0.95
	)
	readonly property real summonButtonHeight: summonButtonWidth / summonAspect
	readonly property real countLabelScale: 0.34
	readonly property real upgradeAllButtonHeight: targetSummonHeight * 0.55
	readonly property real upgradeAllButtonWidth: upgradeAllButtonHeight * 4.2
	readonly property real topActionRowSpacing: targetSummonHeight * 0.12

	Rectangle {
		anchors.fill: parent
		color: Qt.darker(Theme.darkBlue, 1.5)
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

	UpgradeAllButton {
		id: upgradeAllButton

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: bottomColumn.top
		anchors.bottomMargin: root.topActionRowSpacing
		width: root.upgradeAllButtonWidth
		height: root.upgradeAllButtonHeight
		fillColor: root.skillController && root.skillController.canUpgradeAll
			? Theme.blue
			: Theme.lightGrey
		enabled: root.skillController && root.skillController.canUpgradeAll
		onClicked: {
			if (root.skillController)
				root.skillController.performUpgradeAll()
		}
	}

	SkillSummonResult {
		anchors.top: topBar.bottom
		anchors.bottom: upgradeAllButton.top
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
		anchors.bottom: parent.bottom
		anchors.bottomMargin: root.bottomMargin
		spacing: root.summonBarSpacing

		Repeater {
			model: root.skillController ? root.skillController.summonCountOptions : [5, 75, 250]

			delegate: Item {
				required property int modelData
				required property int index

				readonly property bool selected:
					root.skillController && root.skillController.summonCount === modelData
				readonly property bool canAfford:
					root.skillController && root.skillController.summonAffordFlags[index]

				width: root.summonCountButtonSize
				height: width

				SmallRoundButton {
					anchors.fill: parent
					fillColor: parent.selected && parent.canAfford ? Theme.blue : Theme.lightGrey
				}

				AppText {
					anchors.centerIn: parent
					text: modelData
					pixelSize: parent.width * root.countLabelScale
					fillColor: Theme.white
					outlineColor: Theme.black
					outlineWeight: 8
				}

				MouseArea {
					anchors.fill: parent
					onClicked: {
						if (root.skillController)
							root.skillController.setSummonCount(modelData)
					}
				}
			}
		}

		SummonButton {
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
	}
}
