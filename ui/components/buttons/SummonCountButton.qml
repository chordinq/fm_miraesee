import QtQuick
import ui 1.0

Item {
	id: root

	property int summonCount: 1
	property bool selected: false
	property bool enabled: true
	property color fillColor: Theme.blue
	property real scaleW: 2
	property real scaleH: 1

	readonly property color effectiveFillColor:
		root.selected ? root.fillColor : Theme.lightGrey
	readonly property real fillInset: Math.max(1, height * 0.06)
	readonly property real labelScale: 0.6
	readonly property string formattedSummonCount: {
		NumberDisplay.revision
		UiSettings.gameNumberFormattingEnabled
		return NumberDisplay.formatInteger(root.summonCount)
	}

	signal clicked()

	readonly property real baseSize: 256

	implicitWidth: baseSize * scaleW
	implicitHeight: baseSize * scaleH

	RectRounded {
		anchors.fill: parent
		anchors.margins: root.fillInset
		scaleW: root.scaleW
		scaleH: root.scaleH
		fillColor: root.effectiveFillColor
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		outlineColor: Theme.black
		z: 1
	}

	AppText {
		anchors.centerIn: parent
		text: "x" + root.formattedSummonCount
		pixelSize: root.height * root.labelScale
		fillColor: Theme.white
		outlineColor: Theme.black
		outlineWeight: 8
	}

	MouseArea {
		anchors.fill: parent
		enabled: root.enabled
		onClicked: root.clicked()
	}
}
