pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property url primaryCurrencyIcon: ""
	property int primaryCurrencyAmount: 0
	property url secondaryCurrencyIcon: ""
	property int secondaryCurrencyAmount: 0
	property var rarityCounts: []
	property string rarityIconType: "skill"
	property int ascensionLevel: 0

	readonly property real currencyIconSize: height * 0.55
	readonly property real currencyLabelScale: 0.35
	readonly property real currencyRowSpacing: height * 0.08
	readonly property real rarityIconSize: height * 0.62
	readonly property real rarityEntryScale: rarityIconSize / 256
	readonly property real rarityRowSpacing: height * 0.06
	readonly property real rarityCountLabelScale: 0.32
	readonly property bool hasSecondaryCurrency: secondaryCurrencyIcon !== ""

	function formatAmount(amount) {
		NumberDisplay.revision
		UiSettings.gameNumberFormattingEnabled
		return NumberDisplay.formatInteger(amount)
	}

	RowLayout {
		anchors.fill: parent
		spacing: root.currencyRowSpacing

		RowLayout {
			spacing: root.currencyRowSpacing

			Image {
				visible: root.primaryCurrencyIcon !== ""
				Layout.preferredWidth: root.currencyIconSize
				Layout.preferredHeight: root.currencyIconSize
				source: root.primaryCurrencyIcon
				fillMode: Image.PreserveAspectFit
				smooth: true
				mipmap: true
			}

			AppText {
				visible: root.primaryCurrencyIcon !== ""
				text: root.formatAmount(root.primaryCurrencyAmount)
				pixelSize: root.height * root.currencyLabelScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}
		}

		RowLayout {
			Layout.fillWidth: true
			Layout.alignment: Qt.AlignHCenter
			spacing: root.rarityRowSpacing

			Repeater {
				model: root.rarityCounts

				delegate: RowLayout {
					required property var modelData
					required property int index

					readonly property int rarity: modelData.rarity
					readonly property int count: modelData.count

					spacing: root.rarityRowSpacing * 0.35

					Item {
						Layout.preferredWidth: root.rarityIconSize
						Layout.preferredHeight: root.rarityIconSize

						SkillIcon {
							anchors.centerIn: parent
							visible: root.rarityIconType === "skill"
							rarity: rarity
							index: 0
							ascensionLevel: root.ascensionLevel
							scale: root.rarityEntryScale
							transformOrigin: Item.Center
						}

						EggIcon {
							anchors.centerIn: parent
							visible: root.rarityIconType === "egg"
							rarity: rarity
							ascensionLevel: root.ascensionLevel
							scale: root.rarityEntryScale
							transformOrigin: Item.Center
						}

						MountIcon {
							anchors.centerIn: parent
							visible: root.rarityIconType === "mount"
							rarity: rarity
							index: 0
							ascensionLevel: root.ascensionLevel
							scale: root.rarityEntryScale
							transformOrigin: Item.Center
						}
					}

					AppText {
						text: root.formatAmount(count)
						pixelSize: root.height * root.rarityCountLabelScale
						fillColor: Theme.white
						outlineColor: Theme.black
						outlineWeight: 8
						Layout.alignment: Qt.AlignVCenter
					}
				}
			}
		}

		RowLayout {
			visible: root.hasSecondaryCurrency
			spacing: root.currencyRowSpacing

			Image {
				Layout.preferredWidth: root.currencyIconSize
				Layout.preferredHeight: root.currencyIconSize
				source: root.secondaryCurrencyIcon
				fillMode: Image.PreserveAspectFit
				smooth: true
				mipmap: true
			}

			AppText {
				text: root.formatAmount(root.secondaryCurrencyAmount)
				pixelSize: root.height * root.currencyLabelScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}
		}
	}
}
