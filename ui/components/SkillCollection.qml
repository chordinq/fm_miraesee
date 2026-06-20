pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property var skillCollectionModel: null
	property int columnsPerRow: 5
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 7 / 9

	readonly property var skillModels: skillCollectionModel ? skillCollectionModel.skills : []
	readonly property int iconLogicalSize: 256
	readonly property int skillCount: skillModels.length
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
		id: skillGrid

		anchors.fill: parent
		leftMargin: root.horizontalPadding
		topMargin: root.verticalPadding
		rightMargin: root.horizontalPadding
		bottomMargin: root.verticalPadding

		model: root.skillCount
		cellWidth: root.cellWidth + root.columnSpacing
		cellHeight: root.cellHeight + root.rowSpacing
		cacheBuffer: root.cellHeight * 2
		clip: true

		delegate: Item {
			required property int index
			property var skillModel: root.skillModels[index]

			width: root.cellWidth
			height: root.cellHeight

			SkillEntry {
				skillModel: parent.skillModel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
			}
		}
	}
}
