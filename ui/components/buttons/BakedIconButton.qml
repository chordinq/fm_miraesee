import QtQuick
import ui 1.0

Item {
	id: root

	property color fillColor: Theme.white
	property real widthHeightRatio: 1
	property url iconSource
	property real iconScale: 0.5
	property real iconVerticalCenterOffsetRatio: 0
	property real iconRotation: 0

	signal clicked()

	readonly property real baseSize: 256
	readonly property real bakedWidth: baseSize * widthHeightRatio
	readonly property real bakedHeight: baseSize
	readonly property real bakedW: 512 * widthHeightRatio
	readonly property real bakedH: 512
	readonly property real displayScale: bakedWidth > 0 && bakedHeight > 0
		? Math.min(root.width / bakedWidth, root.height / bakedHeight)
		: 1

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

		RectRoundButton {
			anchors.fill: parent
			scaleW: root.widthHeightRatio
			scaleH: 1
			fillColor: root.fillColor
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

		MouseArea {
			anchors.fill: parent
			onClicked: root.clicked()
		}
	}
}
