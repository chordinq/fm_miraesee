import QtQuick
import ui 1.0

DetailsView {
	id: root

	property var eggModel: null
	property var eggController: null
	property int ascensionLevel: 0

	heightScale: 50

	property real progressWidthRatio: 0.87
	property real progressStatusSpacingRatio: 0.008

	readonly property real iconSizeRatio: 0.13
	readonly property real iconSize: panelWidth * iconSizeRatio
	readonly property real iconScale: iconSize / 256
	readonly property real iconLeftMarginRatio: 0.04
	readonly property real iconTopMarginRatio: 0.06
	readonly property real textLeftMarginRatio: 0.13
	readonly property real textTopMarginRatio: 0.03
	readonly property real textRightMarginRatio: 0.05

	readonly property real titleFontScale: 0.043
	readonly property real bodyFontScale: 0.032
	readonly property real statFontScale: 0.043
	readonly property real titleSegmentSpacingRatio: 0.012
	readonly property real lineSpacingRatio: 0.008

	readonly property real progressWidth: panelWidth * progressWidthRatio

	readonly property color titleColor: eggModel
		? Theme.rarityColors[eggModel.rarity]
		: Theme.darkText

	readonly property string eggTitleLocId: "1084108339605504"
	readonly property string hatchButtonLocId: "1087433751588864"
	readonly property string hatchDescLocId: "153364393984"
	readonly property string slotsFullLocId: "1252196544512"
	readonly property string hatchingLocId: "1252196544513"
	readonly property string completeLocId: "27937469076533248"

	readonly property bool showHatchingUi: eggController
		&& eggModel
		&& eggModel.isEquipped
	readonly property bool hatchSlotsFull: eggController
		&& eggController.hatchSlotsFull
	readonly property bool showGemSkipButton: eggController
		&& eggController.gemSkipVisible
	readonly property bool showHatchButton: eggController
		&& (eggController.canStartHatch
			|| (eggController.canCompleteHatch && !root.showGemSkipButton))
	readonly property bool hatchButtonEnabled: eggController
		&& (eggController.canStartHatch || eggController.canCompleteHatch)
	readonly property bool showPredictedPetIcon: eggController
		&& eggController.predictedPetIndex >= 0

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

	Item {
		anchors.fill: parent

		Item {
			visible: root.showPredictedPetIcon
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
					index: eggController ? eggController.predictedPetIndex : -1
					rarity: eggController ? eggController.predictedPetRarity : 0
					ascensionLevel: root.ascensionLevel
				}
			}
		}

		Column {
			anchors.left: parent.left
			anchors.leftMargin: root.showPredictedPetIcon
				? root.iconSize + root.panelWidth * root.textLeftMarginRatio
				: 0
			anchors.top: parent.top
			anchors.topMargin: root.panelWidth * root.textTopMarginRatio
			anchors.right: parent.right
			anchors.rightMargin: root.panelWidth * root.textRightMarginRatio
			spacing: root.panelWidth * root.lineSpacingRatio

			Row {
				spacing: root.panelWidth * root.titleSegmentSpacingRatio

				AppText {
					prefix: "["
					locTable: root.eggModel ? root.eggModel.rarityLocTable : "General"
					locId: root.eggModel ? root.eggModel.rarityLocId : ""
					suffix: "]"
					fillColor: root.titleColor
					pixelSize: root.panelWidth * root.titleFontScale
					outlineWeight: 8
				}

				AppText {
					locTable: "Stats"
					locId: root.eggTitleLocId
					fillColor: root.titleColor
					pixelSize: root.panelWidth * root.titleFontScale
					outlineWeight: 8
				}
			}

			AppText {
				width: parent.width
				locTable: "Pets"
				locId: root.hatchDescLocId
				formatArgs: eggController ? eggController.hatchDescFormatArgs : []
				fillColor: Theme.darkGreyText
				pixelSize: root.panelWidth * root.bodyFontScale
				outlineWeight: 0
				wrapMode: Text.WordWrap
			}

			Repeater {
				model: eggController ? eggController.statLines : []

				Row {
					required property var modelData

					readonly property bool isSecondary: modelData.secondary
					readonly property color lineColor: isSecondary ? Theme.darkGreyText : Theme.black
					spacing: root.panelWidth * 0.012

					AppText {
						text: root.formatStatLine(modelData)
						fillColor: parent.lineColor
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
			anchors.bottom: statusColumn.visible ? statusColumn.top : actionRow.top
			anchors.bottomMargin: root.panelWidth * root.statusBottomMarginRatio
			width: root.progressWidth
			horizontalAlignment: Text.AlignHCenter
			visible: root.hatchSlotsFull
			locTable: "Pets"
			locId: root.slotsFullLocId
			fillColor: Theme.red
			pixelSize: root.panelWidth * root.bodyFontScale
			outlineWeight: 0
		}

		Column {
			id: statusColumn

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: actionRow.top
			anchors.bottomMargin: root.panelWidth * root.statusBottomMarginRatio
			width: root.progressWidth
			spacing: root.panelWidth * root.progressStatusSpacingRatio
			visible: root.showHatchingUi

			AppText {
				width: parent.width
				horizontalAlignment: Text.AlignHCenter
				locTable: "Pets"
				locId: root.hatchingLocId
				fillColor: Theme.black
				pixelSize: root.panelWidth * root.bodyFontScale
				outlineWeight: 0
			}

			ProgressBar {
				width: root.progressWidth
				timerBridge: eggController ? eggController.selectedEggTimerBridge : null
				completeLocId: root.completeLocId
				completeLocTable: "General"
			}
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
				locId: root.hatchButtonLocId
				locTable: "Stats"
				visible: root.showHatchButton
				fillColor: root.hatchButtonEnabled ? Theme.blue : Theme.lightGrey
				enabled: root.hatchButtonEnabled
					&& root.eggController !== null
					&& root.eggModel !== null
				onClicked: {
					if (!root.eggController || !root.eggModel)
						return
					root.eggController.performHatch(root.eggModel.guid)
					root.closed()
				}
			}

			TechTreeDetailsButton {
				width: root.actionButtonWidth
				height: root.actionButtonHeight
				scaleW: root.actionButtonScaleW
				scaleH: root.actionButtonScaleH
				visible: root.showGemSkipButton
				mode: "skip"
				bottomText: eggController ? eggController.skipGemCostText : ""
				bottomIconSource: Qt.resolvedUrl("../../../assets/sprites/Currency/GemIcon.png")
				fillColor: eggController && eggController.canGemSkipHatch
					? Theme.blue
					: Theme.lightGrey
				enabled: eggController !== null
					&& eggModel !== null
					&& eggController.canGemSkipHatch
				onClicked: {
					if (root.eggController && root.eggModel)
						root.eggController.performGemSkipHatch(root.eggModel.guid)
				}
			}
		}
	}

	onClosed: {
		if (root.eggController)
			root.eggController.refreshSelectedEgg()
	}
}
