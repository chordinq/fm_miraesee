import QtQuick
import ui 1.0

Item {
	id: root

	property var techTreeForgeModel: null
	property var techTreePowerModel: null
	property var techTreeSkillsPetTechModel: null

	property string selectedTreeType: ""

	property bool detailsOpen: false
	property var selectedNodeModel: null

	property real columnSpacingRatio: 0.15
	property real rowSpacingRatio: 0.15

	readonly property bool showingTree: selectedTreeType !== ""
	readonly property real typeCardWidth: width > 0
		? Math.floor(width / (2 + 3 * columnSpacingRatio))
		: 0
	readonly property real columnSpacing: typeCardWidth * columnSpacingRatio
	readonly property real rowSpacing: typeCardWidth * rowSpacingRatio
	readonly property real gridInnerWidth: width - 2 * columnSpacing
	readonly property real backButtonSize: width * 0.08

	function techTreeModelForType(treeType) {
		switch (treeType) {
		case "power":
			return root.techTreePowerModel
		case "skillsPetTech":
			return root.techTreeSkillsPetTechModel
		default:
			return root.techTreeForgeModel
		}
	}

	function techTreeForType(treeType) {
		switch (treeType) {
		case "power":
			return powerTechTree
		case "skillsPetTech":
			return skillsPetTechTree
		default:
			return forgeTechTree
		}
	}

	function openTree(treeType) {
		root.selectedTreeType = treeType
		Qt.callLater(function() {
			var tree = root.techTreeForType(treeType)
			if (tree)
				tree.scheduleAutoScroll()
		})
	}

	function closeTree() {
		if (root.selectedTreeType !== "") {
			var tree = root.techTreeForType(root.selectedTreeType)
			if (tree)
				tree.resetScroll()
		}
		root.selectedTreeType = ""
		root.detailsOpen = false
		root.selectedNodeModel = null
	}

	Item {
		anchors.fill: parent
		visible: !root.showingTree

		Grid {
			id: typeGrid

			x: root.columnSpacing
			y: root.rowSpacing
			width: root.gridInnerWidth
			columns: 2
			columnSpacing: root.columnSpacing
			rowSpacing: root.rowSpacing

		TechTreeCategoryView {
			width: root.typeCardWidth
			treeType: "forge"
			progress: root.techTreeForgeModel
				? root.techTreeForgeModel.progress
				: 0
			progressLevelSum: root.techTreeForgeModel
				? root.techTreeForgeModel.progressLevelSum
				: 0
			progressMaxSum: root.techTreeForgeModel
				? root.techTreeForgeModel.progressMaxSum
				: 0
			researchActive: root.techTreeForgeModel
				? root.techTreeForgeModel.categoryResearchActive
				: false
			researchComplete: root.techTreeForgeModel
				? root.techTreeForgeModel.categoryResearchComplete
				: false
			researchRemainingText: root.techTreeForgeModel
				? root.techTreeForgeModel.categoryResearchRemainingText
				: ""
			onClicked: root.openTree("forge")
		}

		TechTreeCategoryView {
			width: root.typeCardWidth
			treeType: "power"
			progress: root.techTreePowerModel
				? root.techTreePowerModel.progress
				: 0
			progressLevelSum: root.techTreePowerModel
				? root.techTreePowerModel.progressLevelSum
				: 0
			progressMaxSum: root.techTreePowerModel
				? root.techTreePowerModel.progressMaxSum
				: 0
			researchActive: root.techTreePowerModel
				? root.techTreePowerModel.categoryResearchActive
				: false
			researchComplete: root.techTreePowerModel
				? root.techTreePowerModel.categoryResearchComplete
				: false
			researchRemainingText: root.techTreePowerModel
				? root.techTreePowerModel.categoryResearchRemainingText
				: ""
			onClicked: root.openTree("power")
		}

		TechTreeCategoryView {
			width: root.typeCardWidth
			treeType: "skillsPetTech"
			progress: root.techTreeSkillsPetTechModel
				? root.techTreeSkillsPetTechModel.progress
				: 0
			progressLevelSum: root.techTreeSkillsPetTechModel
				? root.techTreeSkillsPetTechModel.progressLevelSum
				: 0
			progressMaxSum: root.techTreeSkillsPetTechModel
				? root.techTreeSkillsPetTechModel.progressMaxSum
				: 0
			researchActive: root.techTreeSkillsPetTechModel
				? root.techTreeSkillsPetTechModel.categoryResearchActive
				: false
			researchComplete: root.techTreeSkillsPetTechModel
				? root.techTreeSkillsPetTechModel.categoryResearchComplete
				: false
			researchRemainingText: root.techTreeSkillsPetTechModel
				? root.techTreeSkillsPetTechModel.categoryResearchRemainingText
				: ""
			onClicked: root.openTree("skillsPetTech")
		}
		}
	}

	Item {
		anchors.fill: parent
		visible: root.showingTree

		TechTree {
			id: forgeTechTree

			anchors.fill: parent
			visible: root.selectedTreeType === "forge"
			techTreeModel: root.techTreeForgeModel
			onNodeClicked: function(nodeModel) {
				root.selectedNodeModel = nodeModel
				root.detailsOpen = true
			}
		}

		TechTree {
			id: powerTechTree

			anchors.fill: parent
			visible: root.selectedTreeType === "power"
			techTreeModel: root.techTreePowerModel
			onNodeClicked: function(nodeModel) {
				root.selectedNodeModel = nodeModel
				root.detailsOpen = true
			}
		}

		TechTree {
			id: skillsPetTechTree

			anchors.fill: parent
			visible: root.selectedTreeType === "skillsPetTech"
			techTreeModel: root.techTreeSkillsPetTechModel
			onNodeClicked: function(nodeModel) {
				root.selectedNodeModel = nodeModel
				root.detailsOpen = true
			}
		}

		ReturnButton {
			id: returnButton

			anchors.left: parent.left
			anchors.bottom: parent.bottom
			anchors.margins: root.columnSpacing
			height: root.backButtonSize
			width: returnButton.height * returnButton.widthHeightRatio
			onClicked: root.closeTree()
		}
	}

	TechTreeDetailsView {
		z: 10
		visible: root.detailsOpen && root.selectedNodeModel !== null
		anchors.fill: parent
		nodeModel: root.selectedNodeModel
		techTreeModel: root.techTreeModelForType(root.selectedTreeType)
		onClosed: {
			root.detailsOpen = false
			root.selectedNodeModel = null
		}
	}

	Connections {
		target: root.techTreeModelForType(root.selectedTreeType)
		enabled: root.showingTree && root.selectedNodeModel !== null
		function onChanged() {
			var model = root.techTreeModelForType(root.selectedTreeType)
			if (!model || !root.selectedNodeModel)
				return
			var refreshed = model.nodeById(root.selectedNodeModel.nodeId)
			if (refreshed)
				root.selectedNodeModel = refreshed
		}
	}

	Timer {
		interval: 1000
		running: root.visible && !root.showingTree
		repeat: true
		onTriggered: {
			if (root.techTreeForgeModel)
				root.techTreeForgeModel.tick()
			if (root.techTreePowerModel)
				root.techTreePowerModel.tick()
			if (root.techTreeSkillsPetTechModel)
				root.techTreeSkillsPetTechModel.tick()
		}
	}

	Timer {
		interval: 1000
		running: root.visible && root.showingTree
		repeat: true
		onTriggered: {
			var model = root.techTreeModelForType(root.selectedTreeType)
			if (model)
				model.tick()
		}
	}
}
