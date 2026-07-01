import QtQuick
import QtQuick.Controls

ApplicationWindow {
	id: root

	flags: Qt.FramelessWindowHint | Qt.Window
	width: loadingWinWidth
	height: loadingWinHeight
	x: loadingWinX
	y: loadingWinY
	visible: true
	color: "#272C38"

	Column {
		anchors.centerIn: parent
		spacing: height * 0.04

		Text {
			anchors.horizontalCenter: parent.horizontalCenter
			text: "Miraesee"
			color: "#FFFFFF"
			font.pixelSize: Math.max(32, root.height * 0.06)
			font.bold: true
		}

		BusyIndicator {
			anchors.horizontalCenter: parent.horizontalCenter
			running: true
			palette.dark: "#00A3FF"
		}
	}
}
