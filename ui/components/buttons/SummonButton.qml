import QtQuick
import QtQuick.Layouts
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

		RowLayout {
			anchors.horizontalCenter: parent.horizontalCenter
			spacing: root.height * 0.012

			AppText {
				locId: root.summonLocId
				pixelSize: root.height * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignBaseline
			}

			AppText {
				text: " x" + root.summonCount
				pixelSize: root.height * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignBaseline
			}
		}

		RowLayout {
			anchors.horizontalCenter: parent.horizontalCenter
			spacing: root.height * 0.025

			Item {
				width: root.height * root.costFontScale * 0.95
				height: width
				Layout.alignment: Qt.AlignVCenter

				Image {
					anchors.fill: parent
					source: Qt.resolvedUrl("../../../assets/sprites/Currency/skillTicket.png")
					fillMode: Image.PreserveAspectFit
					smooth: true
					rotation: 1
				}
			}

			AppText {
				text: root.cost
				pixelSize: root.height * root.costFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}
		}
	}
}
