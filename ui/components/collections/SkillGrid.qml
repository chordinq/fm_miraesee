pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property var skillCollectionModel: null
	property int columnsPerRow: 5
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 7 / 9

	signal skillClicked(var skillModel)

	readonly property int ascensionLevel: skillCollectionModel ? skillCollectionModel.ascensionLevel : 0
	readonly property var skillModels: skillCollectionModel ? skillCollectionModel.skills : []
	readonly property int skillCount: skillModels.length
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
		id: skillGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.skillCount
		cellWidth: root.cellWidth
		cellHeight: root.iconSize + root.vSpacing
		clip: true

		delegate: Item {
			required property int index
			property var skillModel: root.skillModels[index]

			width: root.iconSize
			height: root.iconSize

			SkillEntryView {
				skillModel: parent.skillModel
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
				onClicked: {
					if (parent.skillModel)
						root.skillClicked(parent.skillModel)
				}
			}
		}
	}
}
