import QtQuick
import ui 1.0

Item {
	id: root

	property real maxShardCount: 0
	property real shardCount: 0

	property real scaleW: 72 / 16
	property real scaleH: 17 / 16
	property real fontScale: 12 / 16

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

	RectRounded {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		fillColor: Theme.darkBlue
		fillOpacity: 14 / 16
	}

	Item {
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.bottom: parent.bottom
		width: root.width * root.progressFraction
		clip: true

		RectRounded {
			x: 0
			y: 0
			width: root.width
			height: root.height
			scaleW: root.scaleW
			scaleH: root.scaleH
			fillColor: root.progressFillColor
			fillOpacity: 1.0
		}
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		outlineColor: Theme.black
		outlineOpacity: 1.0
	}

	AppText {
		anchors.centerIn: parent
		text: root.formattedShardProgress
		visible: root.maxShardCount > 0
		fillColor: Theme.white
		pixelSize: root.height * fontScale
		anchors.verticalCenterOffset: (root.height - pixelSize) * 1 / 6
		outlineColor: Theme.black
		outlineWeight: 7
	}
}
