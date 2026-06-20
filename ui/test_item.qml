import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "ItemCatalogCollection test (" + testItemCatalogCollection.itemCount + ")"
	color: Theme.white

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	ItemCatalogCollection {
		anchors.fill: parent
		itemCatalogCollectionModel: testItemCatalogCollection
	}
}
