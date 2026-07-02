import QtQuick
import QtQuick.Controls
import ui 1.0
import TMPText 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "CurrencyView / SummonButton preview"
	color: Theme.white

	readonly property real margin: Math.max(24, width * 0.04)
	readonly property real sectionGap: Math.max(20, height * 0.03)
	readonly property real barHeight: Math.max(40, height * 0.08)
	readonly property real columnSpacing: barHeight * 0.65
	readonly property real leftInset: barHeight * 1.5 * 0.5

	readonly property real summonAspect: SummonButtonMetrics.aspect
	readonly property real targetSummonHeight: height * 0.1
	readonly property real summonBarSpacing: targetSummonHeight * 0.2
	readonly property real summonButtonWidth: Math.min(
		targetSummonHeight * summonAspect,
		(width - summonBarSpacing * 2) * 0.34
	)
	readonly property real summonButtonHeight: summonButtonWidth / summonAspect
	readonly property real summonFooterPadding: Math.max(8, height * 0.015)
	readonly property real summonFooterHeight:
		summonButtonHeight + summonFooterPadding * 2

	Column {
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.leftMargin: margin + leftInset
		anchors.topMargin: margin
		anchors.rightMargin: margin
		width: parent.width - margin * 2
		spacing: columnSpacing

		TMPText {
			tmpText: "CurrencyView"
			pixelSize: Math.max(14, width * 0.02)
			fillColor: Theme.darkGreyText
			outlineWeight: 0
		}

		CurrencyView {
			height: window.barHeight
			iconSource: Qt.resolvedUrl("../../assets/sprites/Currency/Eggshells.png")
			amount: 16100
		}

		CurrencyView {
			height: window.barHeight
			iconSource: Qt.resolvedUrl("../../assets/sprites/Currency/skillTicket.png")
			amount: 4470
		}

		CurrencyView {
			height: window.barHeight
			iconSource: Qt.resolvedUrl("../../assets/sprites/Currency/techPotions.png")
			amount: 26600
		}

		CurrencyView {
			height: window.barHeight
			iconSource: Qt.resolvedUrl("../../assets/sprites/Currency/GemIcon.png")
			amount: 250
		}

		CurrencyView {
			height: window.barHeight
			iconSource: Qt.resolvedUrl("../../assets/sprites/Currency/clockWinders.png")
			amount: 83
		}

		Item {
			width: 1
			height: window.sectionGap
		}

		TMPText {
			tmpText: "SummonButton  scaleW "
				+ SummonButtonMetrics.scaleW.toFixed(2)
				+ "  scaleH "
				+ SummonButtonMetrics.scaleH.toFixed(2)
				+ "  aspect "
				+ SummonButtonMetrics.aspect.toFixed(3)
			pixelSize: Math.max(14, width * 0.02)
			fillColor: Theme.darkGreyText
			outlineWeight: 0
		}
	}

	SummonFooterBackground {
		id: summonFooter

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		height: window.summonFooterHeight
		contentPadding: window.summonFooterPadding
		currencyIcon: Qt.resolvedUrl("../../assets/sprites/Currency/skillTicket.png")
		currencyAmount: 4470
		gemAmount: 250
	}

	Row {
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: summonFooter.verticalCenter
		spacing: window.summonBarSpacing

		SkillSummonButton {
			height: window.summonButtonHeight
			summonCount: 10
			cost: 50
			fillColor: Theme.blue
			buttonEnabled: true
		}

		EggSummonButton {
			height: window.summonButtonHeight
			summonCount: 1
			cost: 100
			fillColor: Theme.blue
			buttonEnabled: true
		}

		MountSummonButton {
			height: window.summonButtonHeight
			summonCount: 1
			cost: 5
			fillColor: Theme.lightGrey
			buttonEnabled: false
		}
	}
}
