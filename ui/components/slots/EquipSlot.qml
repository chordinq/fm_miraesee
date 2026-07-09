import QtQuick
import ui 1.0

Item {
	id: root

	property real aspectW: 20
	property real aspectH: 4
	property color fillColor: Theme.darkBlue

	readonly property int baseSize: 256

	implicitWidth: baseSize * aspectW
	implicitHeight: baseSize * aspectH

	RectRounded {
		anchors.fill: parent
		aspectW: root.aspectW
		aspectH: root.aspectH
		cornerRatioW: 255 / (512 * (root.aspectW))
		cornerRatioH: 255 / (512 * (root.aspectH))
		fillColor: root.fillColor
	}

	RectRoundedOutline {
		anchors.fill: parent
		aspectW: root.aspectW
		aspectH: root.aspectH
		cornerRatioW: 255 / (512 * (root.aspectW))
		cornerRatioH: 255 / (512 * (root.aspectH))
		outlineColor: Theme.black
	}
}
