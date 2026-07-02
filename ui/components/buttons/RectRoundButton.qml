import QtQuick
import QtQuick.Effects
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property real scaleW: 2.0
	property real scaleH: 0.72
	property color fillColor: Theme.white
	property real fillOpacity: 1.0

	property string locId: ""
	property string locTable: "General"
	property string labelText: ""
	property bool buttonEnabled: true
	property bool handleInput: root.interactive
	property real pressScale: 0.9
	property bool pressScaleEnabled: root.handleInput
	property real labelScale: 0.22
	property real labelPixelSize: -1
	property real labelWidthRatio: 0.86

	signal clicked()

	readonly property real baseSize: 256
	readonly property real buttonAspect: scaleW / scaleH
	readonly property real layoutHeight: height > 0 ? height : implicitHeight
	readonly property real bakedWidth: baseSize * scaleW
	readonly property real bakedHeight: baseSize * scaleH
	readonly property real bakedW: 512 * scaleW
	readonly property real bakedH: 512 * scaleH
	readonly property bool interactive: locId !== "" || labelText !== ""

	readonly property string resolvedLabel: {
		UiLocale.selectedCode
		if (root.labelText !== "")
			return root.labelText
		if (root.locId === "")
			return ""
		return TmpTextBridge.localized_text_table(
			root.locId,
			UiLocale.selectedCode,
			root.locTable
		)
	}

	readonly property color effectiveFillColor:
		root.handleInput && !root.buttonEnabled
			? Theme.lightGrey
			: root.fillColor

	readonly property real _labelCanvasPixelSize: root.labelPixelSize >= 0
		? root.labelPixelSize * (canvas.height / root.height)
		: canvas.height * root.labelScale

	implicitWidth: bakedWidth
	implicitHeight: bakedHeight
	width: layoutHeight * buttonAspect

	default property alias content: overlay.data
	property alias contentHost: overlay

	layer.enabled: true
	layer.smooth: true
	layer.mipmap: true

	Item {
		id: pressVisual

		anchors.fill: parent
		transformOrigin: Item.Center
		scale: root.pressScaleEnabled && root.buttonEnabled && mouseArea.pressed
			? root.pressScale
			: 1

		Behavior on scale {
			enabled: root.pressScaleEnabled
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
					visible: root.effectiveFillColor !== Theme.white && root.fillOpacity > 0

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
						colorizationColor: root.effectiveFillColor
					}
				}
			}

			Item {
				id: labelHost

				anchors.centerIn: parent
				visible: root.interactive
				width: canvas.width * root.labelWidthRatio
				height: labelTextItem.implicitHeight

				TMPText {
					id: labelTextItem

					anchors.centerIn: parent
					tmpText: root.resolvedLabel
					pixelSize: root._labelCanvasPixelSize
					fillColor: Theme.white
					outlineColor: Theme.black
					outlineWeight: 8
					scale: Math.min(1, labelHost.width / Math.max(implicitWidth, 1))
					transformOrigin: Item.Center
				}
			}

			Item {
				id: overlay

				anchors.fill: parent
			}
		}
	}

	MouseArea {
		id: mouseArea

		anchors.fill: parent
		visible: root.handleInput
		enabled: root.buttonEnabled
		onClicked: root.clicked()
	}
}
