pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property var mountCollectionModel: null
	property int columnsPerRow: 5
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 5 / 9

	signal mountClicked(var mountModel)

	readonly property int ascensionLevel: mountCollectionModel ? mountCollectionModel.ascensionLevel : 0
	readonly property var mountModels: mountCollectionModel ? mountCollectionModel.displayMounts : []
	readonly property int mountCount: mountModels.length
	readonly property int iconLogicalSize: 256
	readonly property int rowCount: mountCount > 0 ? Math.ceil(mountCount / columnsPerRow) : 0
	readonly property real cellHeight: iconSize + vSpacing
	readonly property real estimatedContentHeight: rowCount * cellHeight

	readonly property real totalWidthUnits: columnsPerRow + (columnsPerRow + 1) * columnSpacingRatio
	readonly property real exactIconSize: width > 0 ? (width / totalWidthUnits) : iconLogicalSize
	readonly property real hSpacing: exactIconSize * columnSpacingRatio
	readonly property real cellWidth: width > 0
		? (width - hSpacing) / columnsPerRow
		: exactIconSize + exactIconSize * columnSpacingRatio
	readonly property real iconSize: cellWidth / (1 + columnSpacingRatio)
	readonly property real vSpacing: iconSize * rowSpacingRatio
	readonly property real entryScale: iconSize / iconLogicalSize

	function syncFullCacheBuffer() {
		var target = root.estimatedContentHeight
		if (mountGrid.contentHeight > 0)
			target = Math.max(target, mountGrid.contentHeight)
		if (target > 0)
			mountGrid.cacheBuffer = target
	}

	function warmDelegateCache() {
		syncFullCacheBuffer()
		if (mountGrid.count <= 0 || mountGrid.contentHeight <= mountGrid.height)
			return
		var savedY = mountGrid.contentY
		var maxY = Math.max(0, mountGrid.contentHeight - mountGrid.height)
		if (maxY <= 0)
			return
		mountGrid.contentY = maxY
		Qt.callLater(function() {
			mountGrid.contentY = savedY
		})
	}

	onMountCountChanged: {
		syncFullCacheBuffer()
		if (mountCount > 0)
			Qt.callLater(root.warmDelegateCache)
	}

	GridView {
		id: mountGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.mountCount
		cellWidth: root.cellWidth
		cellHeight: root.cellHeight
		clip: true
		reuseItems: false
		cacheBuffer: Math.max(root.cellHeight * 2, root.estimatedContentHeight)

		onContentHeightChanged: root.syncFullCacheBuffer()

		delegate: Item {
			required property int index
			property var mountModel: root.mountModels[index]

			width: root.iconSize
			height: root.iconSize

			MountEntryView {
				mountModel: parent.mountModel
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
				onClicked: {
					if (parent.mountModel)
						root.mountClicked(parent.mountModel)
				}
			}
		}
	}
}
