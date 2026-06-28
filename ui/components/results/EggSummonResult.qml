pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Rectangle {
	id: root

	property var results: []
	property int ascensionLevel: 0
	property int columnsPerRow: 5
	property real columnSpacingRatio: 0.55
	property real rowSpacingRatio: 0.6

	color: Theme.checkBoxActiveGrey
	readonly property int resultCount: results ? results.length : 0
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
		id: resultGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.resultCount
		cellWidth: root.cellWidth
		cellHeight: root.iconSize + root.vSpacing
		clip: true

		delegate: Item {
			required property int index
			readonly property var entry: root.results[index]

			width: root.iconSize
			height: root.iconSize

			EggIcon {
				anchors.centerIn: parent
				rarity: parent.entry ? parent.entry.rarity : -1
				ascensionLevel: parent.entry && parent.entry.ascensionLevel !== undefined
					? parent.entry.ascensionLevel
					: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.Center
			}
		}
	}
}
