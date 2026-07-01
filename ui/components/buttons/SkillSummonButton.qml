import QtQuick
import ui 1.0

CurrencyButton {
	id: root

	titleLocId: "11670393447301120"
	currencyIconSource: Qt.resolvedUrl("../../../assets/sprites/Currency/skillTicket.png")

	property int summonCount: 1
	property int cost: 0
	property alias spriteImage: root.currencyIconSource

	readonly property string formattedCost: {
		NumberDisplay.revision
		UiSettings.gameNumberFormattingEnabled
		return NumberDisplay.formatInteger(root.cost)
	}
	readonly property string formattedSummonCount: {
		NumberDisplay.revision
		UiSettings.gameNumberFormattingEnabled
		return NumberDisplay.formatInteger(root.summonCount)
	}

	titleSuffix: "x" + root.formattedSummonCount
	costText: root.formattedCost
}
