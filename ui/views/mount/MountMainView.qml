pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property var mountController: null
	property var mountCollectionModel: null
	property real summonResultWidthRatio: 1.0

	readonly property real summonAspect: 4 / 2
	readonly property real bottomMargin: Math.max(8, height * 0.04)
	readonly property real topMargin: Math.max(8, width * 0.02)
	readonly property real topBarHeight: Math.max(32, height * 0.08)
	readonly property int summonOptionCount: mountController
		? mountController.summonCountOptions.length
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
		primaryCurrencyIcon: root.mountController ? root.mountController.summonSpriteImage : ""
		primaryCurrencyAmount: root.mountController ? root.mountController.clockWinderCount : 0
		rarityCounts: root.mountCollectionModel ? root.mountCollectionModel.rarityCounts : []
		rarityIconType: "mount"
		ascensionLevel: root.mountController ? root.mountController.ascensionLevel : 0
	}

	MountSummonResult {
		anchors.top: topBar.bottom
		anchors.bottom: bottomColumn.top
		anchors.left: parent.left
		anchors.leftMargin: root.topMargin
		anchors.topMargin: root.topMargin
		anchors.bottomMargin: root.topMargin
		anchors.right: root.summonResultWidthRatio >= 1 ? parent.right : undefined
		anchors.rightMargin: root.summonResultWidthRatio >= 1 ? root.topMargin : undefined
		width: root.summonResultWidthRatio >= 1
			? undefined
			: parent.width * root.summonResultWidthRatio
		results: root.mountController ? root.mountController.summonResults : []
		ascensionLevel: root.mountController ? root.mountController.ascensionLevel : 0
	}

	Row {
		id: bottomColumn

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: parent.bottom
		anchors.bottomMargin: root.bottomMargin
		spacing: root.summonBarSpacing

		Repeater {
			model: root.mountController ? root.mountController.summonCountOptions : [1, 15, 50]

			delegate: Item {
				required property int modelData
				required property int index

				readonly property bool selected:
					root.mountController && root.mountController.summonCount === modelData
				readonly property bool canAfford:
					root.mountController && root.mountController.summonAffordFlags[index]

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
						if (root.mountController)
							root.mountController.setSummonCount(modelData)
					}
				}
			}
		}

		SummonButton {
			width: root.summonButtonWidth
			height: root.summonButtonHeight
			summonCount: root.mountController ? root.mountController.summonCount : 1
			cost: root.mountController ? root.mountController.summonCost : 0
			spriteImage: root.mountController ? root.mountController.summonSpriteImage : ""
			fillColor: root.mountController && root.mountController.canAffordSummon
				? Theme.blue
				: Theme.lightGrey
			enabled: root.mountController && root.mountController.canAffordSummon
			onClicked: {
				if (root.mountController)
					root.mountController.performSummon()
			}
		}
	}
}
