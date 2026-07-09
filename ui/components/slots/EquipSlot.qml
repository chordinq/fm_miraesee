import QtQuick
import ui 1.0

Item {
	id: root

	property real scaleW: 20
	property real scaleH: 4
	property color fillColor: Theme.darkBlue

	readonly property int baseSize: 256

	implicitWidth: baseSize * scaleW
	implicitHeight: baseSize * scaleH

	RectRounded {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		fillColor: root.fillColor
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		outlineColor: Theme.black
	}
}
