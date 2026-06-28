import QtQuick
import ui 1.0

Row {
	id: root

	property var locSegments: []
	property real pixelSize: 24
	property color fillColor: Theme.black
	property int outlineWeight: 0

	spacing: 0

	Repeater {
		model: root.locSegments

		AppText {
			required property var modelData
			required property int index

			locId: modelData.locId
			locTable: modelData.locTable
			prefix: index > 0 ? " " : ""
			fillColor: root.fillColor
			pixelSize: root.pixelSize
			outlineWeight: root.outlineWeight
		}
	}
}
