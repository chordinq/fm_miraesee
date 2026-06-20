import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property color fillColor: Theme.white
	property real fillOpacity: 1.0

	readonly property int sourceNativeSize: 256

	implicitWidth: sourceNativeSize
	implicitHeight: sourceNativeSize

	Item {
		anchors.fill: parent
		opacity: root.fillOpacity
		visible: root.fillColor.a > 0 && root.fillOpacity > 0

		Image {
			id: bgBase
			anchors.fill: parent
			source: Qt.resolvedUrl("../../assets/sprites/UI/SmallRoundButton.png")
			sourceSize: Qt.size(root.sourceNativeSize, root.sourceNativeSize)
			fillMode: Image.Stretch
			smooth: true
			visible: false
			layer.enabled: true
			layer.smooth: true
		}

		MultiEffect {
			anchors.fill: bgBase
			source: bgBase
			colorization: 1.0
			colorizationColor: root.fillColor
		}
	}
}
