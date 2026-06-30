import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property var skillModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int index: skillModel?.index ?? -1
	readonly property int rarity: skillModel?.rarity ?? 0
	readonly property bool showProgress: (skillModel?.maxShardCount ?? 0) > 0
	readonly property bool showMaxed: root.index >= 0 && !root.showProgress

	readonly property real equippedOpacityFraction: 5 / 16
	readonly property real equippedVisualWidthRatio: 1.4
	readonly property real levelOffsetRatio:
		root.ascensionLevel > 0 ? 0.25 : 0.03
	readonly property real levelPixelSizeRatio: 0.32
	readonly property real progressOffsetRatio: 0.34
	readonly property real progressWidthRatio: 1.3
	readonly property real arrowWidthRatio: 0.52
	readonly property real arrowRightMarginRatio: 0.25
	readonly property real arrowTopMarginRatio: 0.18
	readonly property real ascensionStarSizeRatio: 0.25
	readonly property real ascensionStarOffsetRatio: 0

	signal clicked()

	implicitWidth: iconSize
	implicitHeight: iconSize

	SkillIcon {
		id: icon
		anchors.fill: parent
		index: root.index
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
		opacity: (root.skillModel && root.skillModel.isEquipped) ? root.equippedOpacityFraction : 1
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
		level: (root.skillModel?.level ?? -1) + 1
		visible: root.index >= 0
		pixelSize: iconSize * root.levelPixelSizeRatio
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.skillModel?.isEquipped ?? false
		scaleHorizontal: 3
		width: iconSize * root.equippedVisualWidthRatio
	}

	SkillProgress {
		id: skillProgress

		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * root.progressOffsetRatio
		width: iconSize * root.progressWidthRatio
		visible: root.showProgress || root.showMaxed
		showMaxedLabel: root.showMaxed
		shardCount: root.skillModel?.shardCount ?? 0
		maxShardCount: root.skillModel?.maxShardCount ?? 0
	}

	Item {
		visible: skillProgress.upgradable
		width: icon.width * root.arrowWidthRatio
		height: width
		anchors.right: icon.right
		anchors.top: icon.top
		anchors.rightMargin: -width * root.arrowRightMarginRatio
		anchors.topMargin: -height * root.arrowTopMarginRatio

		Image {
			id: upgradeArrowShape

			anchors.fill: parent
			source: Qt.resolvedUrl("../../../assets/sprites/General/UpgradeArrow.png")
			fillMode: Image.PreserveAspectFit
			visible: false
			layer.enabled: true
			layer.smooth: true
			layer.mipmap: true
		}

		MultiEffect {
			anchors.fill: parent
			source: upgradeArrowShape
			colorization: 1.0
			colorizationColor: Theme.green
		}
	}

	MouseArea {
		anchors.fill: parent
		enabled: root.index >= 0
		onClicked: root.clicked()
	}
}
