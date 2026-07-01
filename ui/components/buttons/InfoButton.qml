import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	signal clicked()

	readonly property real baseSize: 256

	implicitWidth: baseSize
	implicitHeight: baseSize

	Item {
		anchors.fill: parent

		Image {
			id: iconBase

			anchors.fill: parent
			source: Qt.resolvedUrl("../../../assets/sprites/General/InfoIcon.png")
			fillMode: Image.PreserveAspectFit
			smooth: true
			mipmap: true
			visible: false
			layer.enabled: true
			layer.smooth: true
			layer.mipmap: true
		}

		MultiEffect {
			anchors.fill: iconBase
			source: iconBase
			colorization: 1.0
			colorizationColor: Theme.black
		}
	}

	MouseArea {
		anchors.fill: parent
		onClicked: root.clicked()
	}
}
