import QtQuick
import ui 1.0

Item {
	id: root

	signal clicked()

	readonly property int sourceNativeSize: 256
	readonly property real labelScale: 0.45

	implicitWidth: sourceNativeSize
	implicitHeight: sourceNativeSize

	SmallRoundButton {
		id: background
		anchors.fill: parent
		fillColor: Theme.red
	}

	AppText {
		anchors.centerIn: parent
		text: "x"
		fillColor: Theme.white
		outlineColor: Theme.black
		outlineWeight: 8
		pixelSize: parent.height * root.labelScale
	}

	MouseArea {
		anchors.fill: parent
		onClicked: root.clicked()
	}
}
