pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property var mountController: null
	property var mountCollectionModel: null
	property var sessionBridge: null
	property real summonPreviewWidthRatio: 1.0
	property real panelCornerRatio: 255 / (512 * 50)

	readonly property real panelCornerRadius: width * panelCornerRatio
	readonly property real summonAspect: SummonButtonMetrics.aspect
	readonly property real bottomMargin: Math.max(8, height * 0.04)
	readonly property real topMargin: Math.max(8, width * 0.02)
	readonly property real summonFooterPadding: Math.max(8, summonFooter.height * 0.12)
	readonly property real summonButtonHeight: summonFooter.currencyInnerHeight
	readonly property real summonBarSpacing: summonButtonHeight * 0.2
	readonly property real summonButtonWidth: Math.min(
		summonButtonHeight * summonAspect,
		(width - summonBarSpacing * 3) * 0.5
	)

	Rectangle {
		anchors.fill: parent
		color: Qt.darker(Theme.darkBlue, 1.5)
	}

	SummonFooterBackground {
		id: summonFooter

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		anchors.leftMargin: root.topMargin
		anchors.rightMargin: root.topMargin
		anchors.bottomMargin: root.topMargin
		contentPadding: root.summonFooterPadding
		panelCornerRadius: root.panelCornerRadius
		currencyIcon: root.mountController ? root.mountController.summonSpriteImage : ""
		currencyAmount: root.mountController ? root.mountController.clockWinderCount : 0
		gemAmount: root.sessionBridge ? root.sessionBridge.gemCount : 0
	}

	MountSummonPreview {
		id: mountSummonPreview

		anchors.top: parent.top
		anchors.bottom: summonFooter.top
		anchors.left: parent.left
		anchors.leftMargin: root.topMargin
		anchors.topMargin: root.topMargin
		anchors.bottomMargin: root.topMargin
		anchors.right: root.summonPreviewWidthRatio >= 1 ? parent.right : undefined
		anchors.rightMargin: root.summonPreviewWidthRatio >= 1 ? root.topMargin : undefined
		width: root.summonPreviewWidthRatio >= 1
			? undefined
			: parent.width * root.summonPreviewWidthRatio
		panelCornerRadius: root.panelCornerRadius
		preview: root.mountController ? root.mountController.summonPreview : []
		ascensionLevel: root.mountController ? root.mountController.ascensionLevel : 0
	}

	Item {
		id: mountSideColumn

		visible: root.summonPreviewWidthRatio < 1
		anchors.top: parent.top
		anchors.bottom: summonFooter.top
		anchors.left: mountSummonPreview.right
		anchors.right: parent.right
		anchors.margins: root.topMargin

		readonly property real sectionGap: Math.max(4, height * 0.02)

		SummonResultView {
			id: mountSummonResultView

			anchors.top: parent.top
			anchors.left: parent.left
			anchors.right: parent.right
			height: parent.height / 3 - parent.sectionGap / 2
			panelCornerRadius: root.panelCornerRadius
			summonController: root.mountController
		}

		BonusOptimizerPanel {
			anchors.top: mountSummonResultView.bottom
			anchors.topMargin: parent.sectionGap
			anchors.left: parent.left
			anchors.right: parent.right
			anchors.bottom: parent.bottom
			panelCornerRadius: root.panelCornerRadius
			summonController: root.mountController
		}
	}

	LoadingOverlay {
		active: root.mountController ? root.mountController.isOptimizing : false
		iconSizeRatio: 0.06
	}

	Row {
		id: bottomColumn

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: summonFooter.verticalCenter
		spacing: root.summonBarSpacing

		BulkSummonToggleView {
			height: root.summonButtonHeight
			summonController: root.mountController
		}

		MountSummonButton {
			width: root.summonButtonWidth
			height: root.summonButtonHeight
			summonCount: root.mountController ? root.mountController.summonCount : 1
			cost: root.mountController ? root.mountController.summonCost : 0
			spriteImage: root.mountController ? root.mountController.summonSpriteImage : ""
			fillColor: root.mountController && root.mountController.canAffordSummon
				? Theme.blue
				: Theme.lightGrey
			buttonEnabled: root.mountController && root.mountController.canAffordSummon
			onClicked: {
				if (root.mountController)
					root.mountController.performSummon()
			}
		}

		SummonUpgradeStatusView {
			height: root.summonButtonHeight
			summonController: root.mountController
		}
	}
}
