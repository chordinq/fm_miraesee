import QtQuick
import ui 1.0

Item {
	id: root

	property real widthScale: 50
	property real heightScale: 50
	property real parentWidthRatio: 0.9
	property real closeButtonSizeRatio: 0.15
	property real contentInsetWOverride: -1
	property real contentInsetHOverride: -1

	signal closed()

	default property alias content: contentHost.data

	readonly property real cornerRatioW: 1 / widthScale
	readonly property real cornerRatioH: 1 / heightScale
	readonly property real heightWidthRatio: heightScale / widthScale

	width: parent ? parent.width * parentWidthRatio : 0
	height: width * heightWidthRatio

	readonly property real contentInsetW: contentInsetWOverride >= 0
		? contentInsetWOverride
		: width / widthScale
	readonly property real contentInsetH: contentInsetHOverride >= 0
		? contentInsetHOverride
		: height / heightScale
	readonly property real closeSize: width * closeButtonSizeRatio

	RectRoundedFilledOutline {
		id: panel

		anchors.fill: parent
		widthScale: root.widthScale
		heightScale: root.heightScale
	}

	Item {
		id: contentHost

		anchors.left: panel.left
		anchors.right: panel.right
		anchors.top: panel.top
		anchors.bottom: panel.bottom
		anchors.leftMargin: root.contentInsetW
		anchors.rightMargin: root.contentInsetW
		anchors.topMargin: root.contentInsetH
		anchors.bottomMargin: root.contentInsetH
	}

	XButton {
		id: closeButton

		width: root.closeSize
		height: root.closeSize
		anchors.horizontalCenter: panel.horizontalCenter
		anchors.top: panel.bottom
		anchors.topMargin: -height * 0.5
		onClicked: root.closed()
	}
}
