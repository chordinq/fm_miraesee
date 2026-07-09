import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property real maskAspectW: 2
	property real maskAspectH: 2
	property real cellSize: 64
	property real starOpacity: 1 / 2

	readonly property real bakedW: cellSize * maskAspectW
	readonly property real bakedH: cellSize * maskAspectH
	readonly property string starSource: Qt.resolvedUrl("../../../assets/sprites/UI/DivineBackground.png")

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

			Item {
				id: starCanvas

				width: parent.width * 2
				height: parent.height * 2
				anchors.centerIn: parent

				property int rowCount: Math.ceil(height / root.cellSize) + 2
				property int colCount: Math.ceil(width / root.cellSize) + 3

				Repeater {
					model: starCanvas.rowCount

					delegate: Item {
						id: rowItem

						required property int index

						width: starCanvas.width
						height: root.cellSize
						y: index * root.cellSize
						property bool staggered: index % 2 === 1

						Repeater {
							model: starCanvas.colCount

							delegate: Image {
								required property int index

								x: index * root.cellSize + (rowItem.staggered ? root.cellSize * 0.5 : 0)
								width: root.cellSize
								height: root.cellSize
								source: root.starSource
								fillMode: Image.PreserveAspectFit
								opacity: root.starOpacity
								smooth: true
							}
						}
					}
				}

				transform: [
					Translate {
						NumberAnimation on x {
							from: 0
							to: -root.cellSize * 2
							duration: 3000
							loops: Animation.Infinite
						}
					},
					Rotation {
						angle: -20
						origin.x: starCanvas.width / 2
						origin.y: starCanvas.height / 2
					}
				]
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
