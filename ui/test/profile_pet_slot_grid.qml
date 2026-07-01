import QtQuick
import ui 1.0

Item {
	anchors.fill: parent

	PetSlotGrid {
		anchors.fill: parent
		petCollectionModel: petCollectionModel
	}
}
