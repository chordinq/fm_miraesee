import QtQuick
import ui 1.0

Item {
	id: root

	property var eggModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int rarity: eggModel?.rarity ?? -1

	readonly property real labelOffsetRatio: 0.09
	readonly property real labelPixelSizeRatio: 5 / 16

	signal clicked()

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
		anchors.verticalCenterOffset: icon.height * root.labelOffsetRatio
		locId: "1084108339605504"
		locTable: "Stats"
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
