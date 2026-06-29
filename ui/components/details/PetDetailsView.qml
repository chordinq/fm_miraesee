import QtQuick
import ui 1.0

DetailsView {
	id: root

	property var petModel: null
	property var petController: null
	property int ascensionLevel: 0

	property bool comingSoonVisible: false

	readonly property color titleColor: petModel
		? Theme.rarityColors[petModel.rarity]
		: Theme.darkText

	readonly property string upgradeLocId: "25788540620828672"
	readonly property string equipLocId: "27933087392002048"
	readonly property string removeLocId: "27927471772594176"
	readonly property string comingSoonLocId: "29372916365455360"

	PetEntryView {
		parent: root.slotHost
		anchors.left: root.slotHost.left
		anchors.top: root.slotHost.top
		petModel: root.petModel
		ascensionLevel: root.ascensionLevel
		scale: root.slotScale
		transformOrigin: Item.TopLeft
	}

	Row {
		parent: root.titleRow
		spacing: root.width * root.titleRowSpacingRatio

		AppText {
			prefix: "["
			locTable: root.petModel ? root.petModel.rarityLocTable : "General"
			locId: root.petModel ? root.petModel.rarityLocId : ""
			suffix: "]"
			fillColor: root.titleColor
			pixelSize: root.width * root.titleFontScale
			outlineWeight: 8
		}

		AppText {
			locTable: root.petModel ? root.petModel.nameLocTable : "Pets"
			locId: root.petModel ? root.petModel.nameLocId : ""
			fillColor: root.titleColor
			pixelSize: root.width * root.titleFontScale
			outlineWeight: 8
		}
	}

	Repeater {
		parent: root.bodyColumn
		model: root.petModel ? root.petModel.statLines : []

		Row {
			required property var modelData

			readonly property bool isSecondary: modelData.secondary
			readonly property color lineColor: isSecondary ? Theme.darkGreyText : Theme.black

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

	AppText {
		parent: root.statusHost
		anchors.horizontalCenter: parent.horizontalCenter
		visible: root.comingSoonVisible
		locTable: "General"
		locId: root.comingSoonLocId
		suffix: "!"
		fillColor: Theme.red
		pixelSize: root.width * root.titleFontScale
		outlineWeight: 0
	}

	Row {
		parent: root.actionRow
		spacing: root.actionRowSpacing

		RectRoundButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			labelPixelSize: root.actionButtonFontPixelSize
			locTable: "General"
			locId: root.upgradeLocId
			fillColor: Theme.blue
			enabled: root.petController !== null && root.petModel !== null
			onClicked: root.comingSoonVisible = true
		}

		RectRoundButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			labelPixelSize: root.actionButtonFontPixelSize
			visible: root.petModel && !root.petModel.isEquipped
			locId: root.equipLocId
			fillColor: root.petModel && root.petModel.canEquip
				? Theme.blue
				: Theme.lightGrey
			enabled: root.petController !== null
				&& root.petModel !== null
				&& root.petModel.canEquip
			onClicked: {
				if (root.petController && root.petModel)
					root.petController.performPetEquip(root.petModel.guid)
			}
		}

		RectRoundButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			labelPixelSize: root.actionButtonFontPixelSize
			visible: root.petModel && root.petModel.isEquipped
			locId: root.removeLocId
			fillColor: Theme.lightRed
			enabled: root.petController !== null && root.petModel !== null
			onClicked: {
				if (root.petController && root.petModel)
					root.petController.performPetUnequip(root.petModel.guid)
			}
		}
	}

	Timer {
		interval: 2000
		running: root.comingSoonVisible
		onTriggered: root.comingSoonVisible = false
	}

	onClosed: root.comingSoonVisible = false
}
