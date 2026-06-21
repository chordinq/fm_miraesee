pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Rectangle {
	id: root

	property var petCollectionModel: null
	property real slotSpacingRatio: 0.2

	readonly property int ascensionLevel: petCollectionModel ? petCollectionModel.ascensionLevel : 0
	readonly property int slotCount: petCollectionModel ? petCollectionModel.hatchSlotCount : 0
	readonly property var eggModels: petCollectionModel ? petCollectionModel.hatchEggModels : []

	implicitWidth: 1200
	height: width * (5 / 12)

	readonly property real logicalSlotSize: 256
	readonly property real totalWidthUnits: slotCount > 0 ? slotCount + (slotCount - 1) * slotSpacingRatio : 1
	readonly property real exactSlotSize: Math.min(width / totalWidthUnits, height * 0.25)
	readonly property real slotSize: Math.floor(exactSlotSize)
	readonly property real slotSpacing: Math.floor(slotSize * slotSpacingRatio)
	readonly property real slotScale: logicalSlotSize > 0 ? slotSize / logicalSlotSize : 1

	color: Qt.lighter(Theme.darkBlue, 2.22)

	Column {
		anchors.fill: parent

		Rectangle { width: parent.width; height: root.height * 0.01; color: Theme.black }
		Rectangle { width: parent.width; height: root.height * 0.03; color: Qt.darker(Theme.darkBlue, 2) }
		Rectangle { width: parent.width; height: root.height * 0.01; color: Theme.black }
		Rectangle { width: parent.width; height: root.height * 0.02; color: Theme.darkBlue }
		Rectangle { width: parent.width; height: root.height * 0.01; color: Theme.black }

		Rectangle {
			width: parent.width
			height: root.height * 0.88
			color: "transparent"

			Row {
				anchors.centerIn: parent
				spacing: root.slotSpacing

				Repeater {
					model: root.slotCount

					Item {
						required property int index

						width: root.slotSize
						height: root.slotSize

						EggHatchSlot {
							eggModel: root.eggModels[parent.index]
							ascensionLevel: root.ascensionLevel
							scale: root.slotScale
							transformOrigin: Item.TopLeft
						}
					}
				}
			}
		}

		Rectangle { width: parent.width; height: root.height * 0.02; color: Theme.darkBlue }
		Rectangle { width: parent.width; height: root.height * 0.02; color: Theme.black }
	}
}
