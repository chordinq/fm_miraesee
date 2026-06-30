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
	readonly property var petModels: {
		if (!petCollectionModel || !petCollectionModel.pets)
			return []
		var all = petCollectionModel.pets
		var indexed = []
		for (var i = 0; i < all.length; i++)
			indexed.push({ model: all[i], index: i })
		indexed.sort(function(a, b) {
			if (a.model.isEquipped !== b.model.isEquipped)
				return a.model.isEquipped ? -1 : 1
			if (a.model.rarity !== b.model.rarity)
				return b.model.rarity - a.model.rarity
			return a.index - b.index
		})
		var sorted = []
		for (var j = 0; j < indexed.length; j++)
			sorted.push(indexed[j].model)
		return sorted
	}
	readonly property var eggModels: {
		if (!petCollectionModel || !petCollectionModel.eggs)
			return []
		var all = petCollectionModel.eggs
		var indexed = []
		for (var i = 0; i < all.length; i++) {
			if (!all[i].isEquipped)
				indexed.push({ model: all[i], index: i })
		}
		indexed.sort(function(a, b) {
			if (a.model.rarity !== b.model.rarity)
				return b.model.rarity - a.model.rarity
			return a.index - b.index
		})
		var visible = []
		for (var k = 0; k < indexed.length; k++)
			visible.push(indexed[k].model)
		return visible
	}
	readonly property int petCount: petModels.length
	readonly property int eggCount: eggModels.length
	readonly property int entryCount: petCount + eggCount
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
		id: petGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.entryCount
		cellWidth: root.cellWidth
		cellHeight: root.iconSize + root.vSpacing
		clip: true

		delegate: Item {
			required property int index
			readonly property bool isPet: index < root.petCount
			readonly property var eggModel: isPet ? null : root.eggModels[index - root.petCount]

			width: root.iconSize
			height: root.iconSize

			PetEntryView {
				visible: parent.isPet
				petModel: parent.isPet ? root.petModels[parent.index] : null
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
				onClicked: {
					var model = root.petModels[parent.index]
					if (model)
						root.petClicked(model)
				}
			}

			EggEntryView {
				visible: !parent.isPet
				eggModel: parent.eggModel
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
				onClicked: {
					if (parent.eggModel)
						root.eggClicked(parent.eggModel)
				}
			}
		}
	}
}
