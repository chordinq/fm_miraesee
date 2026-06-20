import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "Skill summon test (" + gameTest.skillCollection.skillCount + " skills)"
	color: Theme.white

	readonly property real summonAspect: 4 / 2
	readonly property real summonButtonWidth: sidePanel.width * 0.88
	readonly property real summonButtonHeight: summonButtonWidth / summonAspect

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	RowLayout {
		anchors.fill: parent
		spacing: 0

		SkillCollection {
			Layout.fillWidth: true
			Layout.fillHeight: true
			Layout.preferredWidth: parent.width * 0.68
			skillCollectionModel: gameTest.skillCollection
		}

		Rectangle {
			id: sidePanel
			Layout.fillHeight: true
			Layout.preferredWidth: parent.width * 0.32
			color: Theme.lightGrey

			ColumnLayout {
				anchors.fill: parent
				anchors.margins: 16
				spacing: 12

				Text {
					Layout.fillWidth: true
					text: gameTest.statusText
					font.pixelSize: 14
					color: Theme.black
					wrapMode: Text.WordWrap
				}

				Item {
					Layout.fillWidth: true
					Layout.preferredHeight: summonButtonHeight

					SummonButton {
						anchors.horizontalCenter: parent.horizontalCenter
						width: summonButtonWidth
						height: summonButtonHeight
						summonCount: gameTest.summonCount
						cost: gameTest.summonCost
						spriteImage: gameTest.summonSpriteImage
						onClicked: gameTest.performSummon()
					}
				}

				Item {
					Layout.fillWidth: true
					Layout.preferredHeight: 48

					RectRoundButton {
						anchors.fill: parent
						scaleW: 2
						scaleH: 1
						fillColor: Theme.blue
					}

					MouseArea {
						anchors.fill: parent
						onClicked: gameTest.predictSummon()
					}

					AppText {
						anchors.centerIn: parent
						text: "Predict"
						pixelSize: 18
						fillColor: Theme.white
						outlineWeight: 6
					}
				}

				ScrollView {
					Layout.fillWidth: true
					Layout.fillHeight: true
					clip: true

					Text {
						width: sidePanel.width - 32
						text: gameTest.predictionText
						font.pixelSize: 13
						font.family: Theme.latinFontFamily
						color: Theme.black
						wrapMode: Text.WordWrap
					}
				}

				Text {
					Layout.fillWidth: true
					text: gameTest.lastActionText
					font.pixelSize: 12
					color: Theme.black
					wrapMode: Text.WordWrap
					visible: gameTest.lastActionText !== ""
				}
			}
		}
	}
}
