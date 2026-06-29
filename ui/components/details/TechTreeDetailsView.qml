import QtQuick
import ui 1.0

DetailsView {
	id: root

	property var nodeModel: null
	property var techTreeModel: null

	readonly property string otherResearchLocId: "17687817399296000"
	readonly property string maxedLocId: "17688556561489920"
	readonly property string researchInProgressLocId: "17690949319647232"
	readonly property string completeLocId: "27937469076533248"

	readonly property real progressWidthRatio: 0.87
	readonly property real progressWidth: width * progressWidthRatio
	readonly property real progressStatusSpacingRatio: 0.008

	readonly property bool showUpgradeButton: root.nodeModel
		&& !root.nodeModel.maxLevel
		&& !root.nodeModel.isUpgrading
		&& !root.nodeModel.isUpgradeComplete
	readonly property bool showSkipButton: root.nodeModel
		&& root.nodeModel.isUpgrading
		&& !root.nodeModel.isUpgradeComplete
	readonly property bool showProgressUi: root.nodeModel
		&& (root.nodeModel.isUpgrading || root.nodeModel.isUpgradeComplete)

	function nodeFillColor(model) {
		if (!model)
			return Theme.white
		if (model.maxLevel)
			return Theme.lightGreen
		if (model.requirementsMet)
			return Theme.brown
		return Theme.white
	}

	function refreshTreeModel() {
		if (!root.techTreeModel)
			return
		if (root.nodeModel && root.nodeModel.isUpgradeComplete) {
			root.techTreeModel.performUpgradeClaim(root.nodeModel.nodeId)
			return
		}
		root.techTreeModel.refresh()
	}

	TechTreeNodeView {
		parent: root.slotHost
		anchors.left: root.slotHost.left
		anchors.top: root.slotHost.top
		scale: root.slotScale
		transformOrigin: Item.TopLeft
		nodeModel: root.nodeModel
		fillColor: root.nodeFillColor(root.nodeModel)
	}

	Row {
		parent: root.titleRow
		spacing: root.width * root.titleRowSpacingRatio

		AppText {
			locTable: root.nodeModel ? root.nodeModel.nameLocTable : "TechTree"
			locId: root.nodeModel ? root.nodeModel.nameLocId : ""
			fillColor: Theme.white
			pixelSize: root.width * root.titleFontScale
			outlineWeight: 8
		}

		AppText {
			text: root.nodeModel ? root.nodeModel.tierRoman : ""
			fillColor: Theme.white
			pixelSize: root.width * root.titleFontScale
			outlineWeight: 8
		}
	}

	AppText {
		parent: root.bodyColumn
		width: root.bodyColumn.width
		wrapMode: Text.WordWrap
		locTable: root.nodeModel ? root.nodeModel.descLocTable : "TechTree"
		locId: root.nodeModel ? root.nodeModel.descLocId : ""
		formatArgs: root.nodeModel ? root.nodeModel.descFormatArgs : []
		suffix: root.nodeModel
			&& !root.nodeModel.maxLevel
			&& root.nodeModel.perLevelIncreaseText !== ""
			? " " + root.nodeModel.perLevelIncreaseText
			: ""
		suffixFillColor: Theme.greenText
		fillColor: Theme.black
		pixelSize: root.width * root.bodyFontScale
		outlineWeight: 0
	}

	AppText {
		parent: root.statusHost
		width: root.progressWidth
		horizontalAlignment: Text.AlignHCenter
		visible: root.nodeModel && root.nodeModel.maxLevel
		locTable: "TechTree"
		locId: root.maxedLocId
		fillColor: Theme.black
		pixelSize: root.width * root.bodyFontScale
		outlineWeight: 0
	}

	AppText {
		parent: root.statusHost
		width: root.progressWidth
		horizontalAlignment: Text.AlignHCenter
		visible: root.nodeModel
			&& !root.nodeModel.maxLevel
			&& root.nodeModel.otherResearchInProgress
		locTable: "TechTree"
		locId: root.otherResearchLocId
		fillColor: Theme.red
		pixelSize: root.width * root.bodyFontScale
		outlineWeight: 0
	}

	Column {
		parent: root.statusHost
		width: root.progressWidth
		spacing: root.height * root.progressStatusSpacingRatio
		visible: root.showProgressUi

		AppText {
			width: parent.width
			horizontalAlignment: Text.AlignHCenter
			visible: root.nodeModel && root.nodeModel.isUpgrading
			locTable: "TechTree"
			locId: root.researchInProgressLocId
			fillColor: Theme.black
			pixelSize: root.width * root.bodyFontScale
			outlineWeight: 0
		}

		ProgressBar {
			width: root.progressWidth
			timerBridge: root.nodeModel ? root.nodeModel.timerBridge : null
			completeLocId: root.completeLocId
			completeLocTable: "General"
		}
	}

	TechTreeDetailsButton {
		parent: root.actionRow
		width: root.actionButtonWidth
		height: root.actionButtonHeight
		scaleW: root.actionButtonScaleW
		scaleH: root.actionButtonScaleH
		visible: root.showUpgradeButton
		mode: "upgrade"
		topText: root.nodeModel ? root.nodeModel.upgradeDurationText : ""
		bottomText: root.nodeModel ? root.nodeModel.upgradeCostText : ""
		fillColor: root.nodeModel && root.nodeModel.canStartUpgrade
			? Theme.blue
			: Theme.lightGrey
		enabled: root.techTreeModel !== null
			&& root.nodeModel !== null
			&& root.nodeModel.canStartUpgrade
		onClicked: {
			if (root.techTreeModel && root.nodeModel)
				root.techTreeModel.performUpgradeStart(root.nodeModel.nodeId)
		}
	}

	TechTreeDetailsButton {
		parent: root.actionRow
		width: root.actionButtonWidth
		height: root.actionButtonHeight
		scaleW: root.actionButtonScaleW
		scaleH: root.actionButtonScaleH
		visible: root.showSkipButton
		mode: "skip"
		bottomText: root.nodeModel ? root.nodeModel.skipGemCostText : ""
		bottomIconSource: Qt.resolvedUrl("../../../assets/sprites/Currency/GemIcon.png")
		fillColor: root.nodeModel && root.nodeModel.canAffordSkip
			? Theme.blue
			: Theme.lightGrey
		enabled: root.techTreeModel !== null
			&& root.nodeModel !== null
			&& root.nodeModel.canAffordSkip
		onClicked: {
			if (root.techTreeModel && root.nodeModel)
				root.techTreeModel.performGemSkip(root.nodeModel.nodeId)
		}
	}

	Timer {
		interval: 1000
		running: root.visible && root.showProgressUi
		repeat: true
		onTriggered: root.refreshTreeModel()
	}

	onVisibleChanged: {
		if (root.visible)
			root.refreshTreeModel()
	}
}
