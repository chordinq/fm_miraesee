import QtQuick
import ui 1.0

Item {
	id: root

	property bool checked: false
	property real trackAspectW: 2.1
	property real trackAspectH: 1.4
	property real knobSizeRatio: 1.33

	signal toggled(bool checked)

	readonly property real trackAspectRatio: trackAspectW / trackAspectH
	readonly property real layoutAspectRatio: (trackAspectRatio + knobSizeRatio) / knobSizeRatio
	readonly property real baseSize: 256
	readonly property real trackWidth: baseSize * trackAspectRatio
	readonly property real trackHeight: baseSize
	readonly property real knobSize: trackHeight * knobSizeRatio
	readonly property real bakedWidth: trackWidth + knobSize
	readonly property real bakedHeight: knobSize
	readonly property real displayScale: bakedWidth > 0 && bakedHeight > 0
		? Math.min(root.width / bakedWidth, root.height / bakedHeight)
		: 1
	readonly property real knobLeftX: 0
	readonly property real knobRightX: trackWidth

	implicitWidth: bakedWidth
	implicitHeight: bakedHeight

	layer.enabled: true
	layer.smooth: true
	layer.mipmap: true

	Item {
		id: canvas

		width: root.bakedWidth
		height: root.bakedHeight
		anchors.centerIn: parent
		scale: root.displayScale
		transformOrigin: Item.Center

		Item {
			id: trackHost

			x: root.knobSize / 2
			width: root.trackWidth
			height: root.trackHeight
			anchors.verticalCenter: parent.verticalCenter

			RectRounded {
				anchors.fill: parent
				anchors.margins: parent.height * 0.05
				aspectW: root.trackAspectW
				aspectH: root.trackAspectH
		cornerRatioW: 255 / (512 * (root.trackAspectW))
		cornerRatioH: 255 / (512 * (root.trackAspectH))
				fillColor: root.checked ? Theme.green : Theme.checkBoxActiveGrey
			}

			RectRoundedOutline {
				anchors.fill: parent
				aspectW: root.trackAspectW
				aspectH: root.trackAspectH
		cornerRatioW: 255 / (512 * (root.trackAspectW))
		cornerRatioH: 255 / (512 * (root.trackAspectH))
				outlineColor: Theme.black
				z: 1
			}
		}

		SmallRoundButton {
			id: knob

			width: root.knobSize
			height: root.knobSize
			y: 0
			x: root.checked ? root.knobRightX : root.knobLeftX
			fillColor: Theme.blue
			z: 2

			Behavior on x {
				NumberAnimation {
					duration: 120
					easing.type: Easing.OutCubic
				}
			}
		}

		MouseArea {
			anchors.fill: parent
			onClicked: root.toggled(!root.checked)
		}
	}
}
