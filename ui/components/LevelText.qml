import QtQuick
import QtQuick.Layouts
import ui 1.0

RowLayout {
	id: root

	property int level: 0

	property real pixelSize: 24
	property color fillColor: Theme.white
	property int outlineWeight: 8
	property color outlineColor: Theme.black

	readonly property real lvLetterSpacing: pixelSize * 4 / 80

	spacing: 0

	AppText {
		locId: "25799296414314496"
		pixelSize: root.pixelSize
		letterSpacing: root.lvLetterSpacing
		fillColor: root.fillColor
		outlineColor: root.outlineColor
		outlineWeight: root.outlineWeight
		Layout.alignment: Qt.AlignBaseline
	}

	AppText {
		text: root.level
		pixelSize: root.pixelSize
		fillColor: root.fillColor
		outlineColor: root.outlineColor
		outlineWeight: root.outlineWeight
		Layout.alignment: Qt.AlignBaseline
	}
}
