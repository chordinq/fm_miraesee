pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import ui 1.0

Item {
	id: root

	property var mountCollectionModel: null
	property int columnsPerRow: 5
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 5 / 9

	readonly property int ascensionLevel: mountCollectionModel ? mountCollectionModel.ascensionLevel : 0
	readonly property var mountModels: mountCollectionModel ? mountCollectionModel.mounts : []
	readonly property int mountCount: mountModels.length
	readonly property int iconLogicalSize: 256

	readonly property real totalWidthUnits: columnsPerRow + (columnsPerRow + 1) * columnSpacingRatio
	readonly property real exactIconSize: width > 0 ? (width / totalWidthUnits) : iconLogicalSize
	readonly property real hSpacing: exactIconSize * columnSpacingRatio
	readonly property real cellWidth: width > 0
		? (width - hSpacing) / columnsPerRow
		: exactIconSize + exactIconSize * columnSpacingRatio
	readonly property real iconSize: cellWidth / (1 + columnSpacingRatio)
	readonly property real vSpacing: iconSize * rowSpacingRatio
	readonly property real entryScale: iconSize / iconLogicalSize

	GridView {
		id: mountGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.mountCount
		cellWidth: root.cellWidth
		cellHeight: root.iconSize + root.vSpacing
		clip: true

		ScrollBar.vertical: ScrollBar {
			policy: ScrollBar.AsNeeded
			contentItem: Rectangle {
				implicitWidth: 8
				radius: width / 2
				color: Theme.darkGrey
			}
		}

		delegate: Item {
			required property int index
			property var mountModel: root.mountModels[index]

			width: root.iconSize
			height: root.iconSize

			MountSlot {
				mountModel: parent.mountModel
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
			}
		}
	}
}
