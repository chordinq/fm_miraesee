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
	title: "TechTreeDetailsView preview"
	color: Theme.white

	property bool detailsOpen: true
	property int selectedNodeId: testDefaultNodeId

	readonly property real collectionWidthRatio: 5 / 16
	readonly property var selectedNodeModel: testTechTreeModel
		? testTechTreeModel.nodeById(window.selectedNodeId)
		: null

	Component.onCompleted: {
		UiLocale.setSelectedLocale(uiLanguage)
	}

	Column {
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		anchors.margins: Math.max(16, width * 0.02)
		spacing: Math.max(10, height * 0.012)

		TMPText {
			width: parent.width
			tmpText: window.selectedNodeModel
				? window.selectedNodeModel.nameText + "  L"
					+ (window.selectedNodeModel.level + 1)
				: "No node selected"
			pixelSize: Math.max(16, window.width * 0.022)
			fillColor: Theme.black
			outlineWeight: 0
		}

		ScrollView {
			width: parent.width
			height: Math.min(parent.height, Math.max(72, window.height * 0.18))
			clip: true
			ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

			Flow {
				width: parent.width
				spacing: Math.max(8, window.width * 0.01)

				Repeater {
					model: testNodeOptions

					Rectangle {
						required property var modelData
						required property int index

						width: Math.max(120, nodeLabel.implicitWidth + window.width * 0.04)
						height: Math.max(34, window.height * 0.045)
						radius: height * 0.2
						color: window.selectedNodeId === modelData.nodeId
							? Theme.blue
							: Theme.lightGrey

						TMPText {
							id: nodeLabel

							anchors.centerIn: parent
							tmpText: parent.modelData.label
							pixelSize: parent.height * 0.34
							fillColor: Theme.white
							outlineWeight: 0
						}

						MouseArea {
							anchors.fill: parent
							onClicked: window.selectedNodeId = parent.modelData.nodeId
						}
					}
				}
			}
		}
	}

	Rectangle {
		id: collectionPanel

		width: parent.width * window.collectionWidthRatio
		height: parent.height * 0.72
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: parent.bottom
		anchors.bottomMargin: Math.max(16, height * 0.03)
		color: Theme.commonGrey

		TMPText {
			anchors.centerIn: parent
			visible: !window.detailsOpen
			tmpText: "Closed — click to reopen"
			pixelSize: Math.max(14, parent.width * 0.04)
			fillColor: Theme.darkGreyText
			outlineWeight: 0
		}

		MouseArea {
			anchors.fill: parent
			visible: !window.detailsOpen
			onClicked: window.detailsOpen = true
		}

		TechTreeDetailsView {
			visible: window.detailsOpen && window.selectedNodeModel !== null
			anchors.fill: parent
			nodeModel: window.selectedNodeModel
			techTreeModel: testTechTreeModel
			onClosed: window.detailsOpen = false
		}
	}

	Connections {
		target: testTechTreeModel
		function onChanged() {
			if (!testTechTreeModel || window.selectedNodeId < 0)
				return
			var refreshed = testTechTreeModel.nodeById(window.selectedNodeId)
			if (!refreshed && testNodeOptions.length > 0)
				window.selectedNodeId = testNodeOptions[0].nodeId
		}
	}
}
