import QtQuick
import ui 1.0

Item {
	id: root

	property real cornerRatio: 255 / (256 * 40)
	property real cornerRatioW: cornerRatio
	property real cornerRatioH: cornerRatio

	readonly property real sourceBorder: 255
	readonly property real bakeBase: 256

	readonly property real bakedW: bakeBase / cornerRatioW
	readonly property real bakedH: bakeBase / cornerRatioH
	readonly property real bakeUnitsW: sourceBorder / (512 * cornerRatioW)
	readonly property real bakeUnitsH: sourceBorder / (512 * cornerRatioH)

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
			border.left: root.sourceBorder
			border.top: root.sourceBorder
			border.right: root.sourceBorder
			border.bottom: root.sourceBorder
			smooth: true
		}
	}
}
