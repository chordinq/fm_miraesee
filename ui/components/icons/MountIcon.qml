import QtQuick
import ui 1.0

Item {
	id: root

	property string spriteSheet: ""
	property int sheetCols: 8
	property int sheetNativeSize: 2048
	property int spriteIndex: 0
	property int rarity: 0
	property real iconSizeRatio: 1.0

	readonly property int logicalSize: 256

	implicitWidth: logicalSize
	implicitHeight: logicalSize

	RectRounded {
		anchors.fill: parent
		scaleW: 4
		scaleH: 4
		fillColor: Theme.rarityColors[root.rarity]
		fillOpacity: 1.0
	}

	SpriteSheet {
		anchors.fill: parent
		source: root.spriteSheet
		spriteIndex: root.spriteIndex
		sheetCols: root.sheetCols
		sheetNativeSize: root.sheetNativeSize
		sizeRatio: root.iconSizeRatio
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: 4
		scaleH: 4
		outlineColor: Theme.black
		outlineOpacity: 1.0
	}
}
