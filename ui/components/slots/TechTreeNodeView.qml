import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property var nodeModel: null
	property color fillColor: Theme.white

	readonly property int iconSize: 256
	readonly property int nodeType: nodeModel?.nodeType ?? -1
	readonly property int iconLevel: nodeModel?.iconLevel ?? -2
	readonly property int levelMax: nodeModel?.levelMax ?? 0
	readonly property bool maxLevel: nodeModel?.maxLevel ?? false

	readonly property string completeLocId: "27937469076533248"
	readonly property bool showTimerStatus: nodeModel
		&& (nodeModel.isUpgrading || nodeModel.isUpgradeComplete)
	readonly property bool showRemainingTime: nodeModel
		&& nodeModel.isUpgrading
		&& !nodeModel.isUpgradeComplete

	readonly property real progressOffsetRatio: 0.17
	readonly property real progressPixelSizeRatio: 17 / 64
	readonly property real timerBarWidthRatio: 1.33
	readonly property real timerBarScaleW: 5.5
	readonly property real timerBarScaleH: 1
	readonly property real timerBarHeightRatio:
		timerBarWidthRatio * timerBarScaleH / timerBarScaleW
	readonly property real timerBarTopMarginRatio: -0.1
	readonly property real timerBarFontScale: 0.2

	property int _timerTick: 0

	readonly property string timerRemainingText: {
		void root._timerTick
		if (!root.showRemainingTime || !root.nodeModel || !root.nodeModel.timerBridge)
			return ""
		return root.nodeModel.timerBridge.remainingText
	}

	readonly property int uiLevel: nodeModel ? nodeModel.level : 0
	readonly property bool showMaxProgress:
		root.levelMax > 0
		&& root.uiLevel === root.levelMax
		&& nodeModel
		&& !nodeModel.isUpgrading
		&& !nodeModel.isUpgradeComplete

	readonly property string progressText: {
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		if (root.levelMax <= 0)
			return ""
		if (root.showMaxProgress)
			return NumberDisplay.maxProgressLabel()
		return NumberDisplay.formatProgressPair(root.uiLevel, root.levelMax)
	}

	readonly property string timerStatusText: {
		UiLocale.selectedCode
		void root._timerTick
		if (root.showRemainingTime)
			return root.timerRemainingText
		return TmpTextBridge.localized_text(root.completeLocId, UiLocale.selectedCode)
	}

	implicitWidth: iconSize
	implicitHeight: iconSize

	TechTreeIcon {
		id: icon
		anchors.fill: parent
		nodeType: root.nodeType
		fillColor: root.fillColor
	}

	TMPText {
		id: progressLabel
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * root.progressOffsetRatio
		tmpText: root.progressText
		visible: root.nodeType >= 0
		pixelSize: iconSize * root.progressPixelSizeRatio
		fillColor: Theme.white
		outlineWeight: 8
	}

	Item {
		id: timerStatusPill

		visible: root.showTimerStatus
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.top: progressLabel.bottom
		anchors.topMargin: iconSize * root.timerBarTopMarginRatio
		width: iconSize * root.timerBarWidthRatio
		height: iconSize * root.timerBarHeightRatio

		RectRounded {
			anchors.fill: parent
			scaleW: root.timerBarScaleW
			scaleH: root.timerBarScaleH
			fillColor: Theme.black
			fillOpacity: 0.5
		}

		RectRoundedOutline {
			anchors.fill: parent
			scaleW: root.timerBarScaleW
			scaleH: root.timerBarScaleH
			outlineColor: Theme.black
		}

		TMPText {
			anchors.centerIn: parent
			tmpText: root.timerStatusText
			pixelSize: iconSize * root.timerBarFontScale
			fillColor: Theme.green
			outlineWeight: 7
		}
	}

	Connections {
		target: root.nodeModel ? root.nodeModel.timerBridge : null
		enabled: root.nodeModel !== null
		function onDisplayChanged() {
			root._timerTick++
		}
	}

	Timer {
		interval: 1000
		running: root.visible && root.showRemainingTime && root.nodeModel
			&& root.nodeModel.timerBridge
		repeat: true
		onTriggered: {
			if (root.nodeModel && root.nodeModel.timerBridge)
				root.nodeModel.timerBridge.refresh()
		}
	}
}
