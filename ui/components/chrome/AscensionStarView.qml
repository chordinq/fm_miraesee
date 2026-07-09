import QtQuick
import ui 1.0

Item {
	id: root

	property int ascensionLevel: 0
	property real starSize: 32
	property real starSpacing: starSize * -0.6

	readonly property int starCount: Math.max(0, root.ascensionLevel)
	readonly property real rowWidth: starCount > 0
		? starCount * starSize + (starCount - 1) * starSpacing
		: 0

	implicitWidth: rowWidth
	implicitHeight: starCount > 0 ? starSize : 0
	visible: starCount > 0

	readonly property string starSource:
		Qt.resolvedUrl("../../assets/sprites/General/AscensionStar.png")

	Row {
		anchors.centerIn: parent
		spacing: root.starSpacing

		Repeater {
			model: root.starCount

			Image {
				required property int index

				width: root.starSize
				height: root.starSize
				source: root.starSource
				fillMode: Image.PreserveAspectFit
				smooth: true
				mipmap: true
				z: index === 1 ? 1 : 0
			}
		}
	}
}
