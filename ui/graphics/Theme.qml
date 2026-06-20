pragma Singleton
import QtQuick

QtObject {
	id:	sharedTheme

	property string	language:	"en"
	property real	uiScale:	1.0

	signal fontsChanged()

	readonly property FontLoader fontBaloo:	FontLoader {
		source: "../../assets/Fonts/Baloo-Regular.ttf"
		onStatusChanged: if (status === FontLoader.Ready) sharedTheme.fontsChanged()
	}
	readonly property FontLoader fontKR:	FontLoader {
		source: "../../assets/Fonts/NotoSansKR-Bold.otf"
		onStatusChanged: if (status === FontLoader.Ready) sharedTheme.fontsChanged()
	}
	readonly property FontLoader fontJP:	FontLoader {
		source: "../../assets/Fonts/NotoSansJP-Bold.otf"
		onStatusChanged: if (status === FontLoader.Ready) sharedTheme.fontsChanged()
	}
	readonly property FontLoader fontRU:	FontLoader {
		source: "../../assets/Fonts/NotoSansRU-Bold.ttf"
		onStatusChanged: if (status === FontLoader.Ready) sharedTheme.fontsChanged()
	}
	readonly property FontLoader fontTR:	FontLoader {
		source: "../../assets/Fonts/NotoSansTR-Bold.ttf"
		onStatusChanged: if (status === FontLoader.Ready) sharedTheme.fontsChanged()
	}

	readonly property string latinFontFamily: fontBaloo.status === FontLoader.Ready ? fontBaloo.name : ""
	readonly property string uiFontFamily: {
		switch (language) {
		case "ko":
			return fontKR.status === FontLoader.Ready ? fontKR.name : latinFontFamily
		case "ja":
			return fontJP.status === FontLoader.Ready ? fontJP.name : latinFontFamily
		case "ru":
			return fontRU.status === FontLoader.Ready ? fontRU.name : latinFontFamily
		case "tr-TR":
			return fontTR.status === FontLoader.Ready ? fontTR.name : latinFontFamily
		default:
			return latinFontFamily
		}
	}

	readonly property color black:						"#000000"
	readonly property color	white:						"#FFFFFF"
	readonly property color transparent:				"#00000000"
	readonly property color	brown:						"#E5A27D"
	readonly property color	lightRed:					"#FF4755"
	readonly property color	red:						"#F9595F"
	readonly property color	greyInactive:				"#D1D1D1"
	readonly property color	greyText:					"#838383"
	readonly property color	darkGreyText:				"#8E8E8E"
	readonly property color	yellowText:					"#FDC74F"
	readonly property color	checkBoxActiveGrey:			"#42495B"
	readonly property color	blue:						"#00A3FF"
	readonly property color	darkBlue:					"#272C38"
	readonly property color	lightGrey:					"#E8E8E8"
	readonly property color	darkGrey:					"#4A4A4A"
	readonly property color	lightBlue:					"#9CDBFF"
	readonly property color	lightGreen:					"#82D67F"
	readonly property color	lightishGreen:				"#4FD639"
	readonly property color	green:						"#24FF00"
	readonly property color	greenText:					"#06AD00"
	readonly property color	darkGreen:					"#17A200"
	readonly property color	orange:						"#FAA019"
	readonly property color	ghost:						"#8493AC"
	readonly property color	zombieSkin:					"#9AB97D"
	readonly property color	zombieBody:					"#758D5E"
	readonly property color	commonGrey:					"#F1F1F1"
	readonly property color	rareBlue:					"#5DD8FF"
	readonly property color	epicGreen:					"#5DFF8A"
	readonly property color	legendaryGold:				"#FCFF5D"
	readonly property color	ultimateRed:				"#FF5D5D"
	readonly property color	mythicPurple:				"#D55DFF"
	readonly property color	darkText:					"#5C5C5C"
	readonly property color	otherPlayerChatColor:		"#FFC144"
	readonly property color	hardestMissionColor:		"#E088FF"

	readonly property color	colorPrimitive:				"#F1F1F1"
	readonly property color	colorMedieval:				"#5DD8FF"
	readonly property color	colorEarlyModern:			"#5DFF8A"
	readonly property color	colorModern:				"#FCFF5D"
	readonly property color	colorSpace:					"#FF5D5D"
	readonly property color	colorInterstellar:			"#D55DFF"
	readonly property color	colorMultiverse:			"#74FFEE"
	readonly property color	colorQuantum:				"#7C5DFF"
	readonly property color	colorUnderworld:			"#AF7979"
	readonly property color	colorDivine:				"#FE9E0C"

	readonly property var itemAgeColors: [
		colorPrimitive,
		colorMedieval,
		colorEarlyModern,
		colorModern,
		colorSpace,
		colorInterstellar,
		colorMultiverse,
		colorQuantum,
		colorUnderworld,
		colorDivine
	]

	readonly property var rarityColors: [
		commonGrey,
		rareBlue,
		epicGreen,
		legendaryGold,
		ultimateRed,
		mythicPurple
	]
}
