import QtQuick
import ui 1.0

Item {
	id: root

	property var mountModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int index: mountModel?.index ?? -1
	readonly property int rarity: mountModel?.rarity ?? 0

	implicitWidth: iconSize
	implicitHeight: iconSize

	MountIcon {
		id: icon
		anchors.fill: parent
		index: root.index
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
		opacity: (root.mountModel && root.mountModel.isEquipped) ? 5 / 16 : 1
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.mountModel?.isEquipped ?? false
		scaleHorizontal: 2.5
		fontScale: 21 / 32
		width: iconSize * 1.2
		scale: 0.9
	}

	LevelText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * 0.09
		level: (root.mountModel?.level ?? -1) + 1
		visible: root.index >= 0
		pixelSize: iconSize * 5 / 16
	}
}
