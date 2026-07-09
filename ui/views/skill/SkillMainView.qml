pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property var skillController: null
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
		currencyIcon: root.skillController ? root.skillController.summonSpriteImage : ""
		currencyAmount: root.skillController ? root.skillController.ticketCount : 0
		gemAmount: root.sessionBridge ? root.sessionBridge.gemCount : 0
	}

	SkillSummonPreview {
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
		preview: root.skillController ? root.skillController.summonPreview : []
		ascensionLevel: root.skillController ? root.skillController.ascensionLevel : 0
	}

	Row {
		id: bottomColumn

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: summonFooter.verticalCenter
		spacing: root.summonBarSpacing

		BulkSummonToggleView {
			height: root.summonButtonHeight
			summonController: root.skillController
		}

		SkillSummonButton {
			width: root.summonButtonWidth
			height: root.summonButtonHeight
			summonCount: root.skillController ? root.skillController.summonCount : 5
			cost: root.skillController ? root.skillController.summonCost : 0
			spriteImage: root.skillController ? root.skillController.summonSpriteImage : ""
			fillColor: root.skillController && root.skillController.canAffordSummon
				? Theme.blue
				: Theme.lightGrey
			buttonEnabled: root.skillController && root.skillController.canAffordSummon
			onClicked: {
				if (root.skillController)
					root.skillController.performSummon()
			}
		}

		SummonUpgradeStatusView {
			height: root.summonButtonHeight
			summonController: root.skillController
		}
	}
}
