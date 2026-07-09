import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property real maskAspectW: 2
	property real maskAspectH: 2
	property real ringOpacity: 15 / 128

	readonly property real bakedW: 128 * maskAspectW
	readonly property real bakedH: 128 * maskAspectH
	readonly property int ringWidth: 32
	readonly property int ringGap: 32
	readonly property int stepDiameter: (ringWidth + ringGap) * 2

	property int ringCount: 6
	property int animDuration: 1000

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
			id: patternSource

			anchors.fill: parent
			visible: false
			layer.enabled: true
			layer.live: true
			layer.smooth: true

			property real animOffset: 0.0

			NumberAnimation on animOffset {
				from: 0.0
				to: root.stepDiameter
				duration: root.animDuration
				loops: Animation.Infinite
			}

			Repeater {
				model: root.ringCount

				Rectangle {
					anchors.centerIn: parent
					width: patternSource.animOffset + (index * root.stepDiameter)
					height: width
					radius: width / 2
					color: Theme.transparent
					border.color: Theme.white
					border.width: root.ringWidth
					opacity: root.ringOpacity
				}
			}
		}

		RectRounded {
			id: maskShape

			anchors.fill: parent
			aspectW: root.maskAspectW
			aspectH: root.maskAspectH
		cornerRatioW: 255 / (512 * (root.maskAspectW))
		cornerRatioH: 255 / (512 * (root.maskAspectH))
			fillColor: Theme.white
			visible: false
			layer.enabled: true
			layer.smooth: true
		}

		MultiEffect {
			anchors.fill: parent
			source: patternSource
			maskEnabled: true
			maskSource: maskShape
		}
	}
}
