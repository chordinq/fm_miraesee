import QtQuick
import ui 1.0

Item {
	id: root

	property var mountModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int index: mountModel?.index ?? -1
	readonly property int rarity: mountModel?.rarity ?? 0

	readonly property real equippedOpacityFraction: 8 / 16
	readonly property real iconOpacity: !root.mountModel
		? 1
		: (root.mountModel.isEquipped || root.mountModel.isLocked)
			? root.equippedOpacityFraction
			: 1
	readonly property real equippedVisualWidthRatio: 1.2
	readonly property real equippedScaleHorizontal: 2.5
	readonly property real equippedFontScale: 21 / 32
	readonly property real equippedScale: 0.9
	readonly property real levelOffsetRatio:
		root.ascensionLevel > 0 ? 0.29 : -0.1
	readonly property real levelPixelSizeRatio: 0.32
	readonly property real ascensionStarSizeRatio: 0.27
	readonly property real ascensionStarOffsetRatio: -0.06

	implicitWidth: iconSize
	implicitHeight: iconSize

	MountIcon {
		id: icon

		anchors.fill: parent
		index: root.index
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
		opacity: root.iconOpacity
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.mountModel?.isEquipped ?? false
		scaleHorizontal: root.equippedScaleHorizontal
		fontScale: root.equippedFontScale
		width: iconSize * root.equippedVisualWidthRatio
		scale: root.equippedScale
	}

	LockedVisual {
		anchors.centerIn: icon
		visible: root.mountModel
			? !root.mountModel.isEquipped && root.mountModel.isLocked
			: false
		scaleHorizontal: root.equippedScaleHorizontal
		fontScale: root.equippedFontScale
		width: iconSize * root.equippedVisualWidthRatio
		scale: root.equippedScale
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
		level: (root.mountModel?.level ?? -1) + 1
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
