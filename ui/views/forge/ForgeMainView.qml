import QtQuick
import ui 1.0

Rectangle {
	id: root

	color: Theme.white

	readonly property string comingSoonLocId: "29372916365455360"

	AppText {
		anchors.centerIn: parent
		width: parent.width * 0.9
		locTable: "General"
		locId: root.comingSoonLocId
		suffix: "."
		fillColor: Theme.white
		outlineColor: Theme.black
		outlineWeight: 8
		pixelSize: Math.max(18, parent.height * 0.04)
	}
}
