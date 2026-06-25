import QtQuick
import ui 1.0

PopupView {
	id: root

	property var skillModel: null
	property int ascensionLevel: 0

	widthScale: 52
	heightScale: 47

	readonly property real slotSize: width * 0.13
	readonly property real slotScale: slotSize / 256
	readonly property real titleFontScale: 0.043
	readonly property real bodyFontScale: 0.043
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
		anchors.leftMargin: root.slotSize + root.width * 0.13
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0.03
		anchors.right: parent.right
		anchors.rightMargin: root.width * 0.05
		spacing: root.height * -0.01

		Row {
			AppText {
				prefix: "["
				locTable: root.skillModel ? root.skillModel.rarityLocTable : "General"
				locId: root.skillModel ? root.skillModel.rarityLocId : ""
				suffix: "]"
				fillColor: root.titleColor
				pixelSize: root.width * root.titleFontScale
				outlineWeight: 8
			}

			AppText {
				locTable: "Skills"
				locId: root.skillModel ? root.skillModel.nameLocId : ""
				fillColor: root.titleColor
				pixelSize: root.width * root.titleFontScale
				outlineWeight: 8
			}
		}

		AppText {
			width: infoColumn.width
			wrapMode: Text.WordWrap
			locTable: "Skills"
			locId: root.skillModel ? root.skillModel.descLocId : ""
			formatArgs: root.skillModel ? root.skillModel.descFormatArgs : []
			fillColor: Theme.black
			pixelSize: root.width * root.bodyFontScale
			outlineWeight: 0
		}
	}
}
