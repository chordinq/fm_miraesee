import QtQuick
import ui 1.0

Item {
	id: root

	property var skillModel: null
	property int ascensionLevel: 0

	readonly property int iconSize: 256
	readonly property int index: skillModel?.index ?? -1
	readonly property int rarity: skillModel?.rarity ?? 0
	readonly property bool showProgress: (skillModel?.maxShardCount ?? 0) > 0

	signal clicked()

	implicitWidth: iconSize
	implicitHeight: iconSize

	SkillIcon {
		id: icon
		anchors.fill: parent
		index: root.index
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
		opacity: (root.skillModel && root.skillModel.isEquipped) ? 5 / 16 : 1
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.skillModel?.isEquipped ?? false
		scaleHorizontal: 3
		width: iconSize * 1.4
	}

	LevelText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: -icon.height * 0.04
		level: (root.skillModel?.level ?? -1) + 1
		visible: root.index >= 0
		pixelSize: iconSize * 5 / 16
	}

	SkillProgress {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * 1/3
		width: iconSize * 1.3
		visible: showProgress
		shardCount: root.skillModel?.shardCount ?? 0
		maxShardCount: root.skillModel?.maxShardCount ?? 0
	}

	MouseArea {
		anchors.fill: parent
		enabled: root.index >= 0
		onClicked: root.clicked()
	}
}
