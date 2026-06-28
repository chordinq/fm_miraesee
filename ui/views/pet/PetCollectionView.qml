import QtQuick
import ui 1.0

Item {
	id: root

	property var petCollectionModel: null
	property var petController: null
	property var eggController: null

	property bool petDetailsOpen: false
	property var selectedPetModel: null
	property string selectedPetGuid: ""

	property bool eggDetailsOpen: false
	property var selectedEggModel: null
	property string selectedEggGuid: ""

	EggHatchPanel {
		id: hatchPanel

		anchors.bottom: parent.bottom
		anchors.horizontalCenter: parent.horizontalCenter
		width: parent.width
		petCollectionModel: root.petCollectionModel
		onEggClicked: function(eggModel) {
			root.openEggDetails(eggModel)
		}
	}

	PetSlotGrid {
		id: petGrid

		anchors.top: parent.top
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: hatchPanel.top
		petCollectionModel: root.petCollectionModel
		onPetClicked: function(petModel) {
			root.selectedPetGuid = petModel.guid
			root.selectedPetModel = petModel
			root.petDetailsOpen = true
		}
		onEggClicked: function(eggModel) {
			root.openEggDetails(eggModel)
		}
	}

	function openEggDetails(eggModel) {
		if (!eggModel)
			return
		root.selectedEggGuid = eggModel.guid
		root.selectedEggModel = eggModel
		if (root.eggController)
			root.eggController.selectEgg(eggModel.guid)
		root.eggDetailsOpen = true
	}

	function refreshSelectedPet() {
		if (root.selectedPetGuid === "")
			return
		var pets = root.petCollectionModel.pets
		for (var i = 0; i < pets.length; i++) {
			if (pets[i].guid === root.selectedPetGuid) {
				root.selectedPetModel = pets[i]
				return
			}
		}
		root.petDetailsOpen = false
		root.selectedPetGuid = ""
		root.selectedPetModel = null
	}

	Connections {
		target: root.petCollectionModel
		function onChanged() {
			root.refreshSelectedPet()
			if (root.selectedEggGuid === "")
				return
			var eggs = root.petCollectionModel.eggs
			for (var i = 0; i < eggs.length; i++) {
				if (eggs[i].guid === root.selectedEggGuid) {
					root.selectedEggModel = eggs[i]
					return
				}
			}
			for (i = 0; i < root.petCollectionModel.hatchEggModels.length; i++) {
				var hatchEgg = root.petCollectionModel.hatchEggModels[i]
				if (hatchEgg && hatchEgg.guid === root.selectedEggGuid) {
					root.selectedEggModel = hatchEgg
					return
				}
			}
			root.eggDetailsOpen = false
			root.selectedEggGuid = ""
			root.selectedEggModel = null
		}
	}

	PetDetailsView {
		id: petDetails

		z: 10
		visible: root.petDetailsOpen && root.selectedPetModel !== null
		anchors.centerIn: parent
		petModel: root.selectedPetModel
		petController: root.petController
		ascensionLevel: petGrid.ascensionLevel
		onClosed: {
			root.petDetailsOpen = false
			root.selectedPetGuid = ""
			root.selectedPetModel = null
		}
	}

	EggDetailsView {
		id: eggDetails

		z: 11
		visible: root.eggDetailsOpen && root.selectedEggModel !== null
		anchors.centerIn: parent
		eggModel: root.selectedEggModel
		eggController: root.eggController
		ascensionLevel: petGrid.ascensionLevel
		onClosed: {
			root.eggDetailsOpen = false
			root.selectedEggGuid = ""
			root.selectedEggModel = null
		}
	}
}
