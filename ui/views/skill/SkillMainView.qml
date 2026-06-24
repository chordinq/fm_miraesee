import QtQuick
import QtQuick.Controls
import ui 1.0

Rectangle {
	id: root

	property var skillSummonTest: null

	color: Theme.white

	readonly property real summonAspect: 4 / 2
	readonly property real summonButtonWidth: Math.min(
		width * 0.5,
		summonBar.height * 0.82 * summonAspect
	)
	readonly property real summonButtonHeight: summonButtonWidth / summonAspect
	readonly property real statusFontSize: Math.max(13, height * 0.03)
	readonly property real bodyFontSize: Math.max(12, height * 0.026)
	readonly property real actionFontSize: Math.max(12, height * 0.024)

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
				text: root.skillSummonTest ? root.skillSummonTest.statusText : ""
				fillColor: Theme.darkText
				pixelSize: root.statusFontSize
				outlineWeight: 0
			}
		}

		Flickable {
			id: predictionArea

			width: parent.width
			height: parent.height * 0.62
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
				text: root.skillSummonTest ? root.skillSummonTest.predictionText : ""
				font.family: Theme.latinFontFamily
				font.pixelSize: root.bodyFontSize
				color: Theme.darkText
				lineHeight: 1.35
				lineHeightMode: Text.ProportionalHeight
			}
		}

		Item {
			width: parent.width
			height: parent.height * 0.14

			Text {
				anchors.left: parent.left
				anchors.right: parent.right
				anchors.verticalCenter: parent.verticalCenter
				anchors.leftMargin: 12
				anchors.rightMargin: 12
				text: root.skillSummonTest ? root.skillSummonTest.lastActionText : ""
				font.family: Theme.latinFontFamily
				font.pixelSize: root.actionFontSize
				color: Theme.darkBlue
				wrapMode: Text.WordWrap
				maximumLineCount: 4
				elide: Text.ElideRight
			}
		}

		Rectangle {
			id: summonBar

			width: parent.width
			height: parent.height * 0.14
			color: Theme.darkBlue

			SummonButton {
				anchors.centerIn: parent
				width: root.summonButtonWidth
				height: root.summonButtonHeight
				summonCount: root.skillSummonTest ? root.skillSummonTest.summonCount : 1
				cost: root.skillSummonTest ? root.skillSummonTest.summonCost : 0
				spriteImage: root.skillSummonTest ? root.skillSummonTest.summonSpriteImage : ""
				onClicked: {
					if (root.skillSummonTest)
						root.skillSummonTest.performSummon()
				}
			}
		}
	}
}
