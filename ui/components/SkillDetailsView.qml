import QtQuick
import ui 1.0

PopupView {
	id: root

	property var skillModel: null
	property int ascensionLevel: 0

	widthScale: 52
	heightScale: 47

	readonly property int slotSize: width * 0.13
	readonly property real slotScale: slotSize / 256
	readonly property real titleFontScale: 0.055
	readonly property real bodyFontScale: 0.038
	readonly property color titleColor: skillModel
		? Theme.rarityColors[skillModel.rarity]
		: Theme.darkText

	SkillSlot {
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.leftMargin: parent.width * 0.04
		anchors.topMargin: parent.height * 0.06
		skillModel: root.skillModel
		ascensionLevel: root.ascensionLevel
		scale: root.slotScale
		transformOrigin: Item.TopLeft
	}

	Column {
		id: infoColumn

		anchors.left: parent.left
		anchors.leftMargin: root.slotSize + root.width * 0.04
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0.06
		anchors.right: parent.right
		spacing: root.width * 0.025

		Row {
			spacing: root.width * 0.012

			AppText {
				prefix: "["
				locId: root.skillModel ? root.skillModel.rarityLocId : ""
				locTable: root.skillModel ? root.skillModel.rarityLocTable : "General"
				suffix: "]"
				fillColor: root.titleColor
				pixelSize: root.width * root.titleFontScale
				outlineWeight: 8
			}

			AppText {
				locId: root.skillModel ? root.skillModel.nameLocId : ""
				locTable: root.skillModel ? root.skillModel.nameLocTable : "General"
				fillColor: root.titleColor
				pixelSize: root.width * root.titleFontScale
				outlineWeight: 8
			}
		}

		AppText {
			width: infoColumn.width
			wrapMode: Text.WordWrap
			locId: root.skillModel ? root.skillModel.descLocId : ""
			locTable: root.skillModel ? root.skillModel.descLocTable : "Skills"
			formatArgs: root.skillModel ? root.skillModel.descFormatArgs : []
			fillColor: Theme.darkText
			pixelSize: root.width * root.bodyFontScale
			outlineWeight: 0
		}
	}
}
