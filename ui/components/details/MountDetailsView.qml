import QtQuick
import ui 1.0

DetailsView {
	id: root

	heightScale: 39

	property var mountModel: null
	property var mountController: null
	property int ascensionLevel: 0

	property bool comingSoonVisible: false

	readonly property real iconSizeRatio: 0.16
	readonly property real iconSize: layoutUnit * iconSizeRatio
	readonly property real iconScale: iconSize / 256
	readonly property real iconLeftMarginRatio: 0.04
	readonly property real iconTopMarginRatio: 0.06
	readonly property real iconEquippedOpacity: 0.5
	readonly property real iconOpacity: !root.mountModel
		? 1
		: (root.mountModel.isEquipped || root.mountModel.isLocked)
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
	readonly property color titleColor: mountModel
		? Theme.rarityColors[mountModel.rarity]
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

	function formatStatLine(modelData) {
		if (!modelData)
			return ""
		NumberDisplay.revision
		UiSettings.gameNumberFormattingEnabled
		if (modelData.rawValue !== undefined) {
			if (modelData.secondary && modelData.secondaryStatType >= 0)
				return NumberDisplay.formatSecondaryStat(modelData.secondaryStatType, modelData.rawValue)
			return NumberDisplay.formatStat(modelData.rawValue, false)
		}
		return modelData.value !== undefined ? modelData.value : ""
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

				MountIcon {
					id: mountIcon

					anchors.fill: parent
					index: root.mountModel ? root.mountModel.index : -1
					rarity: root.mountModel ? root.mountModel.rarity : 0
					ascensionLevel: root.ascensionLevel
					opacity: root.iconOpacity
				}

				EquippedVisual {
					anchors.centerIn: mountIcon
					visible: root.mountModel?.isEquipped ?? false
					scaleHorizontal: root.equippedScaleHorizontal
					width: mountIcon.width * root.equippedVisualWidthRatio
				}

				LockedVisual {
					anchors.centerIn: mountIcon
					visible: root.mountModel
						&& !root.mountModel.isEquipped
						&& root.mountModel.isLocked
					scaleHorizontal: root.equippedScaleHorizontal
					width: mountIcon.width * root.equippedVisualWidthRatio
				}
			}
		}

		LockButton {
			visible: root.mountModel !== null
			anchors.top: parent.top
			anchors.right: parent.right
			anchors.topMargin: root.layoutUnit * root.lockButtonTopMarginRatio
			anchors.rightMargin: root.layoutUnit * root.lockButtonRightMarginRatio
			width: root.layoutUnit * root.lockButtonSizeRatio
			height: width
			isLocked: root.mountModel?.isLocked ?? false
			enabled: root.mountController !== null && root.mountModel !== null
			onClicked: {
				if (root.mountController && root.mountModel)
					root.mountController.performMountToggleLock(root.mountModel.guid)
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

			AppText {
				id: titleText

				prefix: "["
				locTable: root.mountModel ? root.mountModel.rarityLocTable : "General"
				locId: root.mountModel ? root.mountModel.rarityLocId : ""
				suffix: "] "
				appendLocTable: root.mountModel ? root.mountModel.nameLocTable : "Mounts"
				appendLocId: root.mountModel ? root.mountModel.nameLocId : ""
				fillColor: root.titleColor
				pixelSize: root.layoutUnit * root.titleFontScale
				outlineWeight: 8
			}
		}

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
					model: root.mountModel ? root.mountModel.baseStatLines : []

					Row {
						required property var modelData

						spacing: root.layoutUnit * root.baseStatLabelSpacingRatio

						AppText {
							text: root.formatStatLine(modelData)
							fillColor: root.statValueColor(modelData)
							pixelSize: root.layoutUnit * root.baseStatFontScale
							outlineWeight: 0
						}

						StatLocLabel {
							locSegments: modelData.labelLocSegments
							fillColor: Theme.black
							pixelSize: root.layoutUnit * root.baseStatFontScale
							outlineWeight: 0
						}
					}
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
					model: root.mountModel ? root.mountModel.subStatLines : []

					Row {
						required property var modelData

						readonly property color lineColor: modelData.rollT !== undefined
							? Theme.statRollColor(modelData.rollT)
							: Theme.darkGreyText
						spacing: root.layoutUnit * root.subStatLabelSpacingRatio

						AppText {
							text: root.formatStatLine(modelData)
							fillColor: parent.lineColor
							pixelSize: root.layoutUnit * root.subStatFontScale
							outlineWeight: 0
						}

						StatLocLabel {
							locSegments: modelData.labelLocSegments
							fillColor: parent.lineColor
							pixelSize: root.layoutUnit * root.subStatFontScale
							outlineWeight: 0
						}
					}
				}
			}
		}

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: actionRow.top
			anchors.bottomMargin: root.layoutUnit * root.comingSoonBottomMarginRatio
			visible: root.comingSoonVisible
			locTable: "General"
			locId: root.comingSoonLocId
			suffix: "."
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
				scaleW: root.actionButtonScaleW
				scaleH: root.actionButtonScaleH
				labelPixelSize: root.actionButtonFontPixelSize
				locTable: "General"
				locId: root.upgradeLocId
				fillColor: Theme.blue
				enabled: root.mountController !== null && root.mountModel !== null
				onClicked: root.comingSoonVisible = true
			}

			RectRoundButton {
				width: root.actionButtonWidth
				height: root.actionButtonHeight
				scaleW: root.actionButtonScaleW
				scaleH: root.actionButtonScaleH
				labelPixelSize: root.actionButtonFontPixelSize
				visible: root.mountModel && !root.mountModel.isEquipped
				locId: root.equipLocId
				fillColor: root.mountModel && root.mountModel.canEquip
					? Theme.blue
					: Theme.lightGrey
				enabled: root.mountController !== null
					&& root.mountModel !== null
					&& root.mountModel.canEquip
				onClicked: {
					if (root.mountController && root.mountModel)
						root.mountController.performMountEquip(root.mountModel.guid)
				}
			}

			RectRoundButton {
				width: root.actionButtonWidth
				height: root.actionButtonHeight
				scaleW: root.actionButtonScaleW
				scaleH: root.actionButtonScaleH
				labelPixelSize: root.actionButtonFontPixelSize
				visible: root.mountModel && root.mountModel.isEquipped
				locId: root.removeLocId
				fillColor: Theme.lightRed
				enabled: root.mountController !== null && root.mountModel !== null
				onClicked: {
					if (root.mountController && root.mountModel)
						root.mountController.performMountUnequip(root.mountModel.guid)
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
