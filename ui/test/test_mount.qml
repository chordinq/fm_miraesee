import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "MountSlotGrid test (" + testMountCollection.mountCount + " mounts)"
	color: Theme.white

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	MountSlotGrid {
		anchors.fill: parent
		mountCollectionModel: testMountCollection
	}
}
