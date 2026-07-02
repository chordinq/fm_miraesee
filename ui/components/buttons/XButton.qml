import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property bool buttonEnabled: true
	property real pressScale: 0.9

	signal clicked()

	readonly property int sourceNativeSize: 256
	readonly property real labelScale: 0.45

	implicitWidth: sourceNativeSize
	implicitHeight: sourceNativeSize

	Item {
		id: pressVisual

		anchors.fill: parent
		transformOrigin: Item.Center
		scale: root.buttonEnabled && mouseArea.pressed ? root.pressScale : 1

		Behavior on scale {
			NumberAnimation {
				duration: 80
				easing.type: Easing.OutCubic
			}
		}

		SmallRoundButton {
			anchors.fill: parent
			fillColor: root.enabled ? Theme.red : Theme.lightGrey
		}

		TMPText {
			anchors.centerIn: parent
			tmpText: "x"
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
			pixelSize: parent.height * root.labelScale
		}
	}

	MouseArea {
		id: mouseArea

		anchors.fill: parent
		enabled: root.buttonEnabled
		onClicked: root.clicked()
	}
}
