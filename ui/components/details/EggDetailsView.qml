import QtQuick
import ui 1.0

DetailsView {
	id: root

	heightScale: 46

	property var eggModel: null
	property var eggController: null
	property int ascensionLevel: 0

	property real progressWidthRatio: 0.87
	property real progressStatusSpacingRatio: 0.03
	property real slotsFullBottomMarginRatio: 0.04
	property real bottomStackBottomMarginRatio: 0.02

	readonly property real iconSizeRatio: 0.16
	readonly property real iconSize: layoutUnit * iconSizeRatio
	readonly property real iconScale: iconSize / 256
	readonly property real iconLeftMarginRatio: 0.04
	readonly property real iconTopMarginRatio: 0.06

	readonly property real titleLeftMarginRatio: 0.27
	readonly property real titleTopMarginRatio: 0.05
	readonly property real titleRightMarginRatio: 0.05
	readonly property real titleFontScale: 0.0449

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
	readonly property real hatchDescTopMarginRatio: 0.012

	readonly property real bodyFontScale: 0.042
	readonly property real progressWidth: layoutUnit * progressWidthRatio

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
	readonly property bool hatchButtonEnabled: eggController
		&& (eggController.canStartHatch || eggController.canCompleteHatch)
	readonly property bool showPredictedPetIcon: eggController
		&& eggController.predictedPetIndex >= 0

	readonly property var baseStatLines: {
		if (!eggController)
			return []
		var lines = eggController.statLines
		var out = []
		for (var i = 0; i < lines.length; ++i) {
			if (!lines[i].secondary)
				out.push(lines[i])
		}
		return out
	}

	readonly property var subStatLines: {
		if (!eggController)
			return []
		var lines = eggController.statLines
		var out = []
		for (var i = 0; i < lines.length; ++i) {
			if (lines[i].secondary)
				out.push(lines[i])
		}
		return out
	}

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

				PetIcon {
					anchors.fill: parent
					visible: root.showPredictedPetIcon
					index: eggController ? eggController.predictedPetIndex : -1
					rarity: eggController ? eggController.predictedPetRarity : 0
					ascensionLevel: root.ascensionLevel
				}

				EggIcon {
					anchors.fill: parent
					visible: !root.showPredictedPetIcon
					rarity: root.eggModel ? root.eggModel.rarity : -1
					ascensionLevel: root.ascensionLevel
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

			AppText {
				id: titleText

				prefix: "["
				locTable: root.eggModel ? root.eggModel.rarityLocTable : "General"
				locId: root.eggModel ? root.eggModel.rarityLocId : ""
				suffix: "] "
				appendLocTable: "Stats"
				appendLocId: root.eggTitleLocId
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
					model: root.baseStatLines

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
					model: root.subStatLines

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

		Item {
			id: hatchDescSlot

			anchors.left: parent.left
			anchors.leftMargin: root.layoutUnit * root.subStatsLeftMarginRatio
			anchors.top: subStatsSlot.bottom
			anchors.topMargin: root.layoutUnit * root.hatchDescTopMarginRatio
			anchors.right: parent.right
			anchors.rightMargin: root.layoutUnit * root.subStatsRightMarginRatio
			height: hatchDescText.height

			AppText {
				id: hatchDescText

				width: parent.width
				locTable: "Pets"
				locId: root.hatchDescLocId
				formatArgs: eggController ? eggController.hatchDescFormatArgs : []
				fillColor: Theme.black
				pixelSize: root.layoutUnit * root.subStatFontScale
				outlineWeight: 0
				wordWrap: true
			}
		}

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: bottomStack.visible ? bottomStack.top : actionRow.top
			anchors.bottomMargin: root.layoutUnit * root.slotsFullBottomMarginRatio
			width: root.progressWidth
			horizontalAlignment: Text.AlignHCenter
			visible: root.hatchSlotsFull
			locTable: "Pets"
			locId: root.slotsFullLocId
			fillColor: Theme.red
			pixelSize: root.layoutUnit * root.bodyFontScale
			outlineWeight: 0
			wordWrap: true
		}

		Column {
			id: bottomStack

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: actionRow.top
			anchors.bottomMargin: root.layoutUnit * root.bottomStackBottomMarginRatio
			width: root.progressWidth
			spacing: root.layoutUnit * root.progressStatusSpacingRatio
			visible: root.showHatchingUi

			AppText {
				width: parent.width
				horizontalAlignment: Text.AlignHCenter
				locTable: "Pets"
				locId: root.hatchingLocId
				fillColor: Theme.black
				pixelSize: root.layoutUnit * root.bodyFontScale
				outlineWeight: 0
				wordWrap: true
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
			anchors.bottomMargin: root.layoutUnit * root.actionBottomMarginRatio
			spacing: root.actionRowSpacing

			RectRoundButton {
				width: root.actionButtonWidth
				height: root.actionButtonHeight
				scaleW: root.actionButtonScaleW
				scaleH: root.actionButtonScaleH
				labelPixelSize: root.actionButtonFontPixelSize
				locId: root.hatchButtonLocId
				locTable: "Stats"
				visible: true
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
