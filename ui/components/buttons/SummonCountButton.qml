import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property int summonCount: 1
	property bool selected: false
	property bool buttonEnabled: true
	property color fillColor: Theme.blue
	property real aspectW: 2
	property real aspectH: 1

	readonly property color effectiveFillColor:
		root.selected ? root.fillColor : Theme.lightGrey
	readonly property real fillInset: Math.max(1, height * 0.06)
	readonly property real labelScale: 0.6
	readonly property string formattedSummonCount: {
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		return TmpTextBridge.bulk_summon_count_text(root.summonCount)
	}

	signal clicked()

	readonly property real baseSize: 256

	implicitWidth: baseSize * aspectW
	implicitHeight: baseSize * aspectH

	RectRounded {
		anchors.fill: parent
		anchors.margins: root.fillInset
		aspectW: root.aspectW
		aspectH: root.aspectH
		cornerRatioW: 255 / (512 * (root.aspectW))
		cornerRatioH: 255 / (512 * (root.aspectH))
		fillColor: root.effectiveFillColor
	}

	RectRoundedOutline {
		anchors.fill: parent
		aspectW: root.aspectW
		aspectH: root.aspectH
		cornerRatioW: 255 / (512 * (root.aspectW))
		cornerRatioH: 255 / (512 * (root.aspectH))
		outlineColor: Theme.black
		z: 1
	}

	TMPText {
		anchors.centerIn: parent
		tmpText: root.formattedSummonCount
		pixelSize: root.height * root.labelScale
		fillColor: Theme.white
		outlineColor: Theme.black
		outlineWeight: 8
	}

	MouseArea {
		anchors.fill: parent
		enabled: root.buttonEnabled
		onClicked: root.clicked()
	}
}
