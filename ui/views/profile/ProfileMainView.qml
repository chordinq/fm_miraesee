pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property var profileBridge: null
	property var playerStatsBridge: null

	readonly property real margin: Math.max(12, width * 0.02)
	readonly property real titleFontScale: 0.042
	readonly property real headingFontScale: 0.034
	readonly property real bodyFontScale: 0.028
	readonly property real tableFontScale: 0.026
	readonly property real rowSpacing: Math.max(6, width * 0.01)
	readonly property real sectionSpacing: Math.max(14, width * 0.02)
	readonly property real tableCol1WidthRatio: 0.18
	readonly property real tableCol2WidthRatio: 0.14
	readonly property real tableCol3WidthRatio: 0.34
	readonly property real tableCol4WidthRatio: 0.34

	readonly property string profileTitleText: TmpTextBridge.localized_text_table(
		"25736002664067072",
		UiLocale.selectedCode,
		"General"
	)

	readonly property string powerLabelText: TmpTextBridge.localized_text_table(
		"280343846913",
		UiLocale.selectedCode,
		"TechTree"
	)

	function formatStatLine(modelData) {
		if (!modelData)
			return ""
		if (modelData.text !== undefined)
			return modelData.text
		return ""
	}

	Rectangle {
		anchors.fill: parent
		color: Qt.darker(Theme.darkBlue, 1.5)
	}

	Flickable {
		id: contentFlickable

		anchors.fill: parent
		anchors.margins: root.margin
		contentWidth: width
		contentHeight: contentColumn.implicitHeight
		clip: true
		boundsBehavior: Flickable.StopAtBounds

		Column {
			id: contentColumn

			width: contentFlickable.width
			spacing: root.sectionSpacing

			TMPText {
				width: parent.width
				tmpText: root.profileTitleText
				fillColor: Theme.white
				pixelSize: Math.max(20, root.width * root.titleFontScale)
				outlineColor: Theme.black
				outlineWeight: 6
			}

			TMPText {
				width: parent.width
				visible: root.playerStatsBridge
				tmpText: root.playerStatsBridge
					? (root.powerLabelText + " " + root.playerStatsBridge.powerText)
					: ""
				fillColor: Theme.yellowText
				pixelSize: Math.max(16, root.width * root.headingFontScale)
				outlineColor: Theme.black
				outlineWeight: 5
			}

			TMPText {
				width: parent.width
				tmpText: "Sub-stats (total)"
				fillColor: Theme.white
				pixelSize: Math.max(14, root.width * root.headingFontScale)
				outlineColor: Theme.black
				outlineWeight: 5
			}

			Repeater {
				model: root.profileBridge ? root.profileBridge.subStatRows : []

				TMPText {
					required property var modelData

					width: contentColumn.width
					tmpText: root.formatStatLine(modelData)
					fillColor: Theme.darkGreyText
					pixelSize: Math.max(11, root.width * root.bodyFontScale)
					outlineColor: Theme.black
					outlineWeight: 3
				}
			}

			TMPText {
				width: parent.width
				visible: root.profileBridge && root.profileBridge.subStatRows.length === 0
				tmpText: "No aggregated sub-stats."
				fillColor: Theme.lightGrey
				pixelSize: Math.max(11, root.width * root.bodyFontScale)
				outlineColor: Theme.black
				outlineWeight: 3
			}

			TMPText {
				width: parent.width
				tmpText: "Combat stats (resolved)"
				fillColor: Theme.white
				pixelSize: Math.max(14, root.width * root.headingFontScale)
				outlineColor: Theme.black
				outlineWeight: 5
			}

			Repeater {
				model: root.profileBridge ? root.profileBridge.combatStatRows : []

				TMPText {
					required property var modelData

					width: contentColumn.width
					tmpText: root.formatStatLine(modelData)
					fillColor: Theme.white
					pixelSize: Math.max(11, root.width * root.bodyFontScale)
					outlineColor: Theme.black
					outlineWeight: 3
				}
			}

			TMPText {
				width: parent.width
				tmpText: "Attack speed breakpoints"
				fillColor: Theme.white
				pixelSize: Math.max(14, root.width * root.headingFontScale)
				outlineColor: Theme.black
				outlineWeight: 5
			}

			TMPText {
				width: parent.width
				visible: root.profileBridge && root.profileBridge.ready
				tmpText: root.profileBridge
					? (root.profileBridge.weaponTitle + "\n" + root.profileBridge.weaponSubtitle)
					: ""
				fillColor: Theme.lightGrey
				pixelSize: Math.max(11, root.width * root.bodyFontScale)
				outlineColor: Theme.black
				outlineWeight: 3
				lineSpacing: root.rowSpacing * 0.5
			}

			TMPText {
				width: parent.width
				visible: root.profileBridge && root.profileBridge.ready
				tmpText: root.profileBridge
					? ("Current: +" + root.profileBridge.attackSpeedBonusPct.toFixed(2) + "% · "
						+ root.profileBridge.currentAps.toFixed(3) + " APS · "
						+ "Base " + root.profileBridge.currentCycleSeconds.toFixed(2) + "s · "
						+ "Double " + root.profileBridge.currentDoubleCycleSeconds.toFixed(2) + "s")
					: ""
				fillColor: Theme.skillColor
				pixelSize: Math.max(12, root.width * root.bodyFontScale)
				outlineColor: Theme.black
				outlineWeight: 4
			}

			RectRoundButton {
				id: computeBreakpointsBtn

				width: Math.min(contentColumn.width, Math.max(220, contentColumn.width * 0.55))
				height: width * (1.75 / 3.5)
				aspectW: 3.5
				aspectH: 1.75
				visible: root.profileBridge && root.profileBridge.ready
				labelText: root.profileBridge && root.profileBridge.breakpointsComputing
					? "Calculating..."
					: (root.profileBridge && root.profileBridge.breakpointsReady
						? "Recalculate breakpoints"
						: "Calculate breakpoints")
				buttonEnabled: root.profileBridge
					&& root.profileBridge.ready
					&& !root.profileBridge.breakpointsComputing
				fillColor: Theme.blue
				labelScale: 0.28
				onClicked: {
					if (!root.profileBridge)
						return
					UiLoading.defer(function() {
						root.profileBridge.computeBreakpoints()
					})
				}
			}

			TMPText {
				width: parent.width
				visible: root.profileBridge
					&& root.profileBridge.ready
					&& !root.profileBridge.breakpointsReady
					&& !root.profileBridge.breakpointsComputing
				tmpText: "Press the button to compute attack speed breakpoints."
				fillColor: Theme.lightGrey
				pixelSize: Math.max(11, root.width * root.bodyFontScale)
				outlineColor: Theme.black
				outlineWeight: 3
			}

			Item {
				width: parent.width
				height: breakpointHeader.implicitHeight
				visible: root.profileBridge && root.profileBridge.breakpointsReady

				TMPText {
					id: breakpointHeader

					width: parent.width * root.tableCol1WidthRatio
					tmpText: "AS%"
					fillColor: Theme.lightGrey
					pixelSize: Math.max(10, root.width * root.tableFontScale)
					outlineColor: Theme.black
					outlineWeight: 3
				}

				TMPText {
					x: parent.width * root.tableCol1WidthRatio
					width: parent.width * root.tableCol2WidthRatio
					tmpText: "APS"
					fillColor: Theme.lightGrey
					pixelSize: Math.max(10, root.width * root.tableFontScale)
					outlineColor: Theme.black
					outlineWeight: 3
				}

				TMPText {
					x: parent.width * (root.tableCol1WidthRatio + root.tableCol2WidthRatio)
					width: parent.width * root.tableCol3WidthRatio
					tmpText: "Base Attack Cycle"
					fillColor: Theme.lightGrey
					pixelSize: Math.max(10, root.width * root.tableFontScale)
					outlineColor: Theme.black
					outlineWeight: 3
				}

				TMPText {
					x: parent.width * (root.tableCol1WidthRatio + root.tableCol2WidthRatio + root.tableCol3WidthRatio)
					width: parent.width * root.tableCol4WidthRatio
					tmpText: "Double Attack Cycle"
					fillColor: Theme.lightGrey
					pixelSize: Math.max(10, root.width * root.tableFontScale)
					outlineColor: Theme.black
					outlineWeight: 3
				}
			}

			Repeater {
				model: root.profileBridge && root.profileBridge.breakpointsReady
					? root.profileBridge.breakpointRows
					: []

				Item {
					required property var modelData
					required property int index

					width: contentColumn.width
					height: Math.max(rowMinPct.implicitHeight, rowAps.implicitHeight, rowCycle.implicitHeight) + root.rowSpacing * 0.25

					Rectangle {
						anchors.fill: parent
						visible: modelData && modelData.isCurrent
						color: Theme.checkBoxActiveGrey
						opacity: 0.55
						radius: 4
					}

					TMPText {
						id: rowMinPct

						width: parent.width * root.tableCol1WidthRatio
						tmpText: modelData
							? ("+" + modelData.minBonusPct.toFixed(2) + "%")
							: ""
						fillColor: modelData && modelData.isCurrent ? Theme.skillColor : Theme.white
						pixelSize: Math.max(10, root.width * root.tableFontScale)
						outlineColor: Theme.black
						outlineWeight: modelData && modelData.isCurrent ? 4 : 3
					}

					TMPText {
						id: rowAps

						x: parent.width * root.tableCol1WidthRatio
						width: parent.width * root.tableCol2WidthRatio
						tmpText: modelData
							? modelData.aps.toFixed(3)
							: ""
						fillColor: modelData && modelData.isCurrent ? Theme.skillColor : Theme.white
						pixelSize: Math.max(10, root.width * root.tableFontScale)
						outlineColor: Theme.black
						outlineWeight: modelData && modelData.isCurrent ? 4 : 3
					}

					TMPText {
						id: rowCycle

						x: parent.width * (root.tableCol1WidthRatio + root.tableCol2WidthRatio)
						width: parent.width * root.tableCol3WidthRatio
						tmpText: modelData
							? (modelData.cycleSeconds.toFixed(2) + "s")
							: ""
						fillColor: modelData && modelData.isCurrent ? Theme.skillColor : Theme.white
						pixelSize: Math.max(10, root.width * root.tableFontScale)
						outlineColor: Theme.black
						outlineWeight: modelData && modelData.isCurrent ? 4 : 3
					}

					TMPText {
						x: parent.width * (root.tableCol1WidthRatio + root.tableCol2WidthRatio + root.tableCol3WidthRatio)
						width: parent.width * root.tableCol4WidthRatio
						tmpText: modelData
							? (modelData.doubleCycleSeconds.toFixed(2) + "s")
							: ""
						fillColor: modelData && modelData.isCurrent ? Theme.skillColor : Theme.white
						pixelSize: Math.max(10, root.width * root.tableFontScale)
						outlineColor: Theme.black
						outlineWeight: modelData && modelData.isCurrent ? 4 : 3
					}
				}
			}
		}
	}
}
