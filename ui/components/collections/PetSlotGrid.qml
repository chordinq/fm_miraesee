pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property var petCollectionModel: null
	property int columnsPerRow: 5
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 5 / 9

	signal petClicked(var petModel)
	signal eggClicked(var eggModel)

	readonly property int ascensionLevel: petCollectionModel ? petCollectionModel.ascensionLevel : 0
	readonly property int iconLogicalSize: 256
	readonly property int entryCount: petCollectionModel ? petCollectionModel.entryCount : 0
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
		if (petGrid.contentHeight > 0)
			target = Math.max(target, petGrid.contentHeight)
		if (target > 0)
			petGrid.cacheBuffer = target
	}

	function warmDelegateCache() {
		syncFullCacheBuffer()
		if (petGrid.count <= 0 || petGrid.contentHeight <= petGrid.height)
			return
		var savedY = petGrid.contentY
		var maxY = Math.max(0, petGrid.contentHeight - petGrid.height)
		if (maxY <= 0)
			return
		petGrid.contentY = maxY
		Qt.callLater(function() {
			petGrid.contentY = savedY
		})
	}

	function restorePreservedScrollPosition() {
		if (!root.preserveScrollPosition)
			return
		var targetY = Math.max(0, Math.min(
			root.preservedContentY,
			petGrid.contentHeight - petGrid.height
		))
		petGrid.contentY = targetY
		root.preserveScrollPosition = false
	}

	onEntryCountChanged: syncFullCacheBuffer()

	GridView {
		id: petGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.petCollectionModel ? root.petCollectionModel.entryModel : null
		cellWidth: root.cellWidth
		cellHeight: root.cellHeight
		clip: true
		reuseItems: false
		cacheBuffer: Math.max(root.cellHeight * 2, root.estimatedContentHeight)

		onContentHeightChanged: root.syncFullCacheBuffer()

		delegate: Item {
			id: entryDelegate

			required property int index
			required property bool isPet
			required property var bridge

			width: root.iconSize
			height: root.iconSize

			PetEntryView {
				visible: entryDelegate.isPet
				petModel: entryDelegate.isPet ? entryDelegate.bridge : null
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
				onClicked: {
					if (entryDelegate.isPet && entryDelegate.bridge)
						root.petClicked(entryDelegate.bridge)
				}
			}

			EggEntryView {
				visible: !entryDelegate.isPet
				eggModel: entryDelegate.isPet ? null : entryDelegate.bridge
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
				onClicked: {
					if (!entryDelegate.isPet && entryDelegate.bridge)
						root.eggClicked(entryDelegate.bridge)
				}
			}
		}
	}

	Connections {
		target: root.petCollectionModel
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
		function onInventoryEggsChanged() {
			root.preservedContentY = petGrid.contentY
			root.preserveScrollPosition = true
		}
		function onPetsChanged() {
			root.preservedContentY = petGrid.contentY
			root.preserveScrollPosition = true
		}
	}
}
