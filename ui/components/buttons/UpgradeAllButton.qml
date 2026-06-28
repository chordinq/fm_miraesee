import QtQuick
import ui 1.0

Item {
	id: root

	property color fillColor: Theme.blue
	property bool enabled: true
	property real scaleW: 2.4
	property real scaleH: 0.72

	readonly property string upgradeAllLocId: "2061927358066688"
	readonly property real labelScale: 0.22

	signal clicked()

	readonly property real baseSize: 256
	readonly property real bakedWidth: baseSize * scaleW
	readonly property real bakedHeight: baseSize * scaleH

	implicitWidth: bakedWidth
	implicitHeight: bakedHeight

	Item {
		id: canvas

		width: root.bakedWidth
		height: root.bakedHeight
		transformOrigin: Item.TopLeft
		transform: Scale {
			xScale: root.width / canvas.width
			yScale: root.height / canvas.height
		}

		RectRoundButton {
			anchors.fill: parent
			scaleW: root.scaleW
			scaleH: root.scaleH
			fillColor: root.fillColor
		}

		MouseArea {
			anchors.fill: parent
			enabled: root.enabled
			onClicked: root.clicked()
		}

		AppText {
			anchors.centerIn: parent
			locId: root.upgradeAllLocId
			locTable: "Skills"
			pixelSize: canvas.height * root.labelScale
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}
	}
}
