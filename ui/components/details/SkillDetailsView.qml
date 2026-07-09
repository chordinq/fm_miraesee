import QtQuick
import ui 1.0
import TMPText 1.0

DetailsView {
	id: root

	panelUnitsH: 45.5

	property var skillModel: null
	property var skillController: null
	property int ascensionLevel: 0

	readonly property int iconLogicalSize: 256
	readonly property real iconSizeRatio: 0.138
	readonly property real iconSize: layoutUnit * iconSizeRatio
	readonly property real iconScale: iconSize / iconLogicalSize
	readonly property real iconLeftMarginRatio: 0.04
	readonly property real iconTopMarginRatio: 0.054
	readonly property real iconEquippedOpacity: 5 / 16
	readonly property real equippedVisualWidthRatio: 1.4
	readonly property real levelOffsetRatio:
		root.ascensionLevel > 0 ? 0.25 : 0.03
	readonly property real levelPixelSizeRatio: 0.32
	readonly property real progressOffsetRatio: 0.34
	readonly property real progressWidthRatio: 1.3
	readonly property real ascensionStarSizeRatio: 0.25
	readonly property real ascensionStarOffsetRatio: 0
	readonly property real iconProgressHeightRatio:
		progressWidthRatio * (17 / 16) / (72 / 16)
	readonly property real iconLogicalHeightRatio:
		1 + progressOffsetRatio + iconProgressHeightRatio * 0.5
	readonly property bool showProgress:
		(root.skillModel?.maxShardCount ?? 0) > 0
	readonly property bool showMaxed:
		(root.skillModel?.index ?? -1) >= 0 && !root.showProgress

	readonly property real titleLeftMarginRatio: 0.27
	readonly property real titleTopMarginRatio: 0.026
	readonly property real titleRightMarginRatio: 0.046
	readonly property real titleFontScale: 0.0449
	readonly property color titleColor: skillModel
		? Theme.rarityColors[skillModel.rarity]
		: Theme.darkText
	
	readonly property real descLeftMarginRatio: 0.27
	readonly property real descTopMarginRatio: 0.1
	readonly property real descRightMarginRatio: 0.046
	readonly property real bodyFontScale: 0.045

	readonly property string upgradeLocId: "25788540620828672"
	readonly property string equipLocId: "27933087392002048"
	readonly property string removeLocId: "27927471772594176"
	readonly property string passiveLocId: "3898839411974144"

	readonly property real passiveWidthRatio: 0.805
	readonly property real passiveWidth: layoutUnit * passiveWidthRatio
	readonly property real passiveLabelLeftMarginRatio: 0.13
	readonly property real passiveLabelBottomMarginRatio: 0.1
	readonly property real passivePillBottomMarginRatio: 0.057
	readonly property real passiveFontScale: 0.045
	readonly property real passivePillAspectW: 21
	readonly property real passivePillAspectH: 1.2
	readonly property real passivePillHeight:
		passiveWidth * passivePillAspectH / passivePillAspectW
	readonly property string passiveLabelText: TmpTextBridge.localized_text_table(
		root.passiveLocId,
		UiLocale.selectedCode,
		"Skills"
	)

	readonly property bool showPassiveUi:
		(root.skillModel?.passiveStatText?.length ?? 0) > 0

	Item {
		anchors.fill: parent

		Item {
			id: iconSlot

			width: root.iconSize
			height: root.iconSize * root.iconLogicalHeightRatio
			anchors.left: parent.left
			anchors.top: parent.top
			anchors.leftMargin: root.layoutUnit * root.iconLeftMarginRatio
			anchors.topMargin: root.layoutUnit * root.iconTopMarginRatio

			Item {
				width: root.iconLogicalSize
				height: root.iconLogicalSize * root.iconLogicalHeightRatio
				scale: root.iconScale
				transformOrigin: Item.TopLeft

				SkillIcon {
					id: skillIcon

					width: root.iconLogicalSize
					height: root.iconLogicalSize
					index: root.skillModel ? root.skillModel.index : -1
					rarity: root.skillModel ? root.skillModel.rarity : 0
					ascensionLevel: root.ascensionLevel
					opacity: root.skillModel && root.skillModel.isEquipped
						? root.iconEquippedOpacity
						: 1
				}

				AscensionStarView {
					visible: root.ascensionLevel >= 1
					ascensionLevel: root.ascensionLevel
					starSize: root.iconLogicalSize * root.ascensionStarSizeRatio
					anchors.horizontalCenter: skillIcon.horizontalCenter
					anchors.verticalCenter: skillIcon.bottom
					anchors.verticalCenterOffset:
						skillIcon.height * root.ascensionStarOffsetRatio
				}

				LevelText {
					anchors.horizontalCenter: skillIcon.horizontalCenter
					anchors.verticalCenter: skillIcon.bottom
					anchors.verticalCenterOffset:
						-skillIcon.height * root.levelOffsetRatio
					level: (root.skillModel?.level ?? -1) + 1
					visible: skillIcon.index >= 0
					pixelSize: root.iconLogicalSize * root.levelPixelSizeRatio
				}

				EquippedVisual {
					anchors.centerIn: skillIcon
					visible: root.skillModel?.isEquipped ?? false
					aspectW: 3
					width: root.iconLogicalSize * root.equippedVisualWidthRatio
				}

				SkillProgress {
					anchors.horizontalCenter: skillIcon.horizontalCenter
					anchors.verticalCenter: skillIcon.bottom
					anchors.verticalCenterOffset:
						skillIcon.height * root.progressOffsetRatio
					width: root.iconLogicalSize * root.progressWidthRatio
					visible: root.showProgress || root.showMaxed
					showMaxedLabel: root.showMaxed
					shardCount: root.skillModel?.shardCount ?? 0
					maxShardCount: root.skillModel?.maxShardCount ?? 0
				}
			}
		}

		Item {
			id: titleSlot

			anchors.left: parent.left
			anchors.leftMargin: root.layoutUnit * root.titleLeftMarginRatio
			anchors.top: parent.top
			anchors.topMargin: root.layoutUnit * root.titleTopMarginRatio
			anchors.right: parent.right
			anchors.rightMargin: root.layoutUnit * root.titleRightMarginRatio
			height: titleText.height

			TMPText {
				id: titleText

				tmpText: root.skillModel ? root.skillModel.titleText : ""
				fillColor: root.titleColor
				pixelSize: root.layoutUnit * root.titleFontScale
				outlineWeight: 8
			}
		}

		Item {
			id: descSlot

			anchors.left: parent.left
			anchors.leftMargin: root.layoutUnit * root.descLeftMarginRatio
			anchors.top: parent.top
			anchors.topMargin: root.layoutUnit * root.descTopMarginRatio
			anchors.right: parent.right
			anchors.rightMargin: root.layoutUnit * root.descRightMarginRatio
			height: descText.height

			TMPText {
				id: descText

				width: parent.width
				wordWrap: true
				tmpText: root.skillModel ? root.skillModel.descText : ""
				fillColor: Theme.black
				pixelSize: root.layoutUnit * root.bodyFontScale
				outlineWeight: 0
			}
		}

		Item {
			id: passiveLabelSlot

			visible: root.showPassiveUi
			anchors.left: parent.left
			anchors.leftMargin: root.layoutUnit * root.passiveLabelLeftMarginRatio
			anchors.bottom: actionRow.top
			anchors.bottomMargin: root.layoutUnit * root.passiveLabelBottomMarginRatio
			height: passiveLabel.height

			TMPText {
				id: passiveLabel

				tmpText: root.passiveLabelText
				fillColor: Theme.darkGreyText
				pixelSize: root.layoutUnit * root.passiveFontScale
				outlineWeight: 0
			}
		}

		Item {
			id: passivePillSlot

			visible: root.showPassiveUi
			width: root.passiveWidth
			height: root.passivePillHeight
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: actionRow.top
			anchors.bottomMargin: root.layoutUnit * root.passivePillBottomMarginRatio

			RectRounded {
				anchors.fill: parent
				aspectW: root.passivePillAspectW
				aspectH: root.passivePillAspectH
				cornerRatioW: 255 / (512 * root.passivePillAspectW)
				cornerRatioH: 255 / (512 * root.passivePillAspectH)
				fillColor: Theme.black
				fillOpacity: 0.3
			}

			TMPText {
				anchors.centerIn: parent
				tmpText: root.skillModel ? root.skillModel.passiveStatText : ""
				fillColor: Theme.black
				pixelSize: root.layoutUnit * root.passiveFontScale
				outlineWeight: 0
			}
		}

		Row {
			id: actionRow
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			anchors.bottomMargin: root.layoutUnit * root.actionBottomMarginRatio
			spacing: root.actionRowSpacing

			RectRoundButton {
				width: root.actionButtonWidth
				height: root.actionButtonHeight
				aspectW: root.actionButtonAspectW
				aspectH: root.actionButtonAspectH
				labelPixelSize: root.actionButtonFontPixelSize
				locId: root.upgradeLocId
				fillColor: root.skillModel && root.skillModel.canUpgrade
					? Theme.blue
					: Theme.lightGrey
				buttonEnabled: root.skillController !== null
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
				aspectW: root.actionButtonAspectW
				aspectH: root.actionButtonAspectH
				labelPixelSize: root.actionButtonFontPixelSize
				visible: root.skillModel && !root.skillModel.isEquipped
				locId: root.equipLocId
				fillColor: root.skillModel && root.skillModel.canEquip
					? Theme.blue
					: Theme.lightGrey
				buttonEnabled: root.skillController !== null
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
				aspectW: root.actionButtonAspectW
				aspectH: root.actionButtonAspectH
				labelPixelSize: root.actionButtonFontPixelSize
				visible: root.skillModel && root.skillModel.isEquipped
				locId: root.removeLocId
				fillColor: Theme.lightRed
				buttonEnabled: root.skillController !== null && root.skillModel !== null
				onClicked: {
					if (root.skillController && root.skillModel)
						root.skillController.performSkillUnequip(root.skillModel.combatSkillType)
				}
			}
		}
	}
}
