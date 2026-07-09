import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property real aspectW: 1
	property real aspectH: 1
	property real cornerRatio: 255 / 512
	property real cornerRatioW: cornerRatio
	property real cornerRatioH: cornerRatio

	property color fillColor: Theme.transparent
	property real fillOpacity: 1.0

	property color outlineColor: Theme.transparent
	property real outlineOpacity: 1.0

	readonly property real baseSize: 256
	readonly property real sourceSize: 512
	readonly property real sourceBorder: 255

	readonly property real bakeUnitsW: sourceBorder / (sourceSize * cornerRatioW)
	readonly property real bakeUnitsH: sourceBorder / (sourceSize * cornerRatioH)
	readonly property real bakedW: sourceBorder / cornerRatioW
	readonly property real bakedH: sourceBorder / cornerRatioH
	readonly property real cornerPxW: width * cornerRatioW
	readonly property real cornerPxH: height * cornerRatioH

	implicitWidth: baseSize * aspectW
	implicitHeight: baseSize * aspectH

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

		Item {
			anchors.fill: parent
			opacity: root.fillOpacity
			visible: root.fillColor.a > 0 && root.fillOpacity > 0

			BorderImage {
				id: fillBase
				anchors.fill: parent
				source: Qt.resolvedUrl("../../assets/sprites/UI/Rect_Extra_Rounded_Filled_Outline.png")
				border.left: root.sourceBorder
				border.top: root.sourceBorder
				border.right: root.sourceBorder
				border.bottom: root.sourceBorder
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
			visible: root.outlineColor.a > 0 && root.outlineOpacity > 0

			BorderImage {
				id: outlineBase
				anchors.fill: parent
				source: Qt.resolvedUrl("../../assets/sprites/UI/Rect_Extra_Rounded_Outline.png")
				border.left: root.sourceBorder
				border.top: root.sourceBorder
				border.right: root.sourceBorder
				border.bottom: root.sourceBorder
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
