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
	readonly property string emptySlotSheetSource: equipmentCollectionModel
		? equipmentCollectionModel.emptySlotSheetUrl
		: ""
	readonly property int iconLogicalSize: 256

	readonly property real totalWidthUnits: columnsPerRow + (columnsPerRow + 1) * columnSpacingRatio
	readonly property real exactIconSize: width > 0 ? (width / totalWidthUnits) : iconLogicalSize
	readonly property real iconSize: exactIconSize
	readonly property real hSpacing: exactIconSize * columnSpacingRatio
	readonly property real vSpacing: exactIconSize * rowSpacingRatio
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
				property var itemModel: {
					if (!root.equipmentCollectionModel)
						return null
					var models = root.itemModels
					if (!models || index < 0 || index >= models.length)
						return null
					var model = models[index]
					return model === undefined ? null : model
				}

				width: root.iconSize
				height: root.iconSize

				ItemInventorySlotView {
					itemModel: parent.itemModel
					itemType: root.equipmentCollectionModel
						? root.equipmentCollectionModel.slotItemType(index)
						: -1
					emptySheetSource: root.emptySlotSheetSource
					scale: root.entryScale
					transformOrigin: Item.TopLeft
				}
			}
		}
	}
}
