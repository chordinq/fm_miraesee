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

	property color fillColor: Theme.white
	property real fillOpacity: 1.0

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
				source: Qt.resolvedUrl("../../assets/sprites/UI/Rect_Rounded_Filled.png")
				border.left: root.sourceBorder
				border.top: root.sourceBorder
				border.right: root.sourceBorder
				border.bottom: root.sourceBorder
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
