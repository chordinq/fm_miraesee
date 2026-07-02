import QtQuick
import QtQuick.Layouts
import ui 1.0
import TMPText 1.0

RectRoundButton {
	id: root

	scaleW: SummonButtonMetrics.scaleW
	scaleH: SummonButtonMetrics.scaleH
	fillColor: Theme.blue
	handleInput: true

	property string titleLocId: ""
	property string titleLocTable: "General"
	property string titleText: ""
	property string titleSuffix: ""
	property url titleIconSource
	property int titleIconSpriteIndex: -1
	property string costText: ""
	property url currencyIconSource

	property real titleFontScale: 11 / 32
	property real costFontScale: 11 / 32
	readonly property real titleWidthRatio: 0.88
	readonly property real rowIconScale: 0.35
	property real titleRowVerticalCenterOffsetRatio: -0.18
	property real costRowVerticalCenterOffsetRatio: 0.15
	readonly property real canvasHeight: root.bakedHeight
	readonly property bool showTitleIcon:
		root.titleIconSpriteIndex >= 0 || root.titleIconSource != ""
	readonly property bool showCurrencyIcon: root.currencyIconSource != ""
	readonly property bool showTitleRow:
		root.showTitleIcon
		|| root.titleLocId !== ""
		|| root.titleText !== ""
		|| root.titleSuffix !== ""
	readonly property bool showCostRow:
		root.showCurrencyIcon || root.costText !== ""

	readonly property string resolvedTitleLocText: {
		UiLocale.selectedCode
		if (root.titleLocId === "")
			return ""
		return TmpTextBridge.localized_text_table(
			root.titleLocId,
			UiLocale.selectedCode,
			root.titleLocTable
		)
	}

	Item {
		id: titleHost

		parent: root.contentHost
		visible: root.showTitleRow
		width: parent.width * root.titleWidthRatio
		height: titleRow.implicitHeight
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.height * root.titleRowVerticalCenterOffsetRatio

		RowLayout {
			id: titleRow

			anchors.centerIn: parent
			spacing: root.canvasHeight * 0.04
			scale: Math.min(1, titleHost.width / Math.max(titleRow.implicitWidth, 1))
			transformOrigin: Item.Center

			Item {
				visible: root.showTitleIcon
				width: root.showTitleIcon ? root.canvasHeight * root.rowIconScale : 0
				height: width
				Layout.alignment: Qt.AlignVCenter

				SpriteSheet {
					anchors.fill: parent
					visible: root.titleIconSpriteIndex >= 0
					source: root.titleIconSource
					spriteIndex: root.titleIconSpriteIndex
				}

				Image {
					anchors.fill: parent
					visible: root.titleIconSpriteIndex < 0
					source: root.titleIconSource
					fillMode: Image.PreserveAspectFit
					smooth: true
					mipmap: true
				}
			}

			TMPText {
				visible: root.titleLocId !== ""
				tmpText: root.resolvedTitleLocText
				pixelSize: root.canvasHeight * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}

			TMPText {
				visible: root.titleText !== ""
				tmpText: root.titleText
				pixelSize: root.canvasHeight * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}

			TMPText {
				visible: root.titleSuffix !== ""
				tmpText: root.titleSuffix
				pixelSize: root.canvasHeight * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignBaseline
			}
		}
	}

	RowLayout {
		parent: root.contentHost
		visible: root.showCostRow
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.height * root.costRowVerticalCenterOffsetRatio
		spacing: 0

		Item {
			visible: root.showCurrencyIcon
			width: root.showCurrencyIcon ? root.canvasHeight * root.rowIconScale : 0
			height: width
			Layout.alignment: Qt.AlignVCenter

			Image {
				anchors.fill: parent
				source: root.currencyIconSource
				fillMode: Image.PreserveAspectFit
				smooth: true
				mipmap: true
			}
		}

		TMPText {
			visible: root.costText !== ""
			tmpText: root.costText
			pixelSize: root.canvasHeight * root.costFontScale
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
			Layout.alignment: Qt.AlignVCenter
		}
	}
}
