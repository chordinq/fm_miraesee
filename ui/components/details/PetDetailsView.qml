import QtQuick
import ui 1.0
import TMPText 1.0

DetailsView {
	id: root

	panelUnitsH: 39

	property var petModel: null
	property var petController: null
	property int ascensionLevel: 0

	property bool comingSoonVisible: false

	readonly property real iconSizeRatio: 0.16
	readonly property real iconSize: layoutUnit * iconSizeRatio
	readonly property real iconScale: iconSize / 256
	readonly property real iconLeftMarginRatio: 0.04
	readonly property real iconTopMarginRatio: 0.06
	readonly property real iconEquippedOpacity: 0.5
	readonly property real iconOpacity: !root.petModel
		? 1
		: (root.petModel.isEquipped || root.petModel.isLocked)
			? root.iconEquippedOpacity
			: 1
	readonly property real equippedVisualWidthRatio: 1.2
	readonly property real equippedScaleHorizontal: 2.5

	readonly property real titleLeftMarginRatio: 0.27
	readonly property real titleTopMarginRatio: 0.05
	readonly property real titleRightMarginRatio: 0.05
	readonly property real lockButtonSizeRatio: 0.055
	readonly property real lockButtonTopMarginRatio: 0.009
	readonly property real lockButtonRightMarginRatio: 0.0075
	readonly property real titleFontScale: 0.0449
	readonly property color titleColor: petModel
		? Theme.rarityColors[petModel.rarity]
		: Theme.darkText

	readonly property real baseStatsLeftMarginRatio: 0.275
	readonly property real baseStatsTopMarginRatio: 0.115
	readonly property real baseStatsRightMarginRatio: 0.05
	readonly property real baseStatFontScale: 0.042
	readonly property real baseStatRowSpacingRatio: -0.02
	readonly property real baseStatLabelSpacingRatio: 0.012

	readonly property real subStatsLeftMarginRatio: 0.275
	readonly property real subStatsSectionSpacingRatio: 0
	readonly property real subStatsRightMarginRatio: 0.05
	readonly property real subStatFontScale: 0.042
	readonly property real subStatRowSpacingRatio: -0.02
	readonly property real subStatLabelSpacingRatio: 0.012

	property real actionBottomMarginRatio: 0.2
	property real comingSoonBottomMarginRatio: 0.02

	readonly property string upgradeLocId: "25788540620828672"
	readonly property string equipLocId: "27933087392002048"
	readonly property string removeLocId: "27927471772594176"
	readonly property string comingSoonLocId: "29372916365455360"

	readonly property string comingSoonText: TmpTextBridge.localized_text(
		root.comingSoonLocId,
		UiLocale.selectedCode
	) + "."

	function formatStatLine(modelData) {
		if (!modelData)
			return ""
		if (modelData.text !== undefined)
			return modelData.text
		return ""
	}

	function statValueColor(modelData) {
		if (!modelData)
			return Theme.black
		if (!modelData.secondary)
			return Theme.black
		if (modelData.rollT !== undefined)
			return Theme.statRollColor(modelData.rollT)
		return Theme.darkGreyText
	}

	Item {
		anchors.fill: parent

		Item {
			id: iconSlot

			width: root.iconSize
			height: root.iconSize
			anchors.left: parent.left
			anchors.top: parent.top
			anchors.leftMargin: root.layoutUnit * root.iconLeftMarginRatio
			anchors.topMargin: root.layoutUnit * root.iconTopMarginRatio

			Item {
				readonly property int logicalSize: 256

				width: logicalSize
				height: logicalSize
				scale: root.iconScale
				transformOrigin: Item.TopLeft

				PetIcon {
					id: petIcon

					anchors.fill: parent
					index: root.petModel ? root.petModel.index : -1
					rarity: root.petModel ? root.petModel.rarity : 0
					ascensionLevel: root.ascensionLevel
					opacity: root.iconOpacity
				}

				EquippedVisual {
					anchors.centerIn: petIcon
					visible: root.petModel?.isEquipped ?? false
					aspectW: root.equippedScaleHorizontal
					width: petIcon.width * root.equippedVisualWidthRatio
				}

				LockedVisual {
					anchors.centerIn: petIcon
					visible: root.petModel
						&& !root.petModel.isEquipped
						&& root.petModel.isLocked
					aspectW: root.equippedScaleHorizontal
					width: petIcon.width * root.equippedVisualWidthRatio
				}
			}
		}

		LockButton {
			visible: root.petModel !== null
			anchors.top: parent.top
			anchors.right: parent.right
			anchors.topMargin: root.layoutUnit * root.lockButtonTopMarginRatio
			anchors.rightMargin: root.layoutUnit * root.lockButtonRightMarginRatio
			width: root.layoutUnit * root.lockButtonSizeRatio
			height: width
			isLocked: root.petModel?.isLocked ?? false
			enabled: root.petController !== null && root.petModel !== null
			onClicked: {
				if (root.petController && root.petModel)
					root.petController.performPetToggleLock(root.petModel.guid)
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

				tmpText: root.petModel ? root.petModel.titleText : ""
				fillColor: root.titleColor
				pixelSize: root.layoutUnit * root.titleFontScale
				outlineWeight: 8
			}		}

		Item {
			id: baseStatsSlot

			anchors.left: parent.left
			anchors.leftMargin: root.layoutUnit * root.baseStatsLeftMarginRatio
			anchors.top: parent.top
			anchors.topMargin: root.layoutUnit * root.baseStatsTopMarginRatio
			anchors.right: parent.right
			anchors.rightMargin: root.layoutUnit * root.baseStatsRightMarginRatio
			height: baseStatsColumn.height

			Column {
				id: baseStatsColumn

				width: parent.width
				spacing: root.layoutUnit * root.baseStatRowSpacingRatio

				Repeater {
					model: root.petModel ? root.petModel.baseStatLines : []

					Row {
						required property var modelData

						TMPText {
							tmpText: root.formatStatLine(modelData)
							fillColor: root.statValueColor(modelData)
							pixelSize: root.layoutUnit * root.baseStatFontScale
							outlineWeight: 0
						}					}
				}
			}
		}

		Item {
			id: subStatsSlot

			anchors.left: parent.left
			anchors.leftMargin: root.layoutUnit * root.subStatsLeftMarginRatio
			anchors.top: baseStatsSlot.bottom
			anchors.topMargin: root.layoutUnit * root.subStatsSectionSpacingRatio
			anchors.right: parent.right
			anchors.rightMargin: root.layoutUnit * root.subStatsRightMarginRatio
			height: subStatsColumn.height

			Column {
				id: subStatsColumn

				width: parent.width
				spacing: root.layoutUnit * root.subStatRowSpacingRatio

				Repeater {
					model: root.petModel ? root.petModel.subStatLines : []

					Row {
						required property var modelData

						readonly property color lineColor: modelData.rollT !== undefined
							? Theme.statRollColor(modelData.rollT)
							: Theme.darkGreyText

						TMPText {
							tmpText: root.formatStatLine(modelData)
							fillColor: parent.lineColor
							pixelSize: root.layoutUnit * root.subStatFontScale
							outlineWeight: 0
						}					}
				}
			}
		}

		TMPText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: actionRow.top
			anchors.bottomMargin: root.layoutUnit * root.comingSoonBottomMarginRatio
			visible: root.comingSoonVisible
			tmpText: root.comingSoonText
			fillColor: Theme.black
			pixelSize: root.layoutUnit * root.titleFontScale
			outlineWeight: 0
		}
		Row {
			id: actionRow

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			anchors.bottomMargin: root.layoutFrameHeight * root.actionBottomMarginRatio
			spacing: root.actionRowSpacing

			RectRoundButton {
				width: root.actionButtonWidth
				height: root.actionButtonHeight
				aspectW: root.actionButtonAspectW
				aspectH: root.actionButtonAspectH
				labelPixelSize: root.actionButtonFontPixelSize
				locTable: "General"
				locId: root.upgradeLocId
				fillColor: Theme.blue
				buttonEnabled: root.petController !== null && root.petModel !== null
				onClicked: root.comingSoonVisible = true
			}

			RectRoundButton {
				width: root.actionButtonWidth
				height: root.actionButtonHeight
				aspectW: root.actionButtonAspectW
				aspectH: root.actionButtonAspectH
				labelPixelSize: root.actionButtonFontPixelSize
				visible: root.petModel && !root.petModel.isEquipped
				locId: root.equipLocId
				fillColor: root.petModel && root.petModel.canEquip
					? Theme.blue
					: Theme.lightGrey
				buttonEnabled: root.petController !== null
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
				aspectW: root.actionButtonAspectW
				aspectH: root.actionButtonAspectH
				labelPixelSize: root.actionButtonFontPixelSize
				visible: root.petModel && root.petModel.isEquipped
				locId: root.removeLocId
				fillColor: Theme.lightRed
				buttonEnabled: root.petController !== null && root.petModel !== null
				onClicked: {
					if (root.petController && root.petModel)
						root.petController.performPetUnequip(root.petModel.guid)
				}
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
