import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property bool active: false
	property color backdropColor: "#A8000000"
	property color iconColor: Theme.white
	property real iconSizeRatio: 0.04

	anchors.fill: parent
	visible: active
	z: 1000

	Rectangle {
		anchors.fill: parent
		color: root.backdropColor
	}

	MouseArea {
		anchors.fill: parent
	}

	Item {
		id: spinnerHost

		anchors.centerIn: parent
		width: Math.max(48, Math.min(root.width, root.height) * root.iconSizeRatio)
		height: width
		transformOrigin: Item.Center

		RotationAnimator on rotation {
			from: 0
			to: 360
			duration: 1000
			loops: Animation.Infinite
			running: root.active
		}

		Image {
			id: spinnerSource

			anchors.fill: parent
			source: Qt.resolvedUrl("../../assets/sprites/UI/LoadingIcon.png")
			fillMode: Image.PreserveAspectFit
			smooth: true
			mipmap: true
			layer.enabled: true
			layer.smooth: true
			layer.mipmap: true
			layer.effect: MultiEffect {
				brightness: 1.0
				colorization: 1.0
				colorizationColor: root.iconColor
			}
		}
	}
}
