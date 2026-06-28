pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property int activeTabIndex: 0

	signal tabClicked(int index)
	signal settingsClicked()
	signal loadDumpClicked()

	readonly property real edgeMargin: Math.max(4, root.width * 0.06)

	readonly property var tabs: [
		{ locId: "12856879411200", locTable: "Forge", color: Theme.darkGrey },
		{ locId: "2109395617640448", locTable: "Stats", color: Theme.lightGreen },
		{ locId: "2110564712771584", locTable: "Stats", color: Theme.lightBlue },
		{ locId: "990866679984128", locTable: "Stats", color: Theme.orange },
		{ locId: "280318681088", locTable: "TechTree", color: Theme.red }
	]

	Rectangle {
		anchors.fill: parent
		color: Theme.darkGrey
	}

	Column {
		id: sideTabColumn

		anchors.top: parent.top
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.margins: root.edgeMargin
		height: parent.height * 0.3

		Repeater {
			model: root.tabs

			delegate: CollectionTabButton {
				required property var modelData
				required property int index

				width: sideTabColumn.width
				height: sideTabColumn.height / root.tabs.length

				locId: modelData.locId
				locTable: modelData.locTable
				activeColor: modelData.color
				active: root.activeTabIndex === index
				onClicked: root.tabClicked(index)
			}
		}
	}

	Row {
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: parent.bottom
		anchors.bottomMargin: root.edgeMargin
		spacing: root.edgeMargin * 0.35

		LoadDumpButton {
			width: root.width * 0.34
			height: width
			onClicked: root.loadDumpClicked()
		}

		SettingsButton {
			width: root.width * 0.34
			height: width
			onClicked: root.settingsClicked()
		}
	}
}
