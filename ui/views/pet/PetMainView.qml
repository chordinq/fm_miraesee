import QtQuick
import QtQuick.Controls
import ui 1.0

Rectangle {
	id: root

	property var eggHatchTest: null

	color: Theme.white

	readonly property real statusFontSize: Math.max(13, height * 0.03)
	readonly property real bodyFontSize: Math.max(12, height * 0.026)
	readonly property real hintFontSize: Math.max(12, height * 0.024)
	readonly property real actionFontSize: Math.max(12, height * 0.024)
	readonly property real hatchButtonWidth: Math.min(width * 0.42, hatchBar.height * 2.2)
	readonly property real hatchButtonHeight: hatchButtonWidth / 2

	Column {
		anchors.fill: parent
		spacing: 0

		Item {
			width: parent.width
			height: parent.height * 0.1

			AppText {
				anchors.left: parent.left
				anchors.right: parent.right
				anchors.verticalCenter: parent.verticalCenter
				anchors.leftMargin: 12
				anchors.rightMargin: 12
				text: root.eggHatchTest ? root.eggHatchTest.statusText : ""
				fillColor: Theme.darkText
				pixelSize: root.statusFontSize
				outlineWeight: 0
			}
		}

		Item {
			width: parent.width
			height: parent.height * 0.08

			AppText {
				anchors.left: parent.left
				anchors.right: parent.right
				anchors.verticalCenter: parent.verticalCenter
				anchors.leftMargin: 12
				anchors.rightMargin: 12
				text: "Egg hatch preview"
				fillColor: Theme.darkBlue
				pixelSize: root.hintFontSize
				outlineWeight: 0
			}
		}

		Flickable {
			id: predictionArea

			width: parent.width
			height: parent.height * 0.58
			clip: true
			boundsBehavior: Flickable.StopAtBounds
			contentWidth: width
			contentHeight: predictionBody.height

			ScrollBar.vertical: ScrollBar {
				policy: ScrollBar.AsNeeded
				contentItem: Rectangle {
					implicitWidth: 8
					radius: width / 2
					color: Theme.darkGrey
				}
			}

			Text {
				id: predictionBody

				width: predictionArea.width - 24
				x: 12
				text: root.eggHatchTest ? root.eggHatchTest.predictionText : ""
				font.family: Theme.latinFontFamily
				font.pixelSize: root.bodyFontSize
				color: Theme.darkText
				lineHeight: 1.35
				lineHeightMode: Text.ProportionalHeight
			}
		}

		Item {
			width: parent.width
			height: parent.height * 0.12

			Text {
				anchors.left: parent.left
				anchors.right: parent.right
				anchors.verticalCenter: parent.verticalCenter
				anchors.leftMargin: 12
				anchors.rightMargin: 12
				text: root.eggHatchTest ? root.eggHatchTest.lastActionText : ""
				font.family: Theme.latinFontFamily
				font.pixelSize: root.actionFontSize
				color: Theme.darkBlue
				wrapMode: Text.WordWrap
				maximumLineCount: 3
				elide: Text.ElideRight
			}
		}

		Rectangle {
			id: hatchBar

			width: parent.width
			height: parent.height * 0.12
			color: Theme.darkBlue

			Item {
				anchors.centerIn: parent
				width: root.hatchButtonWidth
				height: root.hatchButtonHeight

				RectRoundButton {
					id: hatchButtonBg
					anchors.fill: parent
					scaleW: 2
					scaleH: 1
					fillColor: root.eggHatchTest && root.eggHatchTest.canHatchSelected
						? Theme.green
						: Theme.darkGrey
				}

				AppText {
					anchors.centerIn: parent
					text: "Hatch"
					fillColor: Theme.white
					pixelSize: parent.height * 0.42
					outlineColor: Theme.black
					outlineWeight: 8
				}

				MouseArea {
					anchors.fill: parent
					enabled: root.eggHatchTest && root.eggHatchTest.canHatchSelected
					onClicked: root.eggHatchTest.performSelectedHatch()
				}
			}
		}
	}
}
