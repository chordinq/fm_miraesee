pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property var petController: null
	property var petCollectionModel: null
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
		currencyIcon: root.petController ? root.petController.summonSpriteImage : ""
		currencyAmount: root.petController ? root.petController.eggshellCount : 0
		gemAmount: root.sessionBridge ? root.sessionBridge.gemCount : 0
	}

	EggSummonPreview {
		id: petSummonPreview

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
		preview: root.petController ? root.petController.summonPreview : []
		ascensionLevel: root.petController ? root.petController.ascensionLevel : 0
	}

	Item {
		id: petSideColumn

		visible: root.summonPreviewWidthRatio < 1
		anchors.top: parent.top
		anchors.bottom: summonFooter.top
		anchors.left: petSummonPreview.right
		anchors.right: parent.right
		anchors.margins: root.topMargin

		readonly property real sectionGap: Math.max(4, height * 0.02)

		SummonResultView {
			id: petSummonResultView

			anchors.top: parent.top
			anchors.left: parent.left
			anchors.right: parent.right
			height: parent.height / 3 - parent.sectionGap / 2
			panelCornerRadius: root.panelCornerRadius
			summonController: root.petController
		}

		BonusOptimizerPanel {
			anchors.top: petSummonResultView.bottom
			anchors.topMargin: parent.sectionGap
			anchors.left: parent.left
			anchors.right: parent.right
			anchors.bottom: parent.bottom
			panelCornerRadius: root.panelCornerRadius
			summonController: root.petController
		}
	}

	LoadingOverlay {
		active: root.petController ? root.petController.isOptimizing : false
		iconSizeRatio: 0.06
	}

	Row {
		id: bottomColumn

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: summonFooter.verticalCenter
		spacing: root.summonBarSpacing

		BulkSummonToggleView {
			height: root.summonButtonHeight
			summonController: root.petController
		}

		EggSummonButton {
			width: root.summonButtonWidth
			height: root.summonButtonHeight
			summonCount: root.petController ? root.petController.summonCount : 1
			cost: root.petController ? root.petController.summonCost : 0
			spriteImage: root.petController ? root.petController.summonSpriteImage : ""
			fillColor: root.petController && root.petController.canAffordSummon
				? Theme.blue
				: Theme.lightGrey
			buttonEnabled: root.petController && root.petController.canAffordSummon
			onClicked: {
				if (root.petController)
					root.petController.performSummon()
			}
		}

		SummonUpgradeStatusView {
			height: root.summonButtonHeight
			summonController: root.petController
		}
	}
}
