import QtQuick
import ui 1.0
import TMPText 1.0

Row {
	id: root

	property var locSegments: []
	property real pixelSize: 24
	property color fillColor: Theme.black
	property int outlineWeight: 0

	readonly property string labelText: {
		UiLocale.selectedCode
		return TmpTextBridge.join_loc_segments(root.locSegments, UiLocale.selectedCode)
	}

	spacing: 0

	TMPText {
		tmpText: root.labelText
		fillColor: root.fillColor
		pixelSize: root.pixelSize
		outlineWeight: root.outlineWeight
	}
}
