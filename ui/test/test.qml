import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui 1.0
import TMPText 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "TMPText / core.format preview"
	color: "#1a1a2e"

	readonly property real margin: Math.max(20, width * 0.04)
	readonly property real sectionGap: Math.max(28, height * 0.035)
	readonly property real rowGap: Math.max(10, height * 0.014)
	readonly property real labelSize: Math.max(14, width * 0.028)
	readonly property real bodySize: Math.max(22, width * 0.042)
	readonly property real iconSize: Math.round(bodySize * 1.15)

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	ScrollView {
		anchors.fill: parent
		anchors.margins: window.margin
		clip: true
		ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

		ColumnLayout {
			width: Math.max(1, window.width - window.margin * 2)
			spacing: window.sectionGap

			AppText {
				Layout.fillWidth: true
				text: "TMPText + core/format"
				pixelSize: Math.max(20, window.width * 0.045)
				fillColor: Theme.white
				outlineWeight: 0
				horizontalAlignment: Text.AlignHCenter
			}

			TMPText {
				Layout.alignment: Qt.AlignHCenter
				tmpText: "HELLO — plain text"
				pixelSize: Math.max(28, window.bodySize * 1.1)
				fillColor: "#ff6666"
			}

			ColumnLayout {
				Layout.fillWidth: true
				spacing: window.rowGap

				AppText {
					text: "FormatLevelPlusOne (outlineWeight: 8)"
					pixelSize: window.labelSize
					fillColor: Theme.darkGreyText
					outlineWeight: 0
				}

				TMPText {
					Layout.alignment: Qt.AlignHCenter
					tmpText: sampleLevelPlusOne
					pixelSize: window.bodySize
					outlineWeight: 8
				}

				TMPText {
					Layout.alignment: Qt.AlignHCenter
					tmpText: sampleLevelFull
					pixelSize: window.bodySize * 0.85
					fillColor: Theme.white
				}
			}

			ColumnLayout {
				Layout.fillWidth: true
				spacing: window.rowGap

				AppText {
					text: "Numbers.Format / FormatLong"
					pixelSize: window.labelSize
					fillColor: Theme.darkGreyText
					outlineWeight: 0
				}

				TMPText {
					tmpText: sampleLongA
					pixelSize: window.bodySize
				}

				TMPText {
					tmpText: sampleLongB
					pixelSize: window.bodySize
				}

				TMPText {
					tmpText: sampleLongC
					pixelSize: window.bodySize
				}
			}

			ColumnLayout {
				Layout.fillWidth: true
				spacing: window.rowGap

				AppText {
					text: "FormatStat / FormatPercentage"
					pixelSize: window.labelSize
					fillColor: Theme.darkGreyText
					outlineWeight: 0
				}

				TMPText {
					tmpText: sampleStat
					pixelSize: window.bodySize
				}

				TMPText {
					tmpText: samplePct
					pixelSize: window.bodySize
				}
			}

			ColumnLayout {
				Layout.fillWidth: true
				spacing: window.rowGap

				AppText {
					text: "FormatCurrency + inline icon"
					pixelSize: window.labelSize
					fillColor: Theme.darkGreyText
					outlineWeight: 0
				}

				Repeater {
					model: currencySamples

					delegate: Item {
						Layout.fillWidth: true
						implicitHeight: currencyRow.implicitHeight

						RowLayout {
							id: currencyRow

							anchors.left: parent.left
							width: parent.width
							spacing: 12

							AppText {
								Layout.preferredWidth: window.width * 0.28
								text: modelData.label
								pixelSize: window.labelSize
								fillColor: Theme.darkGreyText
								outlineWeight: 0
							}

							TMPText {
								tmpText: modelData.text
								iconSource: modelData.iconSource
								iconPixelSize: window.iconSize
								pixelSize: window.bodySize
							}
						}
					}
				}
			}

			ColumnLayout {
				Layout.fillWidth: true
				spacing: window.rowGap

				AppText {
					text: "FormatPower"
					pixelSize: window.labelSize
					fillColor: Theme.darkGreyText
					outlineWeight: 0
				}

				TMPText {
					tmpText: samplePowerText
					iconSource: samplePowerIcon
					iconPixelSize: window.iconSize
					pixelSize: window.bodySize
				}
			}
		}
	}
}
