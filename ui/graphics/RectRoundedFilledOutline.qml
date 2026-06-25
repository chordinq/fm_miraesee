import QtQuick
import ui 1.0

Item {
	id: root

	property real widthScale: 40
	property real heightScale: 30

	readonly property real sourceBorder: 256
	readonly property real cornerRatioW: 1 / widthScale
	readonly property real cornerRatioH: 1 / heightScale
	readonly property real bakedW: sourceBorder * widthScale
	readonly property real bakedH: sourceBorder * heightScale

	layer.enabled: true
	layer.smooth: true
	layer.mipmap: true

	Item {
		id: bakeCanvas

		width: root.bakedW
		height: root.bakedH
		transformOrigin: Item.TopLeft
		transform: Scale {
			xScale: root.width / root.bakedW
			yScale: root.height / root.bakedH
			origin.x: 0
			origin.y: 0
		}

		BorderImage {
			anchors.fill: parent
			source: Qt.resolvedUrl("../../assets/sprites/UI/Rect_Rounded_Filled_Outline.png")
			border.left: 255
			border.top: 255
			border.right: 255
			border.bottom: 255
			smooth: true
		}
	}
}
