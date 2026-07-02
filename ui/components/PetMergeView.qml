import QtQuick
import ui 1.0
import TMPText 1.0

PopupView {
	id: root

	property var targetPetModel: null
	property var petController: null

	property var selectedPetGuids: []
	property var selectedEggGuids: []

	readonly property string mergeTitleLocId: "68706935435265"
	readonly property string mergeConfirmLocId: "25783797269852160"
	readonly property string selectedCountLocId: "68706935435264"
	readonly property real slotSize: panelWidth * 0.11
	readonly property real slotScale: slotSize / 256
	readonly property real titleFontScale: 0.04
	readonly property real rowFontScale: 0.032
	readonly property real actionButtonHeight: panelHeight * 0.09
	readonly property real actionButtonWidth: actionButtonHeight * 2.4
	readonly property int selectedCount: root.selectedPetGuids.length + root.selectedEggGuids.length
	readonly property bool canConfirm: root.selectedCount > 0
		&& root.petController !== null
		&& root.targetPetModel !== null

	readonly property string mergeTitleText: {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text_table(
			root.mergeTitleLocId,
			UiLocale.selectedCode,
			"Pets"
		)
	}

	readonly property string selectedCountText: {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text_with_args(
			root.selectedCountLocId,
			UiLocale.selectedCode,
			"Pets",
			[root.selectedCount]
		)
	}

	readonly property string targetLevelText: {
		UiLocale.selectedCode
		if (!root.targetPetModel)
			return ""
		return TmpTextBridge.format_level_text(
			root.targetPetModel.level,
			UiLocale.selectedCode,
			1
		)
	}

	widthScale: 52
	heightScale: 58

	onTargetPetModelChanged: root.resetSelection()
	onVisibleChanged: {
		if (!root.visible)
			root.resetSelection()
	}

	function resetSelection() {
		root.selectedPetGuids = []
		root.selectedEggGuids = []
	}

	function isSelected(kind, guid) {
		if (kind === "pet")
			return root.selectedPetGuids.indexOf(guid) >= 0
		return root.selectedEggGuids.indexOf(guid) >= 0
	}

	function toggleSelection(kind, guid) {
		if (kind === "pet") {
			var petIndex = root.selectedPetGuids.indexOf(guid)
			if (petIndex >= 0) {
				var nextPets = root.selectedPetGuids.slice()
				nextPets.splice(petIndex, 1)
				root.selectedPetGuids = nextPets
			} else {
				root.selectedPetGuids = root.selectedPetGuids.concat([guid])
			}
			return
		}
		var eggIndex = root.selectedEggGuids.indexOf(guid)
		if (eggIndex >= 0) {
			var nextEggs = root.selectedEggGuids.slice()
			nextEggs.splice(eggIndex, 1)
			root.selectedEggGuids = nextEggs
		} else {
			root.selectedEggGuids = root.selectedEggGuids.concat([guid])
		}
	}

	TMPText {
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0.05
		tmpText: root.mergeTitleText
		fillColor: Theme.black
		pixelSize: root.panelWidth * root.titleFontScale
		outlineWeight: 0
	}

	PetEntryView {
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.leftMargin: parent.width * 0.05
		anchors.topMargin: parent.height * 0.12
		petModel: root.targetPetModel
		scale: root.slotScale
		transformOrigin: Item.TopLeft
	}

	Column {
		anchors.left: parent.left
		anchors.leftMargin: root.slotSize + parent.width * 0.14
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0.12
		anchors.right: parent.right
		anchors.rightMargin: parent.width * 0.05
		spacing: parent.height * 0.01

		TMPText {
			tmpText: root.targetPetModel ? root.targetPetModel.titleText : ""
			fillColor: root.targetPetModel
				? Theme.rarityColors[root.targetPetModel.rarity]
				: Theme.darkText
			pixelSize: root.panelWidth * root.titleFontScale
			outlineWeight: 8
		}

		TMPText {
			tmpText: root.targetLevelText
			fillColor: Theme.darkGreyText
			pixelSize: root.panelWidth * root.rowFontScale
			outlineWeight: 0
		}
	}

	Flickable {
		id: candidateList

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0.28
		anchors.bottom: confirmButton.top
		anchors.bottomMargin: parent.height * 0.03
		anchors.leftMargin: parent.width * 0.05
		anchors.rightMargin: parent.width * 0.05
		clip: true
		contentWidth: width
		contentHeight: candidateColumn.height

		Column {
			id: candidateColumn

			width: candidateList.width
			spacing: root.panelHeight * 0.012

			Repeater {
				model: root.petController && root.targetPetModel
					? root.petController.mergeCandidatesFor(root.targetPetModel.guid)
					: []

				delegate: Item {
					required property var modelData

					readonly property bool selected: root.isSelected(modelData.kind, modelData.guid)
					readonly property color rowColor: selected ? Theme.blue : Theme.lightGrey
					width: candidateColumn.width
					height: root.slotSize * 0.72

					RectRounded {
						anchors.fill: parent
						scaleW: 72 / 16
						scaleH: 17 / 16
						fillColor: parent.rowColor
						fillOpacity: selected ? 1.0 : 0.35
					}

					Row {
						anchors.left: parent.left
						anchors.leftMargin: parent.width * 0.02
						anchors.verticalCenter: parent.verticalCenter
						spacing: parent.width * 0.02

						PetIcon {
							visible: modelData.kind === "pet"
							rarity: modelData.rarity
							index: modelData.index
							width: root.slotSize * 0.55
							height: width
						}

						EggIcon {
							visible: modelData.kind === "egg"
							rarity: modelData.rarity
							width: root.slotSize * 0.55
							height: width
						}

						TMPText {
							anchors.verticalCenter: parent.verticalCenter
							tmpText: modelData.label
							fillColor: Theme.black
							pixelSize: root.panelWidth * root.rowFontScale
							outlineWeight: 0
						}
					}

					MouseArea {
						anchors.fill: parent
						onClicked: root.toggleSelection(modelData.kind, modelData.guid)
					}
				}
			}
		}
	}

	TMPText {
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: confirmButton.top
		anchors.bottomMargin: parent.height * 0.015
		tmpText: root.selectedCountText
		fillColor: Theme.darkGreyText
		pixelSize: root.panelWidth * root.rowFontScale
		outlineWeight: 0
	}

	RectRoundButton {
		id: confirmButton

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: parent.bottom
		anchors.bottomMargin: parent.height * 0.08
		width: root.actionButtonWidth
		height: root.actionButtonHeight
		locTable: "General"
		locId: root.mergeConfirmLocId
		fillColor: root.canConfirm ? Theme.blue : Theme.lightGrey
		buttonEnabled: root.canConfirm
		onClicked: {
			if (!root.petController || !root.targetPetModel)
				return
			root.petController.performPetMerge(
				root.targetPetModel.guid,
				root.selectedPetGuids,
				root.selectedEggGuids
			)
			root.closed()
		}
	}

	onClosed: {
		if (root.petController)
			root.petController.clearPetMerge()
		root.resetSelection()
	}
}
