import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	implicitWidth: 256
	implicitHeight: 256 / 3

	property real aspectW: 2
	property real fontScale: 11 / 16

	readonly property string equippedLabel: {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text("27927471772594177", UiLocale.selectedCode)
	}

	RectExtraRounded {
		anchors.fill: parent
		aspectW: root.aspectW
		aspectH: 1
		cornerRatioW: 255 / (512 * root.aspectW)
		cornerRatioH: 255 / 512
		fillColor: Theme.black
		fillOpacity: 9 / 16.0
		outlineColor: Theme.black
		outlineOpacity: 1.0
	}

	TMPText {
		anchors.centerIn: parent
		tmpText: root.equippedLabel
		fillColor: Theme.white
		pixelSize: root.height * fontScale
		outlineColor: Theme.black
		outlineWeight: 7
	}
}
