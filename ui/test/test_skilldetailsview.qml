pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "SkillDetailsView preview"
	color: Theme.white

	property bool detailsOpen: true
	property int ascensionLevel: 0

	readonly property real collectionWidthRatio: 5 / 16

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	Row {
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		anchors.margins: Math.max(16, width * 0.02)
		spacing: Math.max(12, width * 0.015)

		AppText {
			text: testSkillModel
				? testSkillModel.skillKey + "  L" + (testSkillModel.level + 1)
				: ""
			pixelSize: Math.max(16, width * 0.022)
			fillColor: Theme.black
			outlineWeight: 0
		}

		Repeater {
			model: testAscensionLevels

			Rectangle {
				required property int modelData

				width: Math.max(72, window.width * 0.08)
				height: Math.max(36, window.height * 0.05)
				radius: height * 0.2
				color: window.ascensionLevel === modelData ? Theme.blue : Theme.lightGrey

				AppText {
					anchors.centerIn: parent
					text: "A" + parent.modelData
					pixelSize: parent.height * 0.42
					fillColor: Theme.white
					outlineWeight: 0
				}

				MouseArea {
					anchors.fill: parent
					onClicked: window.ascensionLevel = modelData
				}
			}
		}
	}

	Rectangle {
		id: collectionPanel

		width: parent.width * window.collectionWidthRatio
		height: parent.height * 0.82
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: parent.bottom
		anchors.bottomMargin: Math.max(16, height * 0.03)
		color: Theme.commonGrey

		AppText {
			anchors.centerIn: parent
			visible: !window.detailsOpen
			text: "Closed — click to reopen"
			pixelSize: Math.max(14, parent.width * 0.04)
			fillColor: Theme.darkGreyText
			outlineWeight: 0
		}

		MouseArea {
			anchors.fill: parent
			visible: !window.detailsOpen
			onClicked: window.detailsOpen = true
		}

		SkillDetailsView {
			visible: window.detailsOpen
			anchors.fill: parent
			skillModel: testSkillModel
			skillController: testSkillController
			ascensionLevel: window.ascensionLevel
			onClosed: window.detailsOpen = false
		}
	}
}
