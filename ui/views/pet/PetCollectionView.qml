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

	function refreshSelectedEgg() {
		if (root.selectedEggGuid === "" || !root.eggController)
			return
		root.eggController.refreshSelectedEgg()
		if (root.selectedEggModel !== null)
			return
		root.eggDetailsOpen = false
		root.selectedEggGuid = ""
	}

	Connections {
		target: root.petCollectionModel
		function onChanged() {
			root.refreshSelectedPet()
			if (root.selectedEggGuid !== "" && root.eggController)
				root.eggController.refreshSelectedEgg()
		}
		function onPetsChanged() {
			root.refreshSelectedPet()
		}
		function onInventoryEggsChanged() {
			root.refreshSelectedEgg()
		}
		function onHatchSlotsChanged() {
			root.refreshSelectedEgg()
		}
	}

	PetDetailsView {
		id: petDetails

		z: 10
		visible: root.petDetailsOpen && root.selectedPetModel !== null
		anchors.fill: parent
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
		anchors.fill: parent
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
