import QtQuick
import ui 1.0

Item {
	id: root

	property var itemModel: null
	property int itemType: -1
	property string emptySheetSource: ""

	readonly property int iconSize: 256
	readonly property bool hasItem: root.itemModel !== null && root.itemModel !== undefined
	readonly property bool showEmpty: !root.hasItem && root.itemType >= 0
	readonly property string resolvedEmptySheetSource: root.emptySheetSource !== ""
		? root.emptySheetSource
		: Qt.resolvedUrl("../../../assets/sprites/Equipment/InventoryTextures.png")
	readonly property int emptySheetCols: 4
	readonly property int emptySheetNativeSize: 1024
	readonly property int emptyBorderIndex: 12

	readonly property real levelOffsetRatio: 0.3
	readonly property real levelPixelSizeRatio: 7 / 32

	implicitWidth: iconSize
	implicitHeight: iconSize

	Item {
		id: emptySlot

		anchors.fill: parent
		visible: root.showEmpty

		layer.enabled: true
		layer.smooth: true
		layer.mipmap: true

		SpriteSheet {
			anchors.fill: parent
			source: root.resolvedEmptySheetSource
			spriteIndex: root.emptyBorderIndex
			sheetCols: root.emptySheetCols
			sheetNativeSize: root.emptySheetNativeSize
		}

		SpriteSheet {
			anchors.fill: parent
			source: root.resolvedEmptySheetSource
			spriteIndex: root.itemType
			sheetCols: root.emptySheetCols
			sheetNativeSize: root.emptySheetNativeSize
		}
	}

	ItemIcon {
		id: icon

		anchors.fill: parent
		visible: root.hasItem
		spriteSheet: root.itemModel?.spriteSheet ?? ""
		spriteIndex: root.itemModel?.spriteIndex ?? 0
		sheetCols: root.itemModel?.sheetCols ?? 1
		sheetNativeSize: root.itemModel?.sheetNativeSize ?? 256
		itemAge: root.itemModel?.itemAge ?? 0
	}

	LevelText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.verticalCenter
		anchors.verticalCenterOffset: icon.height * root.levelOffsetRatio
		visible: root.hasItem
		level: (root.itemModel?.level ?? -1) + 1
		pixelSize: iconSize * root.levelPixelSizeRatio
	}
}
