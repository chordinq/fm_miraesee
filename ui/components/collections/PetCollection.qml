pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import ui 1.0

Item {
	id: root

	property var petCollectionModel: null
	property int columnsPerRow: 5
	property real columnSpacingRatio: 5 / 9
	property real rowSpacingRatio: 5 / 9

	readonly property var petModels: petCollectionModel ? petCollectionModel.pets : []
	readonly property var eggModels: petCollectionModel ? petCollectionModel.eggs : []
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

			width: root.iconSize
			height: root.iconSize

			PetEntry {
				visible: parent.isPet
				petModel: root.petModels[parent.index]
				scale: root.entryScale
				transformOrigin: Item.TopLeft
			}

			EggEntry {
				visible: !parent.isPet
				eggModel: root.eggModels[parent.index - root.petCount]
				scale: root.entryScale
				transformOrigin: Item.TopLeft
			}
		}
	}
}
