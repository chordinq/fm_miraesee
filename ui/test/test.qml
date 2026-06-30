import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "LockButton test"
	color: Theme.darkBlue

	property bool lockA: false
	property bool lockB: true

	readonly property real outerMargin: Math.max(16, width * 0.05)
	readonly property real sectionSpacing: Math.max(24, height * 0.04)
	readonly property real buttonSize: Math.min(width * 0.28, height * 0.22, 128)

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	Column {
		anchors.centerIn: parent
		spacing: sectionSpacing

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			text: "LockButton"
			pixelSize: Math.max(20, width * 0.05)
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}

		LockButton {
			id: lockA

			anchors.horizontalCenter: parent.horizontalCenter
			width: buttonSize
			height: buttonSize
			isLocked: window.lockA
			onClicked: {
				window.lockA = !window.lockA
				console.log("lockA", window.lockA)
			}
		}

		LockButton {
			id: lockB

			anchors.horizontalCenter: parent.horizontalCenter
			width: buttonSize
			height: buttonSize
			isLocked: window.lockB
			onClicked: {
				window.lockB = !window.lockB
				console.log("lockB", window.lockB)
			}
		}

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			text: "A: " + (window.lockA ? "Locked" : "Unlocked")
				+ "  B: " + (window.lockB ? "Locked" : "Unlocked")
			pixelSize: Math.max(14, width * 0.035)
			fillColor: Theme.white
			outlineWeight: 0
		}
	}
}
