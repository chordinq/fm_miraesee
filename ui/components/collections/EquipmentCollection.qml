pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property var equipmentCollectionModel: null
	property int columnsPerRow: 4
	property int rowCount: 2
	property real columnSpacingRatio: 5 / 32
	property real rowSpacingRatio: 5 / 32

	readonly property var itemModels: equipmentCollectionModel ? equipmentCollectionModel.items : []
	readonly property int slotCount: equipmentCollectionModel ? equipmentCollectionModel.slotCount : 0
	readonly property int iconLogicalSize: 256

	readonly property real totalWidthUnits: columnsPerRow + (columnsPerRow + 1) * columnSpacingRatio
	readonly property real exactIconSize: width > 0 ? (width / totalWidthUnits) : iconLogicalSize
	readonly property real iconSize: Math.floor(exactIconSize)
	readonly property real hSpacing: Math.floor(iconSize * columnSpacingRatio)
	readonly property real vSpacing: Math.floor(iconSize * rowSpacingRatio)
	readonly property real entryScale: iconSize / iconLogicalSize

	implicitHeight: (iconSize * rowCount) + (vSpacing * (rowCount + 1))

	Grid {
		id: equipmentGrid

		x: root.hSpacing
		y: root.vSpacing
		columns: root.columnsPerRow
		columnSpacing: root.hSpacing
		rowSpacing: root.vSpacing

		Repeater {
			model: root.slotCount

			Item {
				required property int index
				property var itemModel: root.itemModels[index]

				width: root.iconSize
				height: root.iconSize

				ItemSlot {
					itemModel: parent.itemModel
					scale: root.entryScale
					transformOrigin: Item.TopLeft
				}
			}
		}
	}
}
