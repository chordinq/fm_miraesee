pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	clip: true

	property var preview: []
	property int ascensionLevel: 0
	property int columnsPerRow: 5
	property real columnSpacingRatio: 0.55
	property real rowSpacingRatio: 0.6
	property real cornerRatio: 255 / (512 * 50)
	property real panelCornerRadius: -1

	readonly property real cornerRadiusPx: panelCornerRadius >= 0
		? panelCornerRadius
		: Math.min(width, height) * cornerRatio
	readonly property real panelCornerRatioW: width > 0 ? cornerRadiusPx / width : cornerRatio
	readonly property real panelCornerRatioH: height > 0 ? cornerRadiusPx / height : cornerRatio
	readonly property int previewCount: preview ? preview.length : 0
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

	RectRounded {
		anchors.fill: parent
		cornerRatioW: root.panelCornerRatioW
		cornerRatioH: root.panelCornerRatioH
		fillColor: Theme.checkBoxActiveGrey
	}

	GridView {
		id: previewGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.previewCount
		cellWidth: root.cellWidth
		cellHeight: root.iconSize + root.vSpacing
		clip: true

		delegate: Item {
			required property int index
			readonly property var entry: root.preview[index]

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
