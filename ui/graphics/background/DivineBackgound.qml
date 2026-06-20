import QtQuick
import Qt5Compat.GraphicalEffects
import ui 1.0

Item {
	id: root

	property real scaleW: 2
	property real scaleH: 2
	property real cellSize: 64
	property real starOpacity: 1 / 2

	readonly property real bakedW: cellSize * scaleW
	readonly property real bakedH: cellSize * scaleH
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
						width: starCanvas.width
						height: root.cellSize
						y: index * root.cellSize
						property bool staggered: index % 2 === 1

						Repeater {
							model: starCanvas.colCount
							delegate: Image {
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
			scaleW: root.scaleW
			scaleH: root.scaleH
			fillColor: "white"
			visible: false
		}

		OpacityMask {
			anchors.fill: parent
			source: patternSource
			maskSource: maskShape
		}
	}
}
