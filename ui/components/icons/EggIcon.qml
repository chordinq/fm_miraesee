import QtQuick
import ui 1.0

Item {
	id: root

	property string source: ""
	property int spriteIndex: -1
	property int sheetCols: 8
	property int sheetNativeSize: 2048

	readonly property int logicalSize: 256

	implicitWidth: logicalSize
	implicitHeight: logicalSize

	SpriteSheet {
		anchors.fill: parent
		source: root.source
		spriteIndex: root.spriteIndex
		sheetCols: root.sheetCols
		sheetNativeSize: root.sheetNativeSize
		clipCell: root.spriteIndex >= 0
	}
}
