import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "HatchSlot test"
	color: Qt.lighter(Theme.darkBlue, 2.22)

	readonly property real previewScale: Math.min(width, height) * 0.7 / 256

	Row {
		anchors.centerIn: parent
		spacing: 48

		Item {
			width: 256 * previewScale
			height: slot1.implicitHeight * previewScale
			//color: "#888888"

			HatchSlot {
				id: slot1
				eggModel: hatchEggModels.length > 0 ? hatchEggModels[0] : null
				scale: previewScale
				transformOrigin: Item.TopLeft
			}
		}

		Item {
			width: 256 * previewScale
			height: slot2.implicitHeight * previewScale

			HatchSlot {
				id: slot2
				scale: previewScale
				transformOrigin: Item.TopLeft
			}
		}
	}
}
