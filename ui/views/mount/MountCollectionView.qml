import QtQuick
import ui 1.0

Item {
	id: root

	property var mountCollectionModel: null
	property var mountController: null

	property bool mountDetailsOpen: false
	property var selectedMountModel: null
	property string selectedMountGuid: ""

	MountSlotGrid {
		id: mountGrid

		anchors.fill: parent
		mountCollectionModel: root.mountCollectionModel
		onMountClicked: function(mountModel) {
			root.selectedMountGuid = mountModel.guid
			root.selectedMountModel = mountModel
			root.mountDetailsOpen = true
		}
	}

	function refreshSelectedMount() {
		if (root.selectedMountGuid === "")
			return
		var mounts = root.mountCollectionModel.mounts
		for (var i = 0; i < mounts.length; i++) {
			if (mounts[i].guid === root.selectedMountGuid) {
				root.selectedMountModel = mounts[i]
				return
			}
		}
		root.mountDetailsOpen = false
		root.selectedMountGuid = ""
		root.selectedMountModel = null
	}

	Connections {
		target: root.mountCollectionModel
		function onChanged() {
			root.refreshSelectedMount()
		}
	}

	MountDetailsView {
		id: mountDetails

		z: 10
		visible: root.mountDetailsOpen && root.selectedMountModel !== null
		anchors.centerIn: parent
		mountModel: root.selectedMountModel
		mountController: root.mountController
		ascensionLevel: mountGrid.ascensionLevel
		onClosed: {
			root.mountDetailsOpen = false
			root.selectedMountGuid = ""
			root.selectedMountModel = null
		}
	}
}
