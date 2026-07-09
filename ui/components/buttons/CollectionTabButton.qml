import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property string locId: ""
	property string locTable: "General"
	property string labelText: ""
	property color activeColor: Theme.lightGrey
	property bool active: false
	property real aspectW: 4
	property real aspectH: 1

	signal clicked()

	readonly property real baseSize: 128
	readonly property real bakedWidth: baseSize * aspectW
	readonly property real bakedHeight: baseSize * aspectH
	readonly property real labelFontScale: 52 / 100
	readonly property real labelWidthRatio: 0.86

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
			height: parent.height
			width: height * aspectW / aspectH
			aspectW: root.aspectW
			aspectH: root.aspectH
			fillColor: root.active ? root.activeColor : Theme.lightGrey
		}

		TMPText {
			id: tabLabel

			anchors.centerIn: parent
			tmpText: root.resolvedLabel
			pixelSize: canvas.height * root.labelFontScale
			fillColor: Theme.white
			outlineWeight: 6
			scale: Math.min(
				1,
				canvas.width * root.labelWidthRatio / Math.max(implicitWidth, 1)
			)
			transformOrigin: Item.Center
		}

		MouseArea {
			anchors.fill: parent
			onClicked: root.clicked()
		}
	}
}
