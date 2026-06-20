import QtQuick
import ui 1.0

Item {
	id: root

	property string locId: ""
	property string locTable: "General"
	property string prefix: ""
	property string suffix: ""
	property var formatArgs: []

	property bool useUiFont: false
	property real pixelSize: 24
	property color fillColor: Theme.white
	property real letterSpacing: 0
	property int outlineWeight: 4
	property color outlineColor: Theme.black
	property int outlineSamples: 32

	readonly property real _actualOutlineWidth: pixelSize * (outlineWeight / 100.0)
	readonly property string _currentFontFamily: {
		if (!root.useUiFont)
			return Theme.latinFontFamily
		switch (Theme.language) {
		case "ko":
			return Theme.fontKR.status === FontLoader.Ready ? Theme.fontKR.name : Theme.latinFontFamily
		case "ja":
			return Theme.fontJP.status === FontLoader.Ready ? Theme.fontJP.name : Theme.latinFontFamily
		case "ru":
			return Theme.fontRU.status === FontLoader.Ready ? Theme.fontRU.name : Theme.latinFontFamily
		case "tr-TR":
			return Theme.fontTR.status === FontLoader.Ready ? Theme.fontTR.name : Theme.latinFontFamily
		default:
			return Theme.latinFontFamily
		}
	}

	property string _displayText: ""

	implicitWidth: mainText.implicitWidth + _actualOutlineWidth * 2
	implicitHeight: mainText.implicitHeight + _actualOutlineWidth * 2

	layer.enabled: true
	layer.smooth: true

	function updateText() {
		if (!locId) {
			_displayText = prefix + suffix
			return
		}
		_displayText = prefix + LocManager.get_string(locId, Theme.language, locTable, formatArgs) + suffix
	}

	onLocIdChanged: updateText()
	onLocTableChanged: updateText()
	onPrefixChanged: updateText()
	onSuffixChanged: updateText()
	onFormatArgsChanged: updateText()

	Connections {
		target: Theme
		function onLanguageChanged() { root.updateText() }
		function onFontsChanged() { root.updateText() }
	}

	Component.onCompleted: updateText()

	Item {
		anchors.centerIn: parent
		width: mainText.implicitWidth
		height: mainText.implicitHeight

		Repeater {
			model: root.outlineWeight > 0 ? root.outlineSamples : 0

			Text {
				readonly property real angle: (index / root.outlineSamples) * Math.PI * 2
				x: Math.cos(angle) * root._actualOutlineWidth
				y: Math.sin(angle) * root._actualOutlineWidth
				text: root._displayText
				font.family: root._currentFontFamily
				font.pixelSize: root.pixelSize
				font.letterSpacing: root.letterSpacing
				color: root.outlineColor
			}
		}

		Text {
			id: mainText
			text: root._displayText
			font.family: root._currentFontFamily
			font.pixelSize: root.pixelSize
			font.letterSpacing: root.letterSpacing
			color: root.fillColor
		}
	}
}
