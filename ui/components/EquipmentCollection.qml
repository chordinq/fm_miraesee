pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property var equipmentCollectionModel: null
	property int columnsPerRow: 4
	property int rowCount: 2
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 7 / 9

	readonly property var itemModels: equipmentCollectionModel ? equipmentCollectionModel.items : []
	readonly property int slotCount: equipmentCollectionModel ? equipmentCollectionModel.slotCount : 0
	readonly property int iconLogicalSize: 256
	readonly property real gridDenom: columnsPerRow + (columnsPerRow - 1) * columnSpacingRatio
	readonly property real iconSize: {
		if (width <= 0)
			return iconLogicalSize
		var denom = gridDenom + 2 * columnSpacingRatio
		return Math.max(48, Math.floor(width / denom))
	}
	readonly property real horizontalPadding: iconSize * columnSpacingRatio
	readonly property real verticalPadding: iconSize * rowSpacingRatio
	readonly property real columnSpacing: iconSize * columnSpacingRatio
	readonly property real rowSpacing: iconSize * rowSpacingRatio
	readonly property real entryScale: iconSize / iconLogicalSize
	readonly property real cellWidth: iconSize
	readonly property real cellHeight: iconSize
	readonly property real gridWidth: (columnsPerRow * cellWidth) + ((columnsPerRow - 1) * columnSpacing)

	implicitWidth: width
	implicitHeight: (2 * verticalPadding) + (rowCount * cellHeight) + ((rowCount - 1) * rowSpacing)

	Grid {
		id: equipmentGrid

		x: root.horizontalPadding
		y: root.verticalPadding
		width: root.gridWidth
		columns: root.columnsPerRow
		rowSpacing: root.rowSpacing
		columnSpacing: root.columnSpacing

		Repeater {
			model: root.slotCount

			Item {
				required property int index
				property var itemModel: root.itemModels[index]

				width: root.cellWidth
				height: root.cellHeight

				ItemEntry {
					itemModel: parent.itemModel
					scale: root.entryScale
					transformOrigin: Item.TopLeft
				}
			}
		}
	}
}
