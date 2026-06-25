import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "PetCollection test (" + testPetCollection.petCount + " pets, "
		+ testPetCollection.eggCount + " eggs)"
	color: Theme.white

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	PetCollectionView {
		anchors.fill: parent
		petCollectionModel: testPetCollection
	}
}
