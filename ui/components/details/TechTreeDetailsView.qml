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

	readonly property bool actionEnabled:
		!root.techTreeModel || !root.nodeModel
			? false
			: root.showClaimButton
				? true
				: root.showSkipButton
					? root.nodeModel.canAffordSkip
					: root.showUpgradeButton
						? root.nodeModel.canStartUpgrade
						: false

	readonly property color actionFillColor:
		root.actionEnabled ? Theme.blue : Theme.lightGrey

	function performAction() {
		if (!root.techTreeModel || !root.nodeModel)
			return
		if (root.showUpgradeButton)
			root.techTreeModel.performUpgradeStart(root.nodeModel.nodeId)
		else if (root.showSkipButton)
			root.techTreeModel.performGemSkip(root.nodeModel.nodeId)
		else if (root.showClaimButton) {
			root.techTreeModel.performUpgradeClaim(root.nodeModel.nodeId)
			root.closed()
		}
	}

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
			anchors.bottom: statusColumn.visible ? statusColumn.top : actionSlot.top
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
			anchors.bottom: statusColumn.visible ? statusColumn.top : actionSlot.top
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
			anchors.bottom: actionSlot.top
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

		Item {
			id: actionSlot

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			anchors.bottomMargin: root.layoutUnit * root.actionBottomMarginRatio
			width: root.actionButtonWidth
			height: root.actionButtonHeight

			TechTreeResearchButton {
				anchors.fill: parent
				scaleW: root.actionButtonScaleW
				scaleH: root.actionButtonScaleH
				visible: root.showUpgradeButton
				titleText: root.nodeModel ? root.nodeModel.upgradeDurationText : ""
				costText: root.nodeModel ? root.nodeModel.upgradeCostText : ""
				fillColor: root.actionFillColor
				enabled: root.techTreeModel !== null
					&& root.nodeModel !== null
					&& root.actionEnabled
				onClicked: root.performAction()
			}

			GemSkipButton {
				anchors.fill: parent
				scaleW: root.actionButtonScaleW
				scaleH: root.actionButtonScaleH
				visible: root.showSkipButton
				costText: root.nodeModel ? root.nodeModel.skipGemCostText : ""
				fillColor: root.actionFillColor
				enabled: root.techTreeModel !== null
					&& root.nodeModel !== null
					&& root.actionEnabled
				onClicked: root.performAction()
			}

			RectRoundButton {
				anchors.fill: parent
				scaleW: root.actionButtonScaleW
				scaleH: root.actionButtonScaleH
				labelPixelSize: root.actionButtonFontPixelSize
				visible: root.showClaimButton
				locId: root.completeLocId
				locTable: "General"
				fillColor: root.actionFillColor
				enabled: root.techTreeModel !== null
					&& root.nodeModel !== null
					&& root.actionEnabled
				onClicked: root.performAction()
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
