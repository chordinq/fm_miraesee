import QtQuick
import ui 1.0

PopupView {
	id: root

	parentWidthRatio: 0.25
	widthScale: 40
	heightScale: 60
	closeButtonSizeRatio: 0.2
	readonly property string titleLocId: "30155911439511552"
	readonly property real titleFontScale: 0.085
	readonly property real rowHeightRatio: 0.138
	readonly property real rowSpacingRatio: 0
	readonly property real checkSizeRatio: 0.75
	readonly property real labelFontScale: 0.5

	readonly property var languages: LocManager.languages

	AppText {
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0
		locId: root.titleLocId
		locTable: "General"
		pixelSize: parent.width * root.titleFontScale
		fillColor: Theme.white
		outlineWeight: 8
	}

	Flickable {
		id: languageList

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0.105
		anchors.bottom: parent.bottom
		anchors.bottomMargin: parent.height * 0.05
		anchors.leftMargin: parent.width * 0.065
		anchors.rightMargin: parent.width * 0.05
		clip: true
		contentHeight: languageColumn.height

		Column {
			id: languageColumn

			width: languageList.width
			spacing: languageList.width * root.rowSpacingRatio

			Repeater {
				model: root.languages

				delegate: Item {
					required property var modelData

					width: languageColumn.width
					height: languageColumn.width * root.rowHeightRatio

					readonly property bool selected: Theme.language === modelData.code

					Row {
						anchors.verticalCenter: parent.verticalCenter
						spacing: parent.width * 0.07

						CheckBoxGrey {
							width: parent.parent.height * root.checkSizeRatio
							height: width
							checked: selected
							onClicked: Theme.language = modelData.code
						}

						AppText {
							text: modelData.label
							pixelSize: parent.parent.height * root.labelFontScale
							fillColor: Theme.black
							outlineWeight: 0
						}
					}
				}
			}
		}
	}
}
