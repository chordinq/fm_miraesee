import QtQuick
import ui 1.0

Item {
	id: root

	property var petModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int index: petModel?.index ?? -1
	readonly property int rarity: petModel?.rarity ?? 0

	readonly property real equippedOpacityFraction: 8 / 16
	readonly property bool petEquipped: root.petModel?.isEquipped ?? false
	readonly property bool petLocked: root.petModel?.isLocked ?? false
	readonly property real iconOpacity: !root.petModel
		? 1
		: (root.petEquipped || root.petLocked)
			? root.equippedOpacityFraction
			: 1
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
		opacity: root.iconOpacity
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.petEquipped
		scaleHorizontal: root.equippedScaleHorizontal
		width: iconSize * root.equippedVisualWidthRatio
	}

	LockedVisual {
		anchors.centerIn: icon
		visible: root.petModel !== null && !root.petEquipped && root.petLocked
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
