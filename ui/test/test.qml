import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "PopupView test"
	color: Theme.white

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	PopupView {
		id: popup

		anchors.centerIn: parent
		widthScale: 50
		heightScale: 45
		onClosed: console.log("PopupView closed")

		AppText {
			anchors.centerIn: parent
			text: "Popup content"
			fillColor: Theme.darkText
			pixelSize: popup.width * 0.045
			outlineWeight: 0
		}
	}
}
