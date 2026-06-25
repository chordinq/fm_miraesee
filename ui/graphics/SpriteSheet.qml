import QtQuick

Item {
	id: root

	property string source: ""
	property int spriteIndex: 0
	property int sheetCols: 8
	property int sheetNativeSize: 2048
	property real sizeRatio: 1.0
	property bool clipCell: true

	readonly property int cellSize: sheetNativeSize / sheetCols
	readonly property int iconCol: spriteIndex % sheetCols
	readonly property int iconRow: spriteIndex / sheetCols

	implicitWidth: 0
	implicitHeight: 0

	Image {
		anchors.centerIn: clipCell ? parent : undefined
		anchors.fill: clipCell ? undefined : parent
		width: clipCell ? parent.width * sizeRatio : undefined
		height: clipCell ? parent.height * sizeRatio : undefined
		source: root.source
		sourceSize: clipCell ? Qt.size(sheetNativeSize, sheetNativeSize) : undefined
		sourceClipRect: clipCell ? Qt.rect(
			iconCol * cellSize,
			iconRow * cellSize,
			cellSize,
			cellSize
		) : undefined
		fillMode: clipCell ? Image.Stretch : Image.PreserveAspectFit
		smooth: true
		mipmap: true
	}
}
