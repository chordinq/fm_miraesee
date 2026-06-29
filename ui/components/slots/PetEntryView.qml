import QtQuick
import ui 1.0

Item {
	id: root

	property var petModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int index: petModel?.index ?? -1
	readonly property int rarity: petModel?.rarity ?? 0

	readonly property real equippedOpacityFraction: 5 / 16
	readonly property real equippedVisualWidthRatio: 1.2
	readonly property real equippedScaleHorizontal: 2.5
	readonly property real levelOffsetRatio:
		root.ascensionLevel > 0 ? 0.29 : -0.1
	readonly property real levelPixelSizeRatio: 0.32
	readonly property real ascensionStarSizeRatio: 0.27
	readonly property real ascensionStarOffsetRatio: -0.06

	implicitWidth: iconSize
	implicitHeight: iconSize

	PetIcon {
		id: icon
		anchors.fill: parent
		index: root.index
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
		opacity: (root.petModel && root.petModel.isEquipped) ? root.equippedOpacityFraction : 1
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.petModel?.isEquipped ?? false
		scaleHorizontal: root.equippedScaleHorizontal
		width: iconSize * root.equippedVisualWidthRatio
	}

	AscensionStarView {
		visible: root.ascensionLevel >= 1
		ascensionLevel: root.ascensionLevel
		starSize: iconSize * root.ascensionStarSizeRatio
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * root.ascensionStarOffsetRatio
	}

	LevelText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: -icon.height * root.levelOffsetRatio
		level: (root.petModel?.level ?? -1) + 1
		visible: root.index >= 0
		pixelSize: iconSize * root.levelPixelSizeRatio
	}

	signal clicked()

	MouseArea {
		anchors.fill: parent
		enabled: root.index >= 0
		onClicked: root.clicked()
	}
}
