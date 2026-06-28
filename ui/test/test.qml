import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "SettingToggleButton test"
	color: Theme.darkBlue

	property bool toggleA: true
	property bool toggleB: false
	property bool toggleC: true

	readonly property real outerMargin: Math.max(16, width * 0.05)
	readonly property real sectionSpacing: Math.max(20, height * 0.04)
	readonly property real toggleBaseHeight: Math.min(width * 0.14, 56)

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	Column {
		anchors.centerIn: parent
		spacing: sectionSpacing

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			text: "SettingToggleButton"
			pixelSize: Math.max(20, width * 0.05)
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}

		SettingToggleButton {
			id: toggleA

			anchors.horizontalCenter: parent.horizontalCenter
			height: toggleBaseHeight
			width: height * layoutAspectRatio
			checked: window.toggleA
			onToggled: function(enabled) {
				window.toggleA = enabled
				console.log("toggleA", enabled)
			}
		}

		SettingToggleButton {
			id: toggleB

			anchors.horizontalCenter: parent.horizontalCenter
			height: toggleBaseHeight
			width: height * layoutAspectRatio
			checked: window.toggleB
			onToggled: function(enabled) {
				window.toggleB = enabled
				console.log("toggleB", enabled)
			}
		}

		SettingToggleButton {
			id: toggleC

			anchors.horizontalCenter: parent.horizontalCenter
			height: toggleBaseHeight * 0.75
			width: height * layoutAspectRatio
			checked: window.toggleC
			onToggled: function(enabled) {
				window.toggleC = enabled
				console.log("toggleC", enabled)
			}
		}

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			text: "ratio " + toggleA.trackScaleW + ":" + toggleA.trackScaleH
				+ "  A:" + (window.toggleA ? "ON" : "OFF")
				+ "  B:" + (window.toggleB ? "ON" : "OFF")
				+ "  C:" + (window.toggleC ? "ON" : "OFF")
			pixelSize: Math.max(14, width * 0.035)
			fillColor: Theme.white
			outlineWeight: 0
		}
	}
}
