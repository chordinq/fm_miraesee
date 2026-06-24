pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import ui 1.0

Item {
	id: root

	property var petCollectionModel: null
	property var eggHatchTest: null
	property int columnsPerRow: 5
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 5 / 9

	readonly property int ascensionLevel: petCollectionModel ? petCollectionModel.ascensionLevel : 0
	readonly property var petModels: petCollectionModel ? petCollectionModel.pets : []
	readonly property var eggModels: {
		if (!petCollectionModel || !petCollectionModel.eggs)
			return []
		var all = petCollectionModel.eggs
		var visible = []
		for (var i = 0; i < all.length; i++) {
			if (!all[i].isEquipped)
				visible.push(all[i])
		}
		return visible
	}
	readonly property int petCount: petModels.length
	readonly property int eggCount: eggModels.length
	readonly property int entryCount: petCount + eggCount
	readonly property int iconLogicalSize: 256

	readonly property real totalWidthUnits: columnsPerRow + (columnsPerRow + 1) * columnSpacingRatio
	readonly property real exactIconSize: width > 0 ? (width / totalWidthUnits) : iconLogicalSize
	readonly property real iconSize: Math.floor(exactIconSize)
	readonly property real hSpacing: Math.floor(iconSize * columnSpacingRatio)
	readonly property real vSpacing: Math.floor(iconSize * rowSpacingRatio)
	readonly property real entryScale: iconSize / iconLogicalSize

	GridView {
		id: petGrid

		anchors.fill: parent
		leftMargin: root.hSpacing
		topMargin: root.vSpacing
		model: root.entryCount
		cellWidth: root.iconSize + root.hSpacing
		cellHeight: root.iconSize + root.vSpacing
		clip: true

		ScrollBar.vertical: ScrollBar {
			policy: ScrollBar.AsNeeded
			contentItem: Rectangle {
				implicitWidth: 8
				radius: width / 2
				color: Theme.darkGrey
			}
		}

		delegate: Item {
			required property int index
			readonly property bool isPet: index < root.petCount
			readonly property var eggModel: isPet ? null : root.eggModels[index - root.petCount]

			width: root.iconSize
			height: root.iconSize

			PetSlot {
				visible: parent.isPet
				petModel: root.petModels[parent.index]
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
			}

			EggSlot {
				visible: !parent.isPet
				eggModel: parent.eggModel
				ascensionLevel: root.ascensionLevel
				scale: root.entryScale
				transformOrigin: Item.TopLeft
				onClicked: {
					if (root.eggHatchTest && parent.eggModel)
						root.eggHatchTest.predictHatch(parent.eggModel.guid)
				}
			}
		}
	}
}
