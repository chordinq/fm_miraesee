import QtQuick
import ui 1.0

Item {
	id: root

	property var eggModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int rarity: eggModel?.rarity ?? -1

	implicitWidth: iconSize
	implicitHeight: iconSize

	EggIcon {
		id: icon
		anchors.fill: parent
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
	}

	AppText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * 0.09
		locId: "1084108339605504"
		locTable: "Stats"
		fillColor: Theme.white
		pixelSize: iconSize * 5 / 16
		outlineColor: Theme.black
		outlineWeight: 8
		visible: root.rarity >= 0
	}
}
