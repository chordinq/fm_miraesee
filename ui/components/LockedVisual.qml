import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	implicitWidth: 256
	implicitHeight: 256 / 3

	property real scaleHorizontal: 2
	property real fontScale: 11 / 16

	readonly property string lockedLabel: {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text("119351836584960000", UiLocale.selectedCode)
	}

	RectExtraRounded {
		anchors.fill: parent
		scaleW: root.scaleHorizontal
		scaleH: 1
		fillColor: Theme.black
		fillOpacity: 9 / 16.0
		outlineColor: Theme.black
		outlineOpacity: 1.0
	}

	TMPText {
		anchors.centerIn: parent
		tmpText: root.lockedLabel
		fillColor: Theme.white
		pixelSize: root.height * fontScale
		outlineColor: Theme.black
		outlineWeight: 7
	}
}
