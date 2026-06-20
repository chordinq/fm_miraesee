import QtQuick
import QtQuick.Effects

Item {
	id: root

	property real scaleW: 1.0
	property real scaleH: 1.0

	property color fillColor: "transparent"
	property real fillOpacity: 1.0

	property color outlineColor: "transparent"
	property real outlineOpacity: 1.0

	readonly property real baseSize: 256

	implicitWidth: baseSize * scaleW
	implicitHeight: baseSize * scaleH

	readonly property real bakedW: 512 * scaleW
	readonly property real bakedH: 512 * scaleH

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

		Item {
			anchors.fill: parent
			opacity: root.fillOpacity
			visible: root.fillColor !== "#00000000" && root.fillOpacity > 0

			BorderImage {
				id: fillBase
				anchors.fill: parent
				source: Qt.resolvedUrl("../../assets/sprites/UI/Rect_Extra_Rounded_Filled_Outline.png")
				border.left: 255
				border.top: 255
				border.right: 255
				border.bottom: 255
				smooth: true
				visible: false
				layer.enabled: true
				layer.smooth: true
			}

			MultiEffect {
				anchors.fill: fillBase
				source: fillBase
				colorization: 1.0
				colorizationColor: root.fillColor
			}
		}

		Item {
			anchors.fill: parent
			opacity: root.outlineOpacity
			visible: root.outlineColor !== "#00000000" && root.outlineOpacity > 0

			BorderImage {
				id: outlineBase
				anchors.fill: parent
				source: Qt.resolvedUrl("../../assets/sprites/UI/Rect_Extra_Rounded_Outline.png")
				border.left: 255
				border.top: 255
				border.right: 255
				border.bottom: 255
				smooth: true
				visible: false
				layer.enabled: true
				layer.smooth: true
			}

			MultiEffect {
				anchors.fill: outlineBase
				source: outlineBase
				colorization: 1.0
				colorizationColor: root.outlineColor
			}
		}
	}
}
