import QtQuick
import ui 1.0

Item {
	id: root

	property var skillModel

	readonly property int iconSize: 256
	readonly property bool showProgress: (skillModel?.maxShardCount ?? 0) > 0

	implicitWidth: iconSize
	implicitHeight: iconSize

	SkillIcon {
		id: icon
		anchors.fill: parent
		visible: root.skillModel !== null
		opacity: (root.skillModel && root.skillModel.isEquipped) ? 5 / 16 : 1
		rarity: root.skillModel?.rarity ?? 0
		spriteIndex: root.skillModel?.spriteIndex ?? 0
		spriteSheet: root.skillModel?.spriteSheet ?? ""
		sheetCols: root.skillModel?.sheetCols ?? 8
		sheetNativeSize: root.skillModel?.sheetNativeSize ?? 2048
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.skillModel?.isEquipped ?? false
		scaleHorizontal: 3
		width: iconSize * 1.4
	}

	AppText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: -icon.height * 0.04
		segments: [
			{ locId: "25799296414314496" },
			{ text: (root.skillModel?.level ?? -1) + 1 }
		]
		locLetterSpacing: 4
		rawLetterSpacing: 0
		fillColor: Theme.white
		pixelSize: iconSize * 5 / 16
		outlineColor: Theme.black
		outlineWeight: 8
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
}
