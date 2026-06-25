import QtQuick
import ui 1.0

Item {
	id: root

	property var petCollectionModel: null
	property var eggHatchTest: null

	property bool detailsOpen: false
	property var selectedPetModel: null

	EggHatchPanel {
		id: hatchPanel

		anchors.bottom: parent.bottom
		anchors.horizontalCenter: parent.horizontalCenter
		width: parent.width
		petCollectionModel: root.petCollectionModel
		eggHatchTest: root.eggHatchTest
	}

	PetSlotGrid {
		id: petGrid

		anchors.top: parent.top
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: hatchPanel.top
		petCollectionModel: root.petCollectionModel
		eggHatchTest: root.eggHatchTest
		onPetClicked: function(petModel) {
			root.selectedPetModel = petModel
			root.detailsOpen = true
		}
	}

	PetDetailsView {
		id: petDetails

		z: 10
		visible: root.detailsOpen && root.selectedPetModel !== null
		anchors.centerIn: parent
		petModel: root.selectedPetModel
		ascensionLevel: petGrid.ascensionLevel
		onClosed: root.detailsOpen = false
	}
}
