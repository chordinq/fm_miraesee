pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0
import TMPText 1.0

PopupView {
	id: root

	signal languagesClicked()

	parentWidthRatio: 0.34
	widthScale: 50
	heightScale: 50
	contentInsetWOverride: panelWidth / (widthScale * 4 - 6)

	readonly property string settingsTitleLocId: "1830906689011712"
	readonly property string languagesLocId: "25466346099372032"
	readonly property string fullScreenLocId: "1000000000000003"
	readonly property string preciseNumberLocId: "1000000000000001"
	readonly property string allowNegativeCurrencyLocId: "1000000000000002"
	readonly property real titleFontScale: 0.09
	readonly property real titleHeaderHeight: root.panelWidth * (root.titleFontScale * 1.55 + 0.04)
	readonly property real rowFontScale: 0.44
	readonly property real rowHeightRatio: 0.11
	readonly property real toggleHeightRatio: 0.72
	readonly property int settingsRowCount: settingsRows.length
	readonly property real settingsRowHeight: panelWidth * rowHeightRatio

	readonly property string settingsTitleText: TmpTextBridge.localized_text(
		root.settingsTitleLocId,
		UiLocale.selectedCode
	)

	readonly property var settingsRows: [
		{ locId: fullScreenLocId, locTable: "Miraesee", toggleSetting: "fullScreen" },
		{ locId: preciseNumberLocId, locTable: "Miraesee", toggleSetting: "preciseNumber" },
		{ locId: allowNegativeCurrencyLocId, locTable: "Miraesee", toggleSetting: "allowNegativeCurrency" },
		{ locId: languagesLocId, locTable: "General", navigable: true }
	]

	Item {
		id: titleHeader

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		height: root.titleHeaderHeight

		TMPText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.verticalCenter: parent.verticalCenter
			tmpText: root.settingsTitleText
			pixelSize: root.panelWidth * root.titleFontScale
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}
	}

	Flickable {
		id: settingsList

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: titleHeader.bottom
		anchors.bottom: parent.bottom
		clip: true
		contentWidth: width
		contentHeight: settingsGrid.contentHeight
		boundsBehavior: Flickable.StopAtBounds

		GridView {
			id: settingsGrid

			width: settingsList.width
			height: settingsList.contentHeight
			model: root.settingsRows
			cellWidth: width
			cellHeight: root.settingsRowHeight
			interactive: true

			delegate: Item {
				required property var modelData
				required property int index

				width: settingsGrid.cellWidth
				height: settingsGrid.cellHeight

				readonly property bool stripeLight: index % 2 === 0
				readonly property string toggleSetting: modelData.toggleSetting || ""
				readonly property bool hasToggle: toggleSetting !== ""
				readonly property bool toggleChecked:
					toggleSetting === "fullScreen"
						? UiSettings.fullScreenEnabled
						: toggleSetting === "preciseNumber"
							? UiSettings.preciseNumberEnabled
							: toggleSetting === "allowNegativeCurrency"
								? UiSettings.allowNegativeCurrencyEnabled
								: false

				readonly property string rowLabelText: TmpTextBridge.localized_text_table(
					modelData.locId,
					UiLocale.selectedCode,
					modelData.locTable
				)

				Rectangle {
					anchors.fill: parent
					color: stripeLight ? Theme.lightGrey : Theme.white
				}

				TMPText {
					anchors.left: parent.left
					anchors.leftMargin: parent.width * 0.05
					anchors.verticalCenter: parent.verticalCenter
					tmpText: rowLabelText
					pixelSize: parent.height * root.rowFontScale
					fillColor: Theme.black
					outlineWeight: 0
				}

				SettingToggleButton {
					visible: hasToggle
					anchors.right: parent.right
					anchors.rightMargin: parent.width * 0.05
					anchors.verticalCenter: parent.verticalCenter
					height: parent.height * root.toggleHeightRatio
					width: height * layoutAspectRatio
					checked: toggleChecked
					onToggled: function(enabled) {
						if (!hasToggle)
							return
						if (toggleSetting === "fullScreen")
							UiSettings.setFullScreenEnabled(enabled)
						else if (toggleSetting === "preciseNumber")
							UiSettings.setPreciseNumberEnabled(enabled)
						else if (toggleSetting === "allowNegativeCurrency")
							UiSettings.setAllowNegativeCurrencyEnabled(enabled)
					}
				}

				MouseArea {
					anchors.fill: parent
					visible: modelData.navigable === true
					onClicked: root.languagesClicked()
				}
			}
		}
	}
}
