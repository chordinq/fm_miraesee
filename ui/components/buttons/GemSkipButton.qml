import QtQuick
import ui 1.0

CurrencyButton {
	id: root
	titleFontScale: 0.35
	costFontScale: 0.35
	titleRowVerticalCenterOffsetRatio: -0.25

	currencyIconSource: Qt.resolvedUrl("../../../assets/sprites/Currency/GemIcon.png")

	property int cost: 0

	readonly property string formattedCost: {
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		return TmpTextBridge.format_integer_text(root.cost)
	}

	readonly property string resolvedTitle: {
		UiLocale.selectedCode
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		return TmpTextBridge.skip_button_title(UiLocale.selectedCode)
	}

	titleText: root.resolvedTitle
	costText: root.formattedCost
}
