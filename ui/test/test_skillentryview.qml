pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import ui 1.0
import TMPText 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "SkillEntryView ascension preview"
	color: Theme.white

	readonly property int iconLogicalSize: 256
	readonly property real entrySize: Math.min(width * 0.16, height * 0.55, 220)
	readonly property real entryScale: entrySize / iconLogicalSize
	readonly property real cellWidth: entrySize * 1.35
	readonly property real columnSpacing: Math.max(40, width * 0.05)

	Component.onCompleted: {
		UiLocale.setSelectedLocale(uiLanguage)
	}

	Column {
		anchors.centerIn: parent
		spacing: Math.max(24, height * 0.06)

		TMPText {
			anchors.horizontalCenter: parent.horizontalCenter
			tmpText: testSkillModel ? testSkillModel.skillKey + "  L" + (testSkillModel.level + 1) : ""
			pixelSize: Math.max(18, width * 0.028)
			fillColor: Theme.black
			outlineWeight: 0
		}

		Row {
			anchors.horizontalCenter: parent.horizontalCenter
			spacing: window.columnSpacing

			Repeater {
				model: testAscensionLevels

				Item {
					required property int modelData

					width: window.cellWidth
					height: window.entrySize

					SkillEntryView {
						x: (parent.width - window.iconLogicalSize * window.entryScale) / 2
						skillModel: testSkillModel
						ascensionLevel: parent.modelData
						scale: window.entryScale
						transformOrigin: Item.TopLeft
					}
				}
			}
		}
	}
}
