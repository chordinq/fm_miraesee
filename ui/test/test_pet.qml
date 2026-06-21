import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "PetSlotGrid test"
	color: Theme.white

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	PetSlotGrid {
		anchors.fill: parent
		petCollectionModel: testPetCollection
	}
}
