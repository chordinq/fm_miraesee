import QtQuick
import ui 1.0

Item {
	id: root

	implicitWidth: 256
	implicitHeight: 256 / 3

	property real scaleHorizontal: 2
	property real fontScale: 11 / 16

	RectExtraRounded {
		anchors.fill: parent
		scaleW: root.scaleHorizontal
		scaleH: 1
		fillColor: Theme.black
		fillOpacity: 9 / 16.0
		outlineColor: Theme.black
		outlineOpacity: 1.0
	}

	AppText {
		anchors.centerIn: parent
		locId: "27927471772594177"
		locTable: "General"
		useUiFont: true
		fillColor: Theme.white
		pixelSize: root.height * fontScale
		letterSpacing : 0
		outlineColor: Theme.black
		outlineWeight: 7
	}
}
