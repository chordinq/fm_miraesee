import QtQuick
import ui 1.0

Item {
	id: root

	property real scaleW: 22.5
	property real scaleH: 2
	property real labelFontScale: 0.55
	property var timerBridge: null
	property real progressFraction: 0
	property color fillColor: Theme.blue
	property string labelText: ""
	property string labelLocId: ""
	property string labelLocTable: ""
	property string completeLocId: "27937469076533248"
	property string completeLocTable: "General"

	readonly property bool usesTimerBridge: root.timerBridge !== null
	readonly property bool timerComplete: usesTimerBridge && root.timerBridge.isComplete
	readonly property real displayProgress: usesTimerBridge
		? root.timerBridge.progressFraction
		: root.progressFraction
	readonly property string displayLabelText: usesTimerBridge
		? (timerComplete ? "" : root.timerBridge.remainingText)
		: root.labelText
	readonly property string displayLabelLocId: timerComplete
		? root.completeLocId
		: root.labelLocId
	readonly property string displayLabelLocTable: timerComplete
		? root.completeLocTable
		: root.labelLocTable

	height: width * scaleH / scaleW

	RectRounded {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		fillColor: Theme.darkBlue
	}

	Item {
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.bottom: parent.bottom
		width: parent.width * Math.max(0, Math.min(1, root.displayProgress))
		clip: true

		RectRounded {
			x: 0
			y: 0
			width: root.width
			height: root.height
			scaleW: root.scaleW
			scaleH: root.scaleH
			fillColor: root.fillColor
		}
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		outlineColor: Theme.black
	}

	AppText {
		anchors.centerIn: parent
		text: root.displayLabelText
		locId: root.displayLabelLocId
		locTable: root.displayLabelLocTable
		fillColor: Theme.white
		pixelSize: parent.height * root.labelFontScale
		outlineColor: Theme.black
		outlineWeight: 7
	}

	Timer {
		interval: 1000
		running: root.visible
			&& root.usesTimerBridge
			&& root.timerBridge.isActive
			&& !root.timerBridge.isComplete
		repeat: true
		onTriggered: root.timerBridge.refresh()
	}
}
