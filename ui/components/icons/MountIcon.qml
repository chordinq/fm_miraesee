import QtQuick
import ui 1.0

Item {
	id: root

	property int rarity: 0
	property int index: -1
	property int ascensionLevel: 0
	property real iconSizeRatio: 1.0

	readonly property var _sprite: MountIconHelper.lookup(rarity, index, ascensionLevel)
	readonly property bool hasSprite: index >= 0 && _sprite.spriteSheet !== undefined

	readonly property string spriteSheet: _sprite.spriteSheet ?? ""
	readonly property int spriteIndex: _sprite.spriteIndex ?? 0
	readonly property int sheetCols: _sprite.sheetCols ?? 8
	readonly property int sheetNativeSize: _sprite.sheetNativeSize ?? 2048

	readonly property int logicalSize: 256

	implicitWidth: logicalSize
	implicitHeight: logicalSize
	visible: hasSprite

	layer.enabled: true
	layer.smooth: true
	layer.mipmap: true

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
