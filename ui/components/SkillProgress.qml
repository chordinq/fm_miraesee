import QtQuick
import ui 1.0

Item {
	id: root

	property real maxShardCount: 0
	property real shardCount: 0
	property bool showMaxedLabel: false

	property real scaleW: 72 / 16
	property real scaleH: 17 / 16
	property real fontScale: 12 / 16

	readonly property string maxedLocId: "25788256913911808"

	readonly property bool showProgressBar: root.maxShardCount > 0
	readonly property bool showMaxed: root.showMaxedLabel && !root.showProgressBar

	readonly property real progressFraction: maxShardCount > 0
		? Math.min(1, Math.max(0, shardCount / maxShardCount))
		: 0

	readonly property string formattedShardProgress: {
		if (root.maxShardCount <= 0)
			return ""
		NumberDisplay.revision
		UiSettings.gameNumberFormattingEnabled
		return NumberDisplay.formatInteger(root.shardCount) + "/"
			+ NumberDisplay.formatInteger(root.maxShardCount)
	}

	readonly property bool upgradable:
		root.maxShardCount > 0 && root.shardCount >= root.maxShardCount

	readonly property color progressFillColor: root.upgradable ? Theme.green : Theme.white

	implicitWidth: 256
	implicitHeight: implicitWidth * scaleH / scaleW
	height: width * scaleH / scaleW

	ProgressBar {
		anchors.fill: parent
		visible: root.showProgressBar
		scaleW: root.scaleW
		scaleH: root.scaleH
		progressFraction: root.progressFraction
		fillColor: root.progressFillColor
		trackFillOpacity: 14 / 16
		labelText: root.formattedShardProgress
		labelFontScale: root.fontScale
		labelVerticalCenterOffsetRatio: 1 / 6
	}

	AppText {
		anchors.centerIn: parent
		locTable: "General"
		locId: root.maxedLocId
		visible: root.showMaxed
		fillColor: Theme.black
		pixelSize: root.height
		outlineWeight: 0
	}
}
