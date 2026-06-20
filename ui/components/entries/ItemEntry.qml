import QtQuick
import ui 1.0

Item {
	id: root

	property var itemModel

	readonly property int iconSize: 256

	implicitWidth: iconSize
	implicitHeight: iconSize

	ItemIcon {
		id: icon
		anchors.fill: parent
		visible: root.itemModel !== null
		spriteSheet: root.itemModel?.spriteSheet ?? ""
		spriteIndex: root.itemModel?.spriteIndex ?? 0
		sheetCols: root.itemModel?.sheetCols ?? 1
		sheetNativeSize: root.itemModel?.sheetNativeSize ?? 256
		itemAge: root.itemModel?.itemAge ?? 0
	}

	LevelText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.verticalCenter
		anchors.verticalCenterOffset: icon.height * 0.3
		level: (root.itemModel?.level ?? -1) + 1
		pixelSize: iconSize * 7 / 32
	}
}
