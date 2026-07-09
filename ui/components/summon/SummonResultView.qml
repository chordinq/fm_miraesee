pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	clip: true

	property var summonController: null
	property real cornerRatio: 255 / (512 * 50)
	property real panelCornerRadius: -1

	readonly property var result: root.summonController
		? root.summonController.summonResult
		: ({})
	readonly property bool hasData: result && result.hasData
	readonly property int paidCount: hasData ? result.paidCount : 0
	readonly property int totalPulls: hasData ? result.totalPulls : 0
	readonly property int bonusRolls: hasData ? result.bonusRolls : 0
	readonly property var rarityRows: hasData && result.rarityRows ? result.rarityRows : []

	readonly property real cornerRadiusPx: panelCornerRadius >= 0
		? panelCornerRadius
		: Math.min(width, height) * cornerRatio
	readonly property real panelCornerRatioW: width > 0 ? cornerRadiusPx / width : cornerRatio
	readonly property real panelCornerRatioH: height > 0 ? cornerRadiusPx / height : cornerRatio

	readonly property string locTable: "Miraesee"
	readonly property string bonusLocId: "1000000000000006"
	readonly property string totalLocId: "1000000000000007"

	readonly property real padH: Math.max(8, width * 0.06)
	readonly property real padV: Math.max(5, height * 0.06)
	readonly property real secGap: Math.max(4, height * 0.04)
	readonly property real labelPx: Math.max(10, height * 0.07)
	readonly property real valuePx: Math.max(12, height * 0.095)
	readonly property real rarityPx: Math.max(10, height * 0.065)

	function localizedLabel(locId: string, table: string): string {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text_table(
			locId,
			UiLocale.selectedCode,
			table
		)
	}

	RectRounded {
		anchors.fill: parent
		cornerRatioW: root.panelCornerRatioW
		cornerRatioH: root.panelCornerRatioH
		fillColor: Theme.checkBoxActiveGrey
	}

	TMPText {
		id: titleText

		anchors.top: parent.top
		anchors.topMargin: root.padV
		anchors.horizontalCenter: parent.horizontalCenter
		tmpText: "RESULT"
		pixelSize: root.labelPx * 1.05
		fillColor: Theme.white
		outlineWeight: 0
		horizontalAlignment: Text.AlignHCenter
	}

	Rectangle {
		id: div1

		anchors.top: titleText.bottom
		anchors.topMargin: root.secGap * 0.5
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		height: 1
		color: Theme.white
		opacity: 0.15
	}

	Item {
		id: statsRow

		anchors.top: div1.bottom
		anchors.topMargin: root.secGap
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		height: root.valuePx * 2.2

		Item {
			id: paidCol

			anchors.left: parent.left
			anchors.top: parent.top
			anchors.bottom: parent.bottom
			width: parent.width / 3

			TMPText {
				id: paidLabel

				anchors.horizontalCenter: parent.horizontalCenter
				anchors.top: parent.top
				tmpText: "Paid"
				pixelSize: root.labelPx * 0.85
				fillColor: Theme.white
				opacity: 0.75
				outlineWeight: 0
				horizontalAlignment: Text.AlignHCenter
			}

			TMPText {
				anchors.horizontalCenter: parent.horizontalCenter
				anchors.top: paidLabel.bottom
				anchors.topMargin: root.secGap * 0.2
				tmpText: root.hasData ? ("x" + root.paidCount) : "—"
				pixelSize: root.valuePx
				fillColor: Theme.white
				outlineWeight: 0
				horizontalAlignment: Text.AlignHCenter
			}
		}

		Item {
			id: totalCol

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.top: parent.top
			anchors.bottom: parent.bottom
			width: parent.width / 3

			TMPText {
				id: totalLabel

				anchors.horizontalCenter: parent.horizontalCenter
				anchors.top: parent.top
				tmpText: root.localizedLabel(root.totalLocId, root.locTable)
				pixelSize: root.labelPx * 0.85
				fillColor: Theme.white
				opacity: 0.75
				outlineWeight: 0
				horizontalAlignment: Text.AlignHCenter
			}

			TMPText {
				anchors.horizontalCenter: parent.horizontalCenter
				anchors.top: totalLabel.bottom
				anchors.topMargin: root.secGap * 0.2
				tmpText: root.hasData ? root.totalPulls.toString() : "—"
				pixelSize: root.valuePx
				fillColor: Theme.white
				outlineWeight: 0
				horizontalAlignment: Text.AlignHCenter
			}
		}

		Item {
			id: bonusCol

			anchors.right: parent.right
			anchors.top: parent.top
			anchors.bottom: parent.bottom
			width: parent.width / 3

			TMPText {
				id: bonusLabel

				anchors.horizontalCenter: parent.horizontalCenter
				anchors.top: parent.top
				tmpText: root.localizedLabel(root.bonusLocId, root.locTable)
				pixelSize: root.labelPx * 0.85
				fillColor: Theme.white
				opacity: 0.75
				outlineWeight: 0
				horizontalAlignment: Text.AlignHCenter
			}

			TMPText {
				anchors.horizontalCenter: parent.horizontalCenter
				anchors.top: bonusLabel.bottom
				anchors.topMargin: root.secGap * 0.2
				tmpText: root.hasData ? ("+" + root.bonusRolls) : "—"
				pixelSize: root.valuePx
				fillColor: root.bonusRolls > 0 ? Theme.lightGreen : Theme.darkGrey
				outlineWeight: 0
				horizontalAlignment: Text.AlignHCenter
			}
		}
	}

	Rectangle {
		id: div2

		anchors.top: statsRow.bottom
		anchors.topMargin: root.secGap * 0.6
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		height: 1
		color: Theme.white
		opacity: 0.15
	}

	Flickable {
		id: rarityFlickable

		anchors.top: div2.bottom
		anchors.topMargin: root.secGap * 0.4
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		anchors.bottom: parent.bottom
		anchors.bottomMargin: root.padV
		clip: true
		contentHeight: rarityList.contentHeight
		boundsBehavior: Flickable.StopAtBounds

		ListView {
			id: rarityList

			width: parent.width
			height: contentHeight
			interactive: false
			spacing: root.secGap * 0.35
			model: root.rarityRows.length

			delegate: Item {
				required property int index

				readonly property var row: root.rarityRows[index]
				readonly property int rowRarity: row ? row.rarity : -1
				readonly property int rowCount: row ? row.count : 0
				readonly property color rowColor: rowRarity >= 0 && rowRarity < Theme.rarityColors.length
					? Theme.rarityColors[rowRarity]
					: Theme.white

				width: rarityList.width
				height: root.rarityPx * 1.35

				TMPText {
					anchors.left: parent.left
					anchors.verticalCenter: parent.verticalCenter
					width: parent.width * 0.72
					tmpText: row
						? root.localizedLabel(row.rarityLocId, row.rarityLocTable)
						: ""
					pixelSize: root.rarityPx
					fillColor: rowColor
					outlineWeight: 0
				}

				TMPText {
					anchors.right: parent.right
					anchors.verticalCenter: parent.verticalCenter
					tmpText: "x" + rowCount
					pixelSize: root.rarityPx
					fillColor: rowColor
					outlineWeight: 0
				}
			}
		}
	}
}
