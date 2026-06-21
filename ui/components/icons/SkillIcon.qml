import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property int rarity: 0
	property int index: -1
	property int ascensionLevel: 0

	readonly property var _sprite: SkillIconHelper.lookup(rarity, index, ascensionLevel)
	readonly property bool hasSprite: index >= 0 && _sprite.spriteSheet !== undefined

	readonly property string spriteSheet: _sprite.spriteSheet ?? ""
	readonly property int spriteIndex: _sprite.spriteIndex ?? 0
	readonly property int sheetCols: _sprite.sheetCols ?? 8
	readonly property int sheetNativeSize: _sprite.sheetNativeSize ?? 2048

	readonly property int logicalSize: 256

	implicitWidth: logicalSize
	implicitHeight: logicalSize
	visible: hasSprite

	Item {
		anchors.fill: parent

		Image {
			id: bgShape
			anchors.fill: parent
			source: Qt.resolvedUrl("../../../assets/sprites/UI/SmallRoundButton.png")
			fillMode: Image.Stretch
			smooth: true
			visible: false
			layer.enabled: true
			layer.smooth: true
		}

		MultiEffect {
			anchors.fill: parent
			source: bgShape
			colorization: 1.0
			colorizationColor: Theme.rarityColors[root.rarity]
		}

		SpriteSheet {
			anchors.fill: parent
			source: root.spriteSheet
			spriteIndex: root.spriteIndex
			sheetCols: root.sheetCols
			sheetNativeSize: root.sheetNativeSize
			sizeRatio: 0.95
		}
	}
}
