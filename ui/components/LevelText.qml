import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property int level: 0

	property real pixelSize: 24
	property color fillColor: Theme.white
	property int outlineWeight: 8
	property color outlineColor: Theme.black

	readonly property string levelLabel: {
		UiLocale.selectedCode
		return TmpTextBridge.format_level_text(root.level, UiLocale.selectedCode, 1)
	}

	implicitWidth: levelText.implicitWidth
	implicitHeight: levelText.implicitHeight

	TMPText {
		id: levelText

		tmpText: root.levelLabel
		pixelSize: root.pixelSize
		fillColor: root.fillColor
		outlineColor: root.outlineColor
		outlineWeight: root.outlineWeight
	}
}
