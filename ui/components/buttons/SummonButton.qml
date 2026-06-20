import QtQuick
import ui 1.0

Item {
	id: root

	property int summonCount: 5
	property int cost: 176
	property real scaleW: 4
	property real scaleH: 2

	readonly property string summonLocId: "11670393447301120"
	readonly property real titleFontScale: 7 / 32
	readonly property real costFontScale: 5 / 32

	signal clicked()

	implicitWidth: background.implicitWidth
	implicitHeight: background.implicitHeight

	RectRoundButton {
		id: background
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		fillColor: Theme.blue
	}

	MouseArea {
		anchors.fill: parent
		onClicked: root.clicked()
	}

	Column {
		anchors.centerIn: parent
		spacing: root.height * 0.04

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			segments: [
				{ locId: root.summonLocId },
				{ text: " x" + root.summonCount }
			]
			pixelSize: root.height * root.titleFontScale
			locLetterSpacing: 4
			rawLetterSpacing: 0
			segmentSpacing: root.height * 0.012
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}

		Row {
			anchors.horizontalCenter: parent.horizontalCenter
			spacing: root.height * 0.025

			Item {
				width: root.height * root.costFontScale * 0.95
				height: width

				Image {
					anchors.centerIn: parent
					width: parent.width
					height: parent.height
					source: Qt.resolvedUrl("../../../assets/sprites/Currency/skillTicket.png")
					fillMode: Image.PreserveAspectFit
					smooth: true
					rotation: 1
				}
			}

			AppText {
				anchors.verticalCenter: parent.verticalCenter
				segments: [{ text: root.cost }]
				pixelSize: root.height * root.costFontScale
				rawLetterSpacing: 0
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
			}
		}
	}
}
