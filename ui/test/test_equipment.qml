import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "EquipmentCollection test (" + testEquipmentCollection.equippedCount + "/" + testEquipmentCollection.slotCount + ")"
	color: Theme.white

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	EquipmentCollection {
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		width: Math.min(parent.width * 0.9, parent.height * 0.9)
		equipmentCollectionModel: testEquipmentCollection
	}
}
