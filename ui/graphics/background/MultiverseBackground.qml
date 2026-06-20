import QtQuick
import Qt5Compat.GraphicalEffects
import ui 1.0

Item {
	id: root

	property real scaleW: 2
	property real scaleH: 2
	property real tileScale: 10
	property real nativeTileSize: 32
	property real baseDuration: 2500
	property real patternOpacity: 21 / 32

	readonly property real bakedW: 128 * scaleW
	readonly property real bakedH: 128 * scaleH
	readonly property real scaledTileSize: nativeTileSize * tileScale
	readonly property string patternImage: Qt.resolvedUrl("../../../assets/sprites/UI/MultiverseBackground.png")

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
			color: Theme.colorMultiverse
			visible: false
		}

		Item {
			id: scrollingPattern
			anchors.fill: parent
			visible: false

			Item {
				width: parent.width
				height: parent.height + root.scaledTileSize
				anchors.bottom: parent.bottom

				Image {
					width: parent.width / root.tileScale
					height: parent.height / root.tileScale
					source: root.patternImage
					fillMode: Image.Tile
					smooth: false
					transformOrigin: Item.TopLeft
					scale: root.tileScale
				}

				transform: Translate {
					NumberAnimation on y {
						from: 0
						to: root.scaledTileSize
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
			fillColor: "white"
			outlineOpacity: 0
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
