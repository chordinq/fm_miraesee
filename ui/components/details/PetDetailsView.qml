import QtQuick
import ui 1.0

DetailsView {
	id: root

	heightScale: 39

	property var petModel: null
	property var petController: null
	property int ascensionLevel: 0

	property bool comingSoonVisible: false

	readonly property real iconSizeRatio: 0.162
	readonly property real iconSize: panelWidth * iconSizeRatio
	readonly property real iconScale: iconSize / 256
	readonly property real iconLeftMarginRatio: 0.04
	readonly property real iconTopMarginRatio: 0.06
	readonly property real textLeftMarginRatio: 0.13
	readonly property real textTopMarginRatio: 0.03
	readonly property real textRightMarginRatio: 0.05
	readonly property real iconEquippedOpacity: 5 / 16

	readonly property real titleFontScale: 0.043
	readonly property real statFontScale: 0.043
	readonly property real titleSegmentSpacingRatio: 0.012
	readonly property real lineSpacingRatio: 0.012

	readonly property color titleColor: petModel
		? Theme.rarityColors[petModel.rarity]
		: Theme.darkText

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

				PetIcon {
					anchors.fill: parent
					index: root.petModel ? root.petModel.index : -1
					rarity: root.petModel ? root.petModel.rarity : 0
					ascensionLevel: root.ascensionLevel
					opacity: root.petModel && root.petModel.isEquipped
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
					locTable: root.petModel ? root.petModel.rarityLocTable : "General"
					locId: root.petModel ? root.petModel.rarityLocId : ""
					suffix: "]"
					fillColor: root.titleColor
					pixelSize: root.panelWidth * root.titleFontScale
					outlineWeight: 8
				}

				AppText {
					locTable: root.petModel ? root.petModel.nameLocTable : "Pets"
					locId: root.petModel ? root.petModel.nameLocId : ""
					fillColor: root.titleColor
					pixelSize: root.panelWidth * root.titleFontScale
					outlineWeight: 8
				}
			}

			Repeater {
				model: root.petModel ? root.petModel.statLines : []

				Row {
					required property var modelData

					readonly property bool isSecondary: modelData.secondary
					readonly property color lineColor: isSecondary ? Theme.darkGreyText : Theme.black
					spacing: root.panelWidth * 0.012

					AppText {
						text: root.formatStatLine(modelData)
						fillColor: root.statValueColor(modelData)
						pixelSize: root.panelWidth * root.statFontScale
						outlineWeight: 0
					}

					StatLocLabel {
						locSegments: modelData.labelLocSegments
						fillColor: parent.lineColor
						pixelSize: root.panelWidth * root.statFontScale
						outlineWeight: 0
					}
				}
			}
		}

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: actionRow.top
			anchors.bottomMargin: root.panelWidth * root.statusBottomMarginRatio
			visible: root.comingSoonVisible
			locTable: "General"
			locId: root.comingSoonLocId
			suffix: "!"
			fillColor: Theme.red
			pixelSize: root.panelWidth * root.titleFontScale
			outlineWeight: 0
		}

		Row {
			id: actionRow

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
	}

	Timer {
		interval: 2000
		running: root.comingSoonVisible
		onTriggered: root.comingSoonVisible = false
	}

	onClosed: root.comingSoonVisible = false
}
