import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property var eggModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int rarity: eggModel?.rarity ?? -1

	readonly property real labelOffsetRatio: 0.09
	readonly property real labelPixelSizeRatio: 5 / 16

	readonly property string eggLabel: {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text_table(
			"1084108339605504",
			UiLocale.selectedCode,
			"Stats"
		)
	}

	signal clicked()

	implicitWidth: iconSize
	implicitHeight: iconSize

	EggIcon {
		id: icon
		anchors.fill: parent
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
	}

	TMPText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * root.labelOffsetRatio
		tmpText: root.eggLabel
		fillColor: Theme.white
		pixelSize: iconSize * root.labelPixelSizeRatio
		outlineColor: Theme.black
		outlineWeight: 8
		visible: root.rarity >= 0
	}

	MouseArea {
		anchors.fill: parent
		onClicked: root.clicked()
	}
}
