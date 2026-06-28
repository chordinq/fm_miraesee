import QtQuick
import ui 1.0

PopupView {
	id: root

	widthScale: 52
	heightScale: 52

	property real slotSizeRatio: 0.13
	property real slotSize: width * slotSizeRatio
	property real slotScale: slotSize / 256
	property real slotLeftMarginRatio: 0.04
	property real slotTopMarginRatio: 0.06
	property real infoLeftExtraRatio: 0.13
	property real infoTopMarginRatio: 0.03
	property real infoRightMarginRatio: 0.05
	property real infoColumnSpacingRatio: -0.01
	property real bodyColumnSpacingRatio: 0.012
	property real titleFontScale: 0.043
	property real titleRowSpacingRatio: 0.012
	property real bodyFontScale: 0.043
	property real statFontScale: 0.043
	property real actionButtonScaleW: 3.5
	property real actionButtonScaleH: 1.75
	property real actionButtonWidthRatio: 0.3
	property real actionButtonWidth: width * actionButtonWidthRatio
	property real actionButtonHeight: actionButtonWidth * (actionButtonScaleH / actionButtonScaleW)
	property real actionButtonFontWidthRatio: 0.17
	property real actionButtonFontPixelSize: actionButtonWidth * actionButtonFontWidthRatio
	property real actionRowSpacing: width * 0.05
	property real actionBottomMarginRatio: 0.08
	property real statusBottomMarginRatio: 0.02
	property real statusColumnSpacingRatio: 0.008

	Item {
		id: _slotHost

		width: root.slotSize
		height: root.slotSize
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.leftMargin: root.width * root.slotLeftMarginRatio
		anchors.topMargin: root.height * root.slotTopMarginRatio
	}

	Column {
		id: _infoColumn

		anchors.left: parent.left
		anchors.leftMargin: root.slotSize + root.width * root.infoLeftExtraRatio
		anchors.top: parent.top
		anchors.topMargin: root.height * root.infoTopMarginRatio
		anchors.right: parent.right
		anchors.rightMargin: root.width * root.infoRightMarginRatio
		spacing: root.height * root.infoColumnSpacingRatio

		Row {
			id: _titleRow

			spacing: 0
			width: parent.width
		}

		Column {
			id: _bodyColumn

			width: parent.width
			spacing: root.height * root.bodyColumnSpacingRatio
		}
	}

	Column {
		id: _statusHost

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: _actionRow.top
		anchors.bottomMargin: root.height * root.statusBottomMarginRatio
		spacing: root.height * root.statusColumnSpacingRatio
	}

	Row {
		id: _actionRow

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: parent.bottom
		anchors.bottomMargin: root.height * root.actionBottomMarginRatio
		spacing: root.actionRowSpacing
	}

	readonly property alias slotHost: _slotHost
	readonly property alias infoColumn: _infoColumn
	readonly property alias titleRow: _titleRow
	readonly property alias bodyColumn: _bodyColumn
	readonly property alias statusHost: _statusHost
	readonly property alias actionRow: _actionRow

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
}
