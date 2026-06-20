import QtQuick
import Qt5Compat.GraphicalEffects
import ui 1.0

Item {
	id: root

	property real scaleW: 2
	property real scaleH: 2
	property real tileScale: 4
	property real nativeTileSize: 256
	property real baseDuration: 10000
	property int tileStepX: 1
	property int tileStepY: 2
	property real patternOpacity: 7 / 64

	readonly property real bakedW: 128 * scaleW
	readonly property real bakedH: 128 * scaleH
	readonly property real scaledTileSize: nativeTileSize * tileScale
	readonly property string patternImage: Qt.resolvedUrl("../../../assets/sprites/UI/UnderworldBackground.png")

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
			clip: false

			Item {
				id: scrollLayer
				width: parent.width + (root.tileStepX * root.scaledTileSize)
				height: parent.height + (root.tileStepY * root.scaledTileSize)
				anchors.right: parent.right
				anchors.bottom: parent.bottom

				Rectangle {
					id: colorFill
					anchors.fill: parent
					color: Theme.black
					visible: false
				}

				Item {
					id: scaledMaskLayer
					anchors.fill: parent
					visible: false

					Image {
						width: parent.width / root.tileScale
						height: parent.height / root.tileScale
						source: root.patternImage
						fillMode: Image.Tile
						smooth: true
						transformOrigin: Item.TopLeft
						scale: root.tileScale
					}
				}

				OpacityMask {
					anchors.fill: parent
					source: colorFill
					maskSource: scaledMaskLayer
					opacity: root.patternOpacity
				}

				transform: Translate {
					NumberAnimation on x {
						from: 0
						to: root.tileStepX * root.scaledTileSize
						duration: root.baseDuration * root.tileScale
						loops: Animation.Infinite
					}
					NumberAnimation on y {
						from: 0
						to: root.tileStepY * root.scaledTileSize
						duration: root.baseDuration * root.tileScale
						loops: Animation.Infinite
					}
				}
			}
		}

		RectRounded {
			id: maskShape
			anchors.fill: parent
			scaleW: root.scaleW
			scaleH: root.scaleH
			fillColor: Theme.white
			visible: false
		}

		OpacityMask {
			anchors.fill: parent
			source: patternSource
			maskSource: maskShape
		}
	}
}
