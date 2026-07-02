import QtQuick
import ui 1.0

CurrencyButton {
	id: root

	currencyIconSource: Qt.resolvedUrl("../../../assets/sprites/Currency/skillTicket.png")

	property int summonCount: 1
	property int cost: 0
	property alias spriteImage: root.currencyIconSource

	readonly property string formattedCost: {
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		return TmpTextBridge.format_integer_text(root.cost)
	}

	readonly property string resolvedTitle: {
		UiLocale.selectedCode
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		return TmpTextBridge.skill_summon_title(UiLocale.selectedCode, root.summonCount)
	}

	titleText: root.resolvedTitle
	costText: root.formattedCost
}
