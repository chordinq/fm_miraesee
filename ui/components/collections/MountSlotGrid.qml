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
	readonly property int iconLogicalSize: 256
	readonly property int entryCount: mountCollectionModel ? mountCollectionModel.entryCount : 0
	readonly property int rowCount: entryCount > 0 ? Math.ceil(entryCount / columnsPerRow) : 0
	readonly property real cellHeight: iconSize + vSpacing
	readonly property real estimatedContentHeight: rowCount * cellHeight

	property bool preserveScrollPosition: false
	property real preservedContentY: 0

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
		if (root.mountCollectionModel && root.mountCollectionModel.gridWarmupSuppressed)
			return
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

	function restorePreservedScrollPosition() {
		if (!root.preserveScrollPosition)
			return
		var targetY = Math.max(0, Math.min(
			root.preservedContentY,
			mountGrid.contentHeight - mountGrid.height
		))
		mountGrid.contentY = targetY
		root.preserveScrollPosition = false
	}

	onEntryCountChanged: syncFullCacheBuffer()

	GridView {
		id: mountGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.mountCollectionModel ? root.mountCollectionModel.entryModel : null
		cellWidth: root.cellWidth
		cellHeight: root.cellHeight
		clip: true
		reuseItems: false
		cacheBuffer: Math.max(root.cellHeight * 2, root.estimatedContentHeight)

		onContentHeightChanged: root.syncFullCacheBuffer()

		delegate: Item {
			id: entryDelegate

			required property int index
			required property var bridge

			width: root.iconSize
			height: root.iconSize

			MountEntryView {
				mountModel: entryDelegate.bridge
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
				onClicked: {
					if (entryDelegate.bridge)
						root.mountClicked(entryDelegate.bridge)
				}
			}
		}
	}

	Connections {
		target: root.mountCollectionModel
		function onGridReloaded() {
			Qt.callLater(function() {
				root.syncFullCacheBuffer()
				root.warmDelegateCache()
				root.restorePreservedScrollPosition()
			})
		}
		function onEntryLayoutChanged() {
			root.syncFullCacheBuffer()
			Qt.callLater(root.restorePreservedScrollPosition)
		}
		function onGridWarmupSuppressedChanged() {
			if (root.mountCollectionModel && !root.mountCollectionModel.gridWarmupSuppressed)
				Qt.callLater(root.warmDelegateCache)
		}
	}
}
