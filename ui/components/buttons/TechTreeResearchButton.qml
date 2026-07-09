import QtQuick
import ui 1.0

CurrencyButton {
	aspectW: 3.5
	aspectH: 2
	titleFontScale: 0.35
	costFontScale: 0.35
	titleRowVerticalCenterOffsetRatio: -0.25
	
	titleIconSource: Qt.resolvedUrl("../../../assets/sprites/General/Icons.png")
	titleIconSpriteIndex: 29
	currencyIconSource: Qt.resolvedUrl("../../../assets/sprites/Currency/techPotions.png")
}
