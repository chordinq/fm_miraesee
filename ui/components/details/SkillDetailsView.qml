import QtQuick
import ui 1.0

DetailsView {
	id: root

	property var skillModel: null
	property var skillController: null
	property int ascensionLevel: 0

	readonly property color titleColor: skillModel
		? Theme.rarityColors[skillModel.rarity]
		: Theme.darkText

	readonly property string upgradeLocId: "25788540620828672"
	readonly property string equipLocId: "27933087392002048"
	readonly property string removeLocId: "27927471772594176"

	SkillEntryView {
		parent: root.slotHost
		anchors.left: root.slotHost.left
		anchors.top: root.slotHost.top
		skillModel: root.skillModel
		ascensionLevel: root.ascensionLevel
		scale: root.slotScale
		transformOrigin: Item.TopLeft
	}

	Row {
		parent: root.titleRow
		spacing: root.width * root.titleRowSpacingRatio

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
		parent: root.bodyColumn
		width: root.bodyColumn.width
		wrapMode: Text.WordWrap
		locTable: "Skills"
		locId: root.skillModel ? root.skillModel.descLocId : ""
		formatArgs: root.skillModel ? root.skillModel.descFormatArgs : []
		fillColor: Theme.black
		pixelSize: root.width * root.bodyFontScale
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
			locId: root.upgradeLocId
			fillColor: root.skillModel && root.skillModel.canUpgrade
				? Theme.blue
				: Theme.lightGrey
			enabled: root.skillController !== null
				&& root.skillModel !== null
				&& root.skillModel.canUpgrade
			onClicked: {
				if (root.skillController && root.skillModel)
					root.skillController.performSkillUpgrade(root.skillModel.combatSkillType)
			}
		}

		RectRoundButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			labelPixelSize: root.actionButtonFontPixelSize
			visible: root.skillModel && !root.skillModel.isEquipped
			locId: root.equipLocId
			fillColor: root.skillModel && root.skillModel.canEquip
				? Theme.blue
				: Theme.lightGrey
			enabled: root.skillController !== null
				&& root.skillModel !== null
				&& root.skillModel.canEquip
			onClicked: {
				if (root.skillController && root.skillModel)
					root.skillController.performSkillEquip(root.skillModel.combatSkillType)
			}
		}

		RectRoundButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			labelPixelSize: root.actionButtonFontPixelSize
			visible: root.skillModel && root.skillModel.isEquipped
			locId: root.removeLocId
			fillColor: Theme.lightRed
			enabled: root.skillController !== null && root.skillModel !== null
			onClicked: {
				if (root.skillController && root.skillModel)
					root.skillController.performSkillUnequip(root.skillModel.combatSkillType)
			}
		}
	}
}
