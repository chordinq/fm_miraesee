pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property var itemCatalogCollectionModel: null
	property int columnsPerRow: 8
	property int rowCount: 10
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 7 / 9

	readonly property var itemModels: itemCatalogCollectionModel ? itemCatalogCollectionModel.items : []
	readonly property int itemCount: itemCatalogCollectionModel ? itemCatalogCollectionModel.itemCount : 0
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

	GridView {
		id: itemGrid

		anchors.fill: parent
		leftMargin: root.horizontalPadding
		topMargin: root.verticalPadding
		rightMargin: root.horizontalPadding
		bottomMargin: root.verticalPadding

		model: root.itemCount
		cellWidth: root.cellWidth + root.columnSpacing
		cellHeight: root.cellHeight + root.rowSpacing
		cacheBuffer: root.cellHeight * 2
		clip: true

		delegate: Item {
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
