import QtQuick
import ui 1.0

Item {
	id: root

	property int rarity: -1
	property int ascensionLevel: 0

	readonly property var _sprite: EggIconHelper.lookup(rarity, ascensionLevel)
	readonly property bool hasSprite: rarity >= 0 && _sprite.spriteSheet !== undefined

	readonly property string spriteSheet: _sprite.spriteSheet ?? ""
	readonly property int spriteIndex: _sprite.spriteIndex ?? -1
	readonly property int sheetCols: _sprite.sheetCols ?? 8
	readonly property int sheetNativeSize: _sprite.sheetNativeSize ?? 2048

	readonly property int logicalSize: 256

	implicitWidth: logicalSize
	implicitHeight: logicalSize
	visible: hasSprite

	SpriteSheet {
		anchors.fill: parent
		source: root.spriteSheet
		spriteIndex: root.spriteIndex
		sheetCols: root.sheetCols
		sheetNativeSize: root.sheetNativeSize
		clipCell: root.spriteIndex >= 0
	}
}
