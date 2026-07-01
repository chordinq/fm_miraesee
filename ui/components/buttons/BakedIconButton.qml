import QtQuick
import ui 1.0

Item {
	id: root

	property bool enabled: true
	property color fillColor: Theme.blue
	property real widthHeightRatio: 1
	property url iconSource
	property real iconScale: 0.5
	property real iconVerticalCenterOffsetRatio: 0
	property real iconRotation: 0
	property real pressScale: 0.9

	readonly property color effectiveFillColor:
		root.enabled ? root.fillColor : Theme.lightGrey

	signal clicked()

	readonly property real baseSize: 256
	readonly property real bakedWidth: baseSize * widthHeightRatio
	readonly property real bakedHeight: baseSize

	implicitWidth: bakedWidth
	implicitHeight: bakedHeight

	Item {
		id: pressVisual

		anchors.fill: parent
		transformOrigin: Item.Center
		scale: root.enabled && mouseArea.pressed ? root.pressScale : 1

		Behavior on scale {
			NumberAnimation {
				duration: 80
				easing.type: Easing.OutCubic
			}
		}

		Item {
			id: canvas

			width: root.bakedWidth
			height: root.bakedHeight
			transformOrigin: Item.TopLeft
			transform: Scale {
				xScale: pressVisual.width / canvas.width
				yScale: pressVisual.height / canvas.height
			}

			RectRoundButton {
				anchors.fill: parent
				scaleW: root.widthHeightRatio
				scaleH: 1
				fillColor: root.effectiveFillColor
			}

			Item {
				id: iconHost

				anchors.centerIn: parent
				anchors.verticalCenterOffset: root.bakedHeight * root.iconVerticalCenterOffsetRatio
				width: root.bakedHeight * root.iconScale
				height: width

				Image {
					anchors.fill: parent
					source: root.iconSource
					fillMode: Image.PreserveAspectFit
					rotation: root.iconRotation
					smooth: true
					mipmap: true
				}
			}
		}
	}

	MouseArea {
		id: mouseArea

		anchors.fill: parent
		enabled: root.enabled
		onClicked: root.clicked()
	}
}
