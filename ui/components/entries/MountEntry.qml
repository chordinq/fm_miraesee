import QtQuick
import ui 1.0

Item {
	id: root

	property var mountModel

	readonly property int iconSize: 256

	implicitWidth: iconSize
	implicitHeight: iconSize

	MountIcon {
		id: icon
		anchors.fill: parent
		visible: root.mountModel !== null
		opacity: (root.mountModel && root.mountModel.isEquipped) ? 5 / 16 : 1
		rarity: root.mountModel?.rarity ?? 0
		spriteIndex: root.mountModel?.spriteIndex ?? 0
		spriteSheet: root.mountModel?.spriteSheet ?? ""
		sheetCols: root.mountModel?.sheetCols ?? 8
		sheetNativeSize: root.mountModel?.sheetNativeSize ?? 2048
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.mountModel?.isEquipped ?? false
		scaleHorizontal: 2.5
		fontScale: 21 / 32
		width: iconSize * 1.2
		scale: 0.9
	}

	AppText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * 0.09
		segments: [
			{ locId: "25799296414314496" },
			{ text: (root.mountModel?.level ?? -1) + 1 }
		]
		segmentSpacing: iconSize * 0.015
		locLetterSpacing: 4
		rawLetterSpacing: 0
		fillColor: Theme.white
		pixelSize: iconSize * 5 / 16
		outlineColor: Theme.black
		outlineWeight: 8
	}
}
