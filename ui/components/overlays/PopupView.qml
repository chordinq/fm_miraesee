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
	property bool blockBackdropClicks: true
	property bool dimBackdrop: false
	property color backdropColor: "#A8000000"
	property bool closeOnBackdropClick: true
	property bool bakeLayout: false
	property real layoutBaseWidth: 720

	signal closed()

	default property alias content: contentHost.data

	readonly property real cornerRatioW: 1 / widthScale
	readonly property real cornerRatioH: 1 / heightScale
	readonly property real heightWidthRatio: heightScale / widthScale

	readonly property real panelWidth: parent ? parent.width * parentWidthRatio : 0
	readonly property real panelHeight: panelWidth * heightWidthRatio

	readonly property real layoutBaseHeight: layoutBaseWidth * heightWidthRatio

	readonly property real layoutFrameWidth: root.bakeLayout ? layoutBaseWidth : panelWidth
	readonly property real layoutFrameHeight: root.bakeLayout ? layoutBaseHeight : panelHeight

	readonly property real contentInsetW: contentInsetWOverride >= 0
		? contentInsetWOverride
		: layoutFrameWidth / widthScale
	readonly property real contentInsetH: contentInsetHOverride >= 0
		? contentInsetHOverride
		: layoutFrameHeight / heightScale
	readonly property real closeSize: panelWidth * closeButtonSizeRatio

	Rectangle {
		anchors.fill: parent
		visible: root.dimBackdrop
		color: root.backdropColor
	}

	MouseArea {
		anchors.fill: parent
		enabled: root.blockBackdropClicks
		z: 0
		onClicked: (mouse) => {
			if (!root.closeOnBackdropClick)
				return
			var panelPos = panel.mapFromItem(root, mouse.x, mouse.y)
			if (panelPos.x >= 0 && panelPos.x <= panel.width
					&& panelPos.y >= 0 && panelPos.y <= panel.height)
				return
			var closePos = closeButton.mapFromItem(root, mouse.x, mouse.y)
			if (closePos.x >= 0 && closePos.x <= closeButton.width
					&& closePos.y >= 0 && closePos.y <= closeButton.height)
				return
			root.closed()
		}
	}

	Item {
		id: panel

		z: 1
		width: root.panelWidth
		height: root.panelHeight
		anchors.centerIn: parent

		MouseArea {
			anchors.fill: parent
			z: 0
		}

		Item {
			id: layoutCanvas

			width: root.layoutFrameWidth
			height: root.layoutFrameHeight
			transformOrigin: Item.TopLeft
			transform: Scale {
				xScale: root.bakeLayout ? panel.width / layoutCanvas.width : 1
				yScale: root.bakeLayout ? panel.height / layoutCanvas.height : 1
			}

			RectRoundedFilledOutline {
				id: panelFrame

				z: 1
				anchors.fill: parent
				widthScale: root.widthScale
				heightScale: root.heightScale
			}

			Item {
				id: contentHost

				z: 1
				anchors.left: panelFrame.left
				anchors.right: panelFrame.right
				anchors.top: panelFrame.top
				anchors.bottom: panelFrame.bottom
				anchors.leftMargin: root.contentInsetW
				anchors.rightMargin: root.contentInsetW
				anchors.topMargin: root.contentInsetH
				anchors.bottomMargin: root.contentInsetH
			}
		}

		XButton {
			id: closeButton

			z: 2
			width: root.closeSize
			height: root.closeSize
			anchors.horizontalCenter: panel.horizontalCenter
			anchors.top: panel.bottom
			anchors.topMargin: -height * 0.5
			onClicked: root.closed()
		}
	}
}
