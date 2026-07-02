import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	readonly property string comingSoonLocId: "29372916365455360"

	readonly property string comingSoonText: {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text(root.comingSoonLocId, UiLocale.selectedCode) + "."
	}

	readonly property real labelPixelSize: Math.max(18, height * 0.04)
	readonly property real labelWidthRatio: 0.85

	Item {
		id: labelHost

		anchors.centerIn: parent
		width: parent.width * root.labelWidthRatio
		height: labelText.implicitHeight

		TMPText {
			id: labelText

			anchors.centerIn: parent
			tmpText: root.comingSoonText
			pixelSize: root.labelPixelSize
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
			scale: Math.min(1, labelHost.width / Math.max(implicitWidth, 1))
			transformOrigin: Item.Center
		}
	}
}
