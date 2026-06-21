import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "PetArea test (" + testPetCollection.petCount + " pets, "
		+ testPetCollection.eggCount + " eggs, "
		+ testPetCollection.hatchSlotCount + " hatch slots)"
	color: Theme.white

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

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
