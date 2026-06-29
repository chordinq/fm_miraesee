import QtQuick
import ui 1.0

DetailsView {
	id: root

	property var skillModel: null
	property var skillController: null
	property int ascensionLevel: 0

	readonly property real iconSizeRatio: 0.13
	readonly property real iconSize: panelWidth * iconSizeRatio
	readonly property real iconScale: iconSize / 256
	readonly property real iconLeftMarginRatio: 0.04
	readonly property real iconTopMarginRatio: 0.06
	readonly property real textLeftMarginRatio: 0.13
	readonly property real textTopMarginRatio: 0.03
	readonly property real textRightMarginRatio: 0.05
	readonly property real iconEquippedOpacity: 5 / 16

	readonly property real titleFontScale: 0.043
	readonly property real bodyFontScale: 0.043
	readonly property real titleSegmentSpacingRatio: 0.012
	readonly property real lineSpacingRatio: 0.012

	readonly property color titleColor: skillModel
		? Theme.rarityColors[skillModel.rarity]
		: Theme.darkText

	readonly property string upgradeLocId: "25788540620828672"
	readonly property string equipLocId: "27933087392002048"
	readonly property string removeLocId: "27927471772594176"

	Item {
		anchors.fill: parent

		Item {
			width: root.iconSize
			height: root.iconSize
			anchors.left: parent.left
			anchors.top: parent.top
			anchors.leftMargin: root.panelWidth * root.iconLeftMarginRatio
			anchors.topMargin: root.panelWidth * root.iconTopMarginRatio

			Item {
				readonly property int logicalSize: 256

				width: logicalSize
				height: logicalSize
				scale: root.iconScale
				transformOrigin: Item.TopLeft

				SkillIcon {
					anchors.fill: parent
					index: root.skillModel ? root.skillModel.index : -1
					rarity: root.skillModel ? root.skillModel.rarity : 0
					ascensionLevel: root.ascensionLevel
					opacity: root.skillModel && root.skillModel.isEquipped
						? root.iconEquippedOpacity
						: 1
				}
			}
		}

		Column {
			anchors.left: parent.left
			anchors.leftMargin: root.iconSize + root.panelWidth * root.textLeftMarginRatio
			anchors.top: parent.top
			anchors.topMargin: root.panelWidth * root.textTopMarginRatio
			anchors.right: parent.right
			anchors.rightMargin: root.panelWidth * root.textRightMarginRatio
			spacing: root.panelWidth * root.lineSpacingRatio

			Row {
				spacing: root.panelWidth * root.titleSegmentSpacingRatio

				AppText {
					prefix: "["
					locTable: root.skillModel ? root.skillModel.rarityLocTable : "General"
					locId: root.skillModel ? root.skillModel.rarityLocId : ""
					suffix: "]"
					fillColor: root.titleColor
					pixelSize: root.panelWidth * root.titleFontScale
					outlineWeight: 8
				}

				AppText {
					locTable: "Skills"
					locId: root.skillModel ? root.skillModel.nameLocId : ""
					fillColor: root.titleColor
					pixelSize: root.panelWidth * root.titleFontScale
					outlineWeight: 8
				}
			}

			AppText {
				width: parent.width
				wrapMode: Text.WordWrap
				locTable: "Skills"
				locId: root.skillModel ? root.skillModel.descLocId : ""
				formatArgs: root.skillModel ? root.skillModel.descFormatArgs : []
				fillColor: Theme.black
				pixelSize: root.panelWidth * root.bodyFontScale
				outlineWeight: 0
			}
		}

		Row {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			anchors.bottomMargin: root.panelWidth * root.actionBottomMarginRatio
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
}
