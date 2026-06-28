import QtQuick
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property int summonCount: 1
	property int cost
	property color fillColor: Theme.blue
	property bool enabled: true
	property url spriteImage: Qt.resolvedUrl("../../../assets/sprites/Currency/clockWinders.png")
	property real scaleW: 4
	property real scaleH: 2

	readonly property string summonLocId: "11670393447301120"
	readonly property real titleFontScale: 10 / 32
	readonly property real costFontScale: 11 / 32
	readonly property string formattedCost: {
		NumberDisplay.revision
		UiSettings.gameNumberFormattingEnabled
		return NumberDisplay.formatInteger(root.cost)
	}
	readonly property string formattedSummonCount: {
		NumberDisplay.revision
		UiSettings.gameNumberFormattingEnabled
		return NumberDisplay.formatInteger(root.summonCount)
	}

	signal clicked()

	readonly property real baseSize: 128
	readonly property real bakedWidth: baseSize * scaleW
	readonly property real bakedHeight: baseSize * scaleH

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
			id: background
			anchors.fill: parent
			scaleW: root.scaleW
			scaleH: root.scaleH
			fillColor: root.fillColor
		}

		MouseArea {
			anchors.fill: parent
			enabled: root.enabled
			onClicked: root.clicked()
		}

		RowLayout {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.verticalCenter: parent.verticalCenter
			anchors.verticalCenterOffset: -canvas.height * 0.18

			AppText {
				locId: root.summonLocId
				pixelSize: canvas.height * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignBaseline
			}

			AppText {
				text: "x" + root.formattedSummonCount
				pixelSize: canvas.height * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignBaseline
			}
		}

		RowLayout {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.verticalCenter: parent.verticalCenter
			anchors.verticalCenterOffset: canvas.height * 0.14

			Item {
				width: canvas.height * 25 / 64
				height: width
				Layout.alignment: Qt.AlignVCenter

				Image {
					anchors.fill: parent
					source: root.spriteImage
					fillMode: Image.PreserveAspectFit
					smooth: true
				}
			}

			AppText {
				text: root.formattedCost
				pixelSize: canvas.height * root.costFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}
		}
	}
}
