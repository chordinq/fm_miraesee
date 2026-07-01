import QtQuick
import ui 1.0

Item {
	id: root

	property real scaleH: 2
	readonly property real scaleW: height > 0 ? width / height * scaleH : scaleH

	RectRounded {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		fillColor: Theme.white
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
	}
}
