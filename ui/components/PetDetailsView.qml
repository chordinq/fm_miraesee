import QtQuick
import ui 1.0

PopupView {
	id: root

	property var petModel: null
	property int ascensionLevel: 0

	widthScale: 52
	heightScale: 38

	readonly property real slotSize: width * 0.13
	readonly property real slotScale: slotSize / 256
	readonly property real titleFontScale: 0.043
	readonly property real statFontScale: 0.038
	readonly property color titleColor: petModel
		? Theme.rarityColors[petModel.rarity]
		: Theme.darkText

	PetSlot {
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.leftMargin: parent.width * 0.04
		anchors.topMargin: parent.height * 0.08
		petModel: root.petModel
		ascensionLevel: root.ascensionLevel
		scale: root.slotScale
		transformOrigin: Item.TopLeft
	}

	Column {
		id: infoColumn

		anchors.left: parent.left
		anchors.leftMargin: root.slotSize + root.width * 0.13
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0.06
		anchors.right: parent.right
		anchors.rightMargin: root.width * 0.05
		spacing: root.height * 0.012

		Row {
			spacing: 0

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
			model: root.petModel ? root.petModel.statLines : []

			Row {
				required property var modelData

				readonly property bool isSecondary: modelData.secondary
				readonly property color lineColor: isSecondary ? Theme.darkGreyText : Theme.black
				spacing: root.width * 0.012

				AppText {
					text: modelData.value
					fillColor: parent.lineColor
					pixelSize: root.width * root.statFontScale
					outlineWeight: 0
				}

				AppText {
					locTable: modelData.labelLocTable
					locId: modelData.labelLocId
					fillColor: parent.lineColor
					pixelSize: root.width * root.statFontScale
					outlineWeight: 0
				}
			}
		}
	}
}
