import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
	id: root

	property real scaleW: 2.0
	property real scaleH: 0.72
	property color fillColor: Theme.white
	property real fillOpacity: 1.0

	property string locId: ""
	property string locTable: "General"
	property bool enabled: true
	property real labelScale: 0.22
	property real labelPixelSize: -1

	signal clicked()

	readonly property real baseSize: 256
	readonly property real bakedWidth: baseSize * scaleW
	readonly property real bakedHeight: baseSize * scaleH
	readonly property real bakedW: 512 * scaleW
	readonly property real bakedH: 512 * scaleH
	readonly property bool interactive: locId !== ""

	readonly property real _labelCanvasPixelSize: root.labelPixelSize >= 0
		? root.labelPixelSize * (canvas.height / root.height)
		: canvas.height * root.labelScale

	implicitWidth: bakedWidth
	implicitHeight: bakedHeight

	layer.enabled: true
	layer.smooth: true
	layer.mipmap: true

	Item {
		id: canvas

		width: root.bakedWidth
		height: root.bakedHeight
		transformOrigin: Item.TopLeft
		transform: Scale {
			xScale: root.width / canvas.width
			yScale: root.height / canvas.height
		}

		Item {
			id: bakeCanvas

			width: root.bakedW
			height: root.bakedH
			transformOrigin: Item.TopLeft
			transform: Scale {
				xScale: canvas.width / root.bakedW
				yScale: canvas.height / root.bakedH
				origin.x: 0
				origin.y: 0
			}

			Item {
				anchors.fill: parent
				opacity: root.fillOpacity
				visible: root.fillColor !== Theme.white && root.fillOpacity > 0

				BorderImage {
					id: bgBase

					anchors.fill: parent
					source: Qt.resolvedUrl("../../../assets/sprites/UI/Button.png")
					border.left: 100
					border.top: 100
					border.right: 100
					border.bottom: 370
					smooth: true
					visible: false
				}

				MultiEffect {
					anchors.fill: bgBase
					source: bgBase
					colorization: 1.0
					colorizationColor: root.fillColor
				}
			}
		}

		MouseArea {
			anchors.fill: parent
			visible: root.interactive
			enabled: root.enabled
			onClicked: root.clicked()
		}

		AppText {
			anchors.centerIn: parent
			visible: root.interactive
			locId: root.locId
			locTable: root.locTable
			pixelSize: root._labelCanvasPixelSize
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}
	}
}
