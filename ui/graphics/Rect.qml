import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property real scaleW: 1.0
	property real scaleH: 1.0

	property color fillColor: Theme.white
	property real fillOpacity: 1.0

	readonly property real baseSize: 256
	readonly property real sourceSize: 128

	implicitWidth: baseSize * scaleW
	implicitHeight: baseSize * scaleH

	readonly property real bakedW: sourceSize * scaleW
	readonly property real bakedH: sourceSize * scaleH

	Item {
		anchors.fill: parent
		opacity: root.fillOpacity
		visible: root.fillColor.a > 0 && root.fillOpacity > 0

		Item {
			id: effectSource
			anchors.fill: parent
			visible: false
			layer.enabled: true
			layer.smooth: true
			layer.mipmap: true

			BorderImage {
				width: root.bakedW
				height: root.bakedH
				transformOrigin: Item.TopLeft
				transform: Scale {
					xScale: root.width / root.bakedW
					yScale: root.height / root.bakedH
				}
				source: Qt.resolvedUrl("../../assets/sprites/UI/Rect_Filled.png")
				border.left: 63
				border.top: 63
				border.right: 63
				border.bottom: 63
				smooth: true
			}
		}

		MultiEffect {
			anchors.fill: effectSource
			source: effectSource
			colorization: 1.0
			colorizationColor: root.fillColor
		}
	}
}
