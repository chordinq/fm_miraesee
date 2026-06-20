import QtQuick
import Qt5Compat.GraphicalEffects
import ui 1.0

Item {
	id: root

	property real scaleW: 4.0
	property real scaleH: 4.0
	property real tileScale: 4.0
	property real nativeTileSize: 256
	property real baseDuration: 7500
	property real patternOpacity: 21 / 32

	readonly property real bakedW: 128 * scaleW
	readonly property real bakedH: 128 * scaleH
	readonly property real scaledTileSize: nativeTileSize * tileScale
	readonly property string patternImage: Qt.resolvedUrl("../../../assets/sprites/UI/InterstellarBackground.png")

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

		Rectangle {
			id: bgColor
			anchors.fill: parent
			color: Theme.colorInterstellar
			visible: false
		}

		Item {
			id: scrollingPattern
			anchors.fill: parent
			visible: false
			clip: false

			Item {
				width: parent.width + root.scaledTileSize
				height: parent.height + root.scaledTileSize
				anchors.right: parent.right
				anchors.top: parent.top

				Image {
					width: parent.width / root.tileScale
					height: parent.height / root.tileScale
					source: root.patternImage
					fillMode: Image.Tile
					smooth: true
					transformOrigin: Item.TopLeft
					scale: root.tileScale
				}

				transform: Translate {
					NumberAnimation on x {
						from: 0
						to: root.scaledTileSize
						duration: root.baseDuration * root.tileScale
						loops: Animation.Infinite
					}
					NumberAnimation on y {
						from: 0
						to: -root.scaledTileSize
						duration: root.baseDuration * root.tileScale
						loops: Animation.Infinite
					}
				}
			}
		}

		Blend {
			id: blendedPattern
			anchors.fill: parent
			source: bgColor
			foregroundSource: scrollingPattern
			mode: "screen"
			visible: false
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
			source: blendedPattern
			maskSource: maskShape
			opacity: root.patternOpacity
		}
	}
}
