import QtQuick
import ui 1.0

Item {
	id: root

	property real aspectW: 8
	property real aspectH: 4

	readonly property real baseSize: 256

	implicitWidth: baseSize * aspectW
	implicitHeight: baseSize * aspectH

	readonly property real maxBakedExtent: 4096
	readonly property real bakedW: Math.min(512 * aspectW, maxBakedExtent)
	readonly property real bakedH: Math.min(512 * aspectH, maxBakedExtent)

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
			source: Qt.resolvedUrl("../../assets/sprites/UI/TagBanner.png")
			border.left: 106
			border.top: 127
			border.right: 150
			border.bottom: 129
			smooth: true
		}
	}
}
