import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property int nodeType: -1
	property color fillColor: Theme.white

	readonly property var _sprite: TechTreeIconHelper.lookup(nodeType)
	readonly property bool hasSprite: nodeType >= 0 && _sprite.spriteSheet !== undefined

	readonly property string spriteSheet: _sprite.spriteSheet ?? ""
	readonly property int spriteIndex: _sprite.spriteIndex ?? 0
	readonly property int sheetCols: _sprite.sheetCols ?? 8
	readonly property int sheetNativeSize: _sprite.sheetNativeSize ?? 1024

	readonly property int logicalSize: 256

	implicitWidth: logicalSize
	implicitHeight: logicalSize
	visible: hasSprite

	layer.enabled: true
	layer.smooth: true
	layer.mipmap: true

	Item {
		anchors.fill: parent

		Image {
			id: bgShape
			anchors.fill: parent
			source: Qt.resolvedUrl("../../../assets/sprites/UI/TechTreeNode.png")
			fillMode: Image.Stretch
			smooth: true
			visible: false
			layer.enabled: true
			layer.smooth: true
			layer.mipmap: true
		}

		MultiEffect {
			anchors.fill: parent
			source: bgShape
			colorization: 1.0
			colorizationColor: root.fillColor
		}

		SpriteSheet {
			anchors.fill: parent
			source: root.spriteSheet
			spriteIndex: root.spriteIndex
			sheetCols: root.sheetCols
			sheetNativeSize: root.sheetNativeSize
			sizeRatio: 0.72
		}
	}
}
