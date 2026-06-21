import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "PetArea + SummonButton test"
	color: Theme.white

	readonly property real summonAspect: 4 / 2
	readonly property real summonButtonWidth: Math.min(
		width * 0.55,
		bottomArea.height * 0.8 * summonAspect
	)
	readonly property real summonButtonHeight: summonButtonWidth / summonAspect

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	Item {
		id: petArea
		anchors.top: parent.top
		anchors.left: parent.left
		anchors.right: parent.right
		height: parent.height * 4 / 5

		EggHatchPanel {
			id: hatchPanel
			anchors.bottom: parent.bottom
			anchors.horizontalCenter: parent.horizontalCenter
			width: parent.width
			petCollectionModel: testPetCollection
		}

		PetSlotGrid {
			anchors.top: parent.top
			anchors.left: parent.left
			anchors.right: parent.right
			anchors.bottom: hatchPanel.top
			petCollectionModel: testPetCollection
		}
	}

	Rectangle {
		id: bottomArea
		anchors.bottom: parent.bottom
		anchors.left: parent.left
		anchors.right: parent.right
		height: parent.height / 5
		color: Theme.darkBlue

		SummonButton {
			anchors.centerIn: parent
			width: window.summonButtonWidth
			height: window.summonButtonHeight
			summonCount: testSummonCount
			cost: testSummonCost
			onClicked: console.log("SummonButton clicked")
		}
	}
}
