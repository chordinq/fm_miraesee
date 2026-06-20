import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property int rarity: 0
	property int spriteIndex: 0
	property string spriteSheet: ""
	property int sheetCols: 8
	property int sheetNativeSize: 2048

	readonly property int logicalSize: 256

	implicitWidth: logicalSize
	implicitHeight: logicalSize

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
