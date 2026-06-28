import QtQuick
import ui 1.0

DetailsView {
	id: root

	property var eggModel: null
	property var eggController: null
	property int ascensionLevel: 0

	heightScale: 50

	property real bodyFontScale: 0.032
	property real progressWidthRatio: 0.87
	property real progressStatusSpacingRatio: 0.008

	readonly property real progressWidth: width * progressWidthRatio

	readonly property color titleColor: eggModel
		? Theme.rarityColors[eggModel.rarity]
		: Theme.darkText

	readonly property string eggTitleLocId: "1084108339605504"
	readonly property string hatchButtonLocId: "1087433751588864"
	readonly property string hatchDescLocId: "153364393984"
	readonly property string slotsFullLocId: "1252196544512"
	readonly property string hatchingLocId: "1252196544513"
	readonly property string completeLocId: "27937469076533248"

	readonly property bool showHatchingUi: eggController
		&& eggModel
		&& eggModel.isEquipped
	readonly property bool hatchSlotsFull: eggController
		&& eggController.hatchSlotsFull
	readonly property bool hatchButtonEnabled: eggController
		&& eggController.hatchButtonEnabled

	PetIcon {
		parent: root.slotHost
		anchors.left: root.slotHost.left
		anchors.top: root.slotHost.top
		visible: eggController && eggController.predictedPetIndex >= 0
		rarity: eggController ? eggController.predictedPetRarity : 0
		index: eggController ? eggController.predictedPetIndex : -1
		ascensionLevel: root.ascensionLevel
		scale: root.slotScale
		transformOrigin: Item.TopLeft
	}

	Row {
		parent: root.titleRow
		spacing: root.width * root.titleRowSpacingRatio

		AppText {
			prefix: "["
			locTable: root.eggModel ? root.eggModel.rarityLocTable : "General"
			locId: root.eggModel ? root.eggModel.rarityLocId : ""
			suffix: "]"
			fillColor: root.titleColor
			pixelSize: root.width * root.titleFontScale
			outlineWeight: 8
		}

		AppText {
			locTable: "Stats"
			locId: root.eggTitleLocId
			fillColor: root.titleColor
			pixelSize: root.width * root.titleFontScale
			outlineWeight: 8
		}
	}

	AppText {
		parent: root.bodyColumn
		width: root.bodyColumn.width
		locTable: "Pets"
		locId: root.hatchDescLocId
		formatArgs: eggController ? eggController.hatchDescFormatArgs : []
		fillColor: Theme.darkGreyText
		pixelSize: root.width * root.bodyFontScale
		outlineWeight: 0
		wrapMode: Text.WordWrap
	}

	Column {
		parent: root.bodyColumn
		width: root.bodyColumn.width
		spacing: root.height * 0.008

		Repeater {
			model: eggController ? eggController.statLines : []

			Row {
				required property var modelData

				readonly property bool isSecondary: modelData.secondary
				readonly property color lineColor: isSecondary ? Theme.darkGreyText : Theme.black
				spacing: root.width * 0.012

				AppText {
					text: root.formatStatLine(modelData)
					fillColor: parent.lineColor
					pixelSize: root.width * root.statFontScale
					outlineWeight: 0
				}

				StatLocLabel {
					locSegments: modelData.labelLocSegments
					fillColor: parent.lineColor
					pixelSize: root.width * root.statFontScale
					outlineWeight: 0
				}
			}
		}
	}

	AppText {
		parent: root.statusHost
		width: root.progressWidth
		horizontalAlignment: Text.AlignHCenter
		visible: root.hatchSlotsFull
		locTable: "Pets"
		locId: root.slotsFullLocId
		fillColor: Theme.red
		pixelSize: root.width * root.bodyFontScale
		outlineWeight: 0
	}

	Column {
		parent: root.statusHost
		width: root.progressWidth
		spacing: root.height * root.progressStatusSpacingRatio
		visible: root.showHatchingUi

		AppText {
			width: parent.width
			horizontalAlignment: Text.AlignHCenter
			locTable: "Pets"
			locId: root.hatchingLocId
			fillColor: Theme.black
			pixelSize: root.width * root.bodyFontScale
			outlineWeight: 0
		}

		ProgressBar {
			width: root.progressWidth
			timerBridge: eggController ? eggController.selectedEggTimerBridge : null
			completeLocId: root.completeLocId
			completeLocTable: "General"
		}
	}

	RectRoundButton {
		parent: root.actionRow
		width: root.actionButtonWidth
		height: root.actionButtonHeight
		scaleW: root.actionButtonScaleW
		scaleH: root.actionButtonScaleH
		labelPixelSize: root.actionButtonFontPixelSize
		locId: root.hatchButtonLocId
		locTable: "Stats"
		fillColor: root.hatchButtonEnabled ? Theme.blue : Theme.lightGrey
		enabled: root.hatchButtonEnabled
			&& root.eggController !== null
			&& root.eggModel !== null
		onClicked: {
			if (root.eggController && root.eggModel)
				root.eggController.performHatch(root.eggModel.guid)
		}
	}

	onClosed: {
		if (root.eggController)
			root.eggController.refreshSelectedEgg()
	}
}
