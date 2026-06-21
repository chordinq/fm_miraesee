import QtQuick
import ui 1.0

Item {
	id: root

	property var petModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int index: petModel?.index ?? -1
	readonly property int rarity: petModel?.rarity ?? 0

	implicitWidth: iconSize
	implicitHeight: iconSize

	PetIcon {
		id: icon
		anchors.fill: parent
		index: root.index
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
		opacity: (root.petModel && root.petModel.isEquipped) ? 5 / 16 : 1
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.petModel?.isEquipped ?? false
		scaleHorizontal: 2.5
		width: iconSize * 1.2
	}

	LevelText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * 0.09
		level: (root.petModel?.level ?? -1) + 1
		visible: root.index >= 0
		pixelSize: iconSize * 5 / 16
	}
}
