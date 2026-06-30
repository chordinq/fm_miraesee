import QtQuick
import ui 1.0

DetailsView {
	id: root

	property var nodeModel: null
	property var techTreeModel: null

	readonly property real iconSizeRatio: 0.138
	readonly property real iconSize: layoutUnit * iconSizeRatio
	readonly property real iconScale: iconSize / 256
	readonly property real iconLeftMarginRatio: 0.04
	readonly property real iconTopMarginRatio: 0.054
	readonly property real iconOverlayOffsetRatio: 0.17
	readonly property real iconOverlayFontScale: 17 / 64

	readonly property real titleLeftMarginRatio: 0.27
	readonly property real titleTopMarginRatio: 0.026
	readonly property real titleRightMarginRatio: 0.05
	readonly property real titleFontScale: 0.0449
	readonly property real titleSegmentSpacingRatio: 0.012

	readonly property real descLeftMarginRatio: 0.27
	readonly property real descTopMarginRatio: 0.1
	readonly property real descRightMarginRatio: 0.05
	readonly property real bodyFontScale: 0.045

	readonly property string otherResearchLocId: "17687817399296000"
	readonly property string maxedLocId: "17688556561489920"
	readonly property string researchInProgressLocId: "17690949319647232"
	readonly property string completeLocId: "27937469076533248"

	readonly property real progressWidthRatio: 0.87
	readonly property real progressWidth: layoutUnit * progressWidthRatio
	readonly property real progressStatusSpacingRatio: 0.008
	readonly property real statusBottomMarginRatio: 0.02

	readonly property string iconProgressText: {
		if (!root.nodeModel || root.nodeModel.levelMax <= 0)
			return ""
		if (root.nodeModel.maxLevel)
			return root.nodeModel.level + "/" + root.nodeModel.levelMax
		var iconLevel = root.nodeModel.iconLevel
		if (iconLevel === -2 || iconLevel === -1)
			return "0/" + root.nodeModel.levelMax
		return root.nodeModel.level + "/" + root.nodeModel.levelMax
	}

	readonly property bool showClaimButton: root.nodeModel
		&& root.nodeModel.isUpgradeComplete
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
		if (!root.techTreeModel || !root.nodeModel)
			return
		root.nodeModel.timerBridge.refresh()
	}

	readonly property string actionMode: {
		if (!root.nodeModel)
			return ""
		if (root.showClaimButton)
			return "claim"
		if (root.showSkipButton)
			return "skip"
		if (root.showUpgradeButton)
			return "upgrade"
		return ""
	}

	readonly property bool actionEnabled:
		!root.techTreeModel || !root.nodeModel
			? false
			: root.actionMode === "claim"
				? true
				: root.actionMode === "skip"
					? root.nodeModel.canAffordSkip
					: root.actionMode === "upgrade"
						? root.nodeModel.canStartUpgrade
						: false

	readonly property color actionFillColor:
		root.actionEnabled ? Theme.blue : Theme.lightGrey

	Item {
		anchors.fill: parent

		Item {
			id: iconSlot

			width: root.iconSize
			height: root.iconSize
			anchors.left: parent.left
			anchors.top: parent.top
			anchors.leftMargin: root.layoutUnit * root.iconLeftMarginRatio
			anchors.topMargin: root.layoutUnit * root.iconTopMarginRatio

			Item {
				readonly property int logicalSize: 256

				width: logicalSize
				height: logicalSize
				scale: root.iconScale
				transformOrigin: Item.TopLeft

				TechTreeIcon {
					id: techTreeIcon

					anchors.fill: parent
					nodeType: root.nodeModel ? root.nodeModel.nodeType : -1
					fillColor: root.nodeFillColor(root.nodeModel)
				}

				AppText {
					anchors.horizontalCenter: techTreeIcon.horizontalCenter
					anchors.verticalCenter: techTreeIcon.bottom
					anchors.verticalCenterOffset: techTreeIcon.height * root.iconOverlayOffsetRatio
					text: root.iconProgressText
					visible: root.iconProgressText !== ""
						&& techTreeIcon.nodeType >= 0
					pixelSize: techTreeIcon.height * root.iconOverlayFontScale
					fillColor: Theme.white
					outlineWeight: 8
				}
			}
		}

		Item {
			id: titleSlot

			anchors.left: parent.left
			anchors.leftMargin: root.layoutUnit * root.titleLeftMarginRatio
			anchors.top: parent.top
			anchors.topMargin: root.layoutUnit * root.titleTopMarginRatio
			anchors.right: parent.right
			anchors.rightMargin: root.layoutUnit * root.titleRightMarginRatio
			height: titleRow.height

			Row {
				id: titleRow

				spacing: root.layoutUnit * root.titleSegmentSpacingRatio

				AppText {
					locTable: root.nodeModel ? root.nodeModel.nameLocTable : "TechTree"
					locId: root.nodeModel ? root.nodeModel.nameLocId : ""
					fillColor: Theme.white
					pixelSize: root.layoutUnit * root.titleFontScale
					outlineWeight: 8
				}

				AppText {
					text: root.nodeModel ? root.nodeModel.tierRoman : ""
					fillColor: Theme.white
					pixelSize: root.layoutUnit * root.titleFontScale
					outlineWeight: 8
				}
			}
		}

		Item {
			id: descSlot

			anchors.left: parent.left
			anchors.leftMargin: root.layoutUnit * root.descLeftMarginRatio
			anchors.top: parent.top
			anchors.topMargin: root.layoutUnit * root.descTopMarginRatio
			anchors.right: parent.right
			anchors.rightMargin: root.layoutUnit * root.descRightMarginRatio
			height: descText.height

			AppText {
				id: descText

				width: parent.width
				wordWrap: true
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
				pixelSize: root.layoutUnit * root.bodyFontScale
				outlineWeight: 0
			}
		}

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: statusColumn.visible ? statusColumn.top : actionButton.top
			anchors.bottomMargin: root.layoutUnit * root.statusBottomMarginRatio
			width: root.progressWidth
			horizontalAlignment: Text.AlignHCenter
			visible: root.nodeModel && root.nodeModel.maxLevel
			locTable: "TechTree"
			locId: root.maxedLocId
			fillColor: Theme.black
			pixelSize: root.layoutUnit * root.bodyFontScale
			outlineWeight: 0
		}

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: statusColumn.visible ? statusColumn.top : actionButton.top
			anchors.bottomMargin: root.layoutUnit * root.statusBottomMarginRatio
			width: root.progressWidth
			horizontalAlignment: Text.AlignHCenter
			visible: root.nodeModel
				&& !root.nodeModel.maxLevel
				&& root.nodeModel.otherResearchInProgress
			locTable: "TechTree"
			locId: root.otherResearchLocId
			fillColor: Theme.red
			pixelSize: root.layoutUnit * root.bodyFontScale
			outlineWeight: 0
		}

		Column {
			id: statusColumn

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: actionButton.top
			anchors.bottomMargin: root.layoutUnit * root.statusBottomMarginRatio
			width: root.progressWidth
			spacing: root.layoutUnit * root.progressStatusSpacingRatio
			visible: root.showProgressUi

			AppText {
				width: parent.width
				horizontalAlignment: Text.AlignHCenter
				visible: root.nodeModel && root.nodeModel.isUpgrading
				locTable: "TechTree"
				locId: root.researchInProgressLocId
				fillColor: Theme.black
				pixelSize: root.layoutUnit * root.bodyFontScale
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
			id: actionButton

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			anchors.bottomMargin: root.layoutUnit * root.actionBottomMarginRatio
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			visible: root.actionMode !== ""
			mode: root.actionMode
			topText: root.actionMode === "upgrade" && root.nodeModel
				? root.nodeModel.upgradeDurationText
				: ""
			bottomText: root.nodeModel
				? (root.actionMode === "skip"
					? root.nodeModel.skipGemCostText
					: root.actionMode === "upgrade"
						? root.nodeModel.upgradeCostText
						: "")
				: ""
			bottomIconSource: root.actionMode === "skip"
				? Qt.resolvedUrl("../../../assets/sprites/Currency/GemIcon.png")
				: Qt.resolvedUrl("../../../assets/sprites/Currency/techPotions.png")
			claimLocId: root.completeLocId
			claimLocTable: "General"
			fillColor: root.actionFillColor
			enabled: root.techTreeModel !== null
				&& root.nodeModel !== null
				&& root.actionEnabled
			onClicked: {
				if (!root.techTreeModel || !root.nodeModel)
					return
				if (root.actionMode === "upgrade")
					root.techTreeModel.performUpgradeStart(root.nodeModel.nodeId)
				else if (root.actionMode === "skip")
					root.techTreeModel.performGemSkip(root.nodeModel.nodeId)
				else if (root.actionMode === "claim") {
					root.techTreeModel.performUpgradeClaim(root.nodeModel.nodeId)
					root.closed()
				}
			}
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
