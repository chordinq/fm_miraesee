import QtQuick
import QtQuick.Layouts
import ui 1.0

RectRoundButton {
	id: root

	scaleW: 4
	scaleH: 2
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

	readonly property real titleFontScale: 10 / 32
	readonly property real costFontScale: 11 / 32
	readonly property real titleWidthRatio: 0.88
	readonly property real rowIconScale: 25 / 64
	readonly property bool showTitleIcon: root.titleIconSource != ""
	readonly property bool showTitleRow:
		root.showTitleIcon
		|| root.titleLocId !== ""
		|| root.titleText !== ""
		|| root.titleSuffix !== ""
	readonly property bool showCostRow:
		root.currencyIconSource != "" || root.costText !== ""

	Item {
		id: titleHost

		visible: root.showTitleRow
		width: parent.width * root.titleWidthRatio
		height: titleRow.implicitHeight
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: -parent.height * 0.18

		RowLayout {
			id: titleRow

			anchors.centerIn: parent
			spacing: titleHost.parent.height * 0.04
			scale: Math.min(1, titleHost.width / Math.max(titleRow.implicitWidth, 1))
			transformOrigin: Item.Center

			Item {
				visible: root.showTitleIcon
				width: titleHost.parent.height * root.rowIconScale
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
				}
			}

			AppText {
				visible: root.titleLocId !== ""
				locId: root.titleLocId
				locTable: root.titleLocTable
				pixelSize: titleHost.parent.height * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}

			AppText {
				visible: root.titleText !== ""
				text: root.titleText
				pixelSize: titleHost.parent.height * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}

			AppText {
				visible: root.titleSuffix !== ""
				text: root.titleSuffix
				pixelSize: titleHost.parent.height * root.titleFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignBaseline
			}
		}
	}

	RowLayout {
		visible: root.showCostRow
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.height * 0.14
		spacing: parent.height * 0.04

		Item {
			visible: root.currencyIconSource != ""
			width: parent.parent.height * root.rowIconScale
			height: width
			Layout.alignment: Qt.AlignVCenter

			Image {
				anchors.fill: parent
				source: root.currencyIconSource
				fillMode: Image.PreserveAspectFit
				smooth: true
			}
		}

		AppText {
			visible: root.costText !== ""
			text: root.costText
			pixelSize: parent.parent.height * root.costFontScale
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
			Layout.alignment: Qt.AlignVCenter
		}
	}
}
