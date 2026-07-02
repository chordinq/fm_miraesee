import QtQuick
import ui 1.0

Item {
	id: root

	property string tmpText: ""
	property string suffixText: ""
	property color suffixFillColor: "transparent"
	property string iconSource: ""
	property string iconSpriteSource: ""
	property int iconSpriteIndex: -1
	property real bodyPixelSize: 24
	property color fillColor: Theme.white
	property real fillOpacity: 1.0
	property color outlineColor: Theme.black
	property int outlineWeight: 0
	property real letterSpacing: 0
	property real lineSpacing: 0.09
	property bool wordWrap: false
	property int horizontalAlignment: Text.AlignLeft
	property real iconPixelSize: root.bodyPixelSize * 1.15
	property real iconTextSpacing: root.bodyPixelSize * 0.12

	property int _fontEpoch: 0

	readonly property bool _hasSpriteIcon:
		root.iconSpriteIndex >= 0 && root.iconSpriteSource.length > 0
	readonly property bool _hasImageIcon:
		!root._hasSpriteIcon && root.iconSource.length > 0
	readonly property bool _hasIcon: root._hasSpriteIcon || root._hasImageIcon
	readonly property url _iconUrl:
		root._hasImageIcon ? Qt.resolvedUrl(root.iconSource) : ""
	readonly property url _spriteSheetUrl:
		root._hasSpriteIcon ? Qt.resolvedUrl(root.iconSpriteSource) : ""
	readonly property int wrapMode: root.wordWrap ? Text.WordWrap : Text.NoWrap
	readonly property int _outlineSamples: 16
	readonly property real _fontPx: Math.max(1, root.bodyPixelSize)
	readonly property real _outlinePad: root._fontPx * (root.outlineWeight / 100.0)
	readonly property real _lineHeight: root._fontPx * (1.0 + root.lineSpacing)
	readonly property bool _wraps: root.wordWrap && root.width > 0
	readonly property real _contentWidth: root._wraps
		? Math.max(
			0,
			root.width
				- (root._hasIcon ? root.iconPixelSize + root.iconTextSpacing : 0)
				- root._outlinePad * 2)
		: 0

	readonly property string _plainText: root.tmpText + root.suffixText

	readonly property bool _useSuffixColor:
		root.suffixText !== "" && root.suffixFillColor.a > 0

	readonly property bool _hasMixedScripts:
		root._plainText.length > 0
		&& /[^\x00-\x7F]/.test(root._plainText)
		&& /[\x00-\x7F]/.test(root._plainText)

	readonly property string _fillHtml: root._buildHtml(true)
	readonly property string _outlineHtml: root._buildHtml(false)

	implicitWidth: (root._hasIcon ? root.iconPixelSize + root.iconTextSpacing : 0)
		+ textRoot.implicitWidth
	implicitHeight: Math.max(root._hasIcon ? root.iconPixelSize : 0, textRoot.implicitHeight)
	height: implicitHeight

	baselineOffset: textRoot.y + stack.y + fillText.baselineOffset

	property alias pixelSize: root.bodyPixelSize
	property alias text: root.tmpText

	function _escapeRichText(value) {
		return value
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
	}

	function _colorCss(value) {
		var c = Qt.color(value)
		var r = Math.round(c.r * 255).toString(16).padStart(2, "0")
		var g = Math.round(c.g * 255).toString(16).padStart(2, "0")
		var b = Math.round(c.b * 255).toString(16).padStart(2, "0")
		return "#" + r + g + b
	}

	function _runStyle(family, weight, colorValue) {
		var style = "font-family:'" + family + "'; font-weight:" + weight
			+ "; font-size:" + Math.round(root._fontPx) + "px"
		if (colorValue !== undefined)
			style += "; color:" + root._colorCss(colorValue)
		return style
	}

	function _span(textValue, family, weight, colorValue) {
		return "<span style=\"" + root._runStyle(family, weight, colorValue) + "\">"
			+ root._escapeRichText(textValue) + "</span>"
	}

	function _familyForPlainText(value) {
		void root._fontEpoch
		return Theme.fontFamilyForText(value)
	}

	function _weightForFamily(family) {
		return family === Theme.latinFontFamily ? "normal" : "bold"
	}

	function _buildScriptRunsHtml(text, colorValue, withFillColor) {
		if (text === "")
			return ""
		var html = ""
		var pattern = /[\x00-\x7F]+|[^\x00-\x7F]+/g
		var match
		while ((match = pattern.exec(text)) !== null) {
			var runText = match[0]
			var latin = /^[\x00-\x7F]+$/.test(runText)
			var family = latin ? Theme.latinFontFamily : root._familyForPlainText(runText)
			var weight = latin ? "normal" : root._weightForFamily(family)
			html += root._span(
				runText,
				family,
				weight,
				withFillColor ? colorValue : undefined)
		}
		return html
	}

	function _buildHtml(withFillColor) {
		void root._fontEpoch
		if (root._plainText === "")
			return ""

		if (root._useSuffixColor) {
			return root._buildScriptRunsHtml(root.tmpText, root.fillColor, withFillColor)
				+ root._buildScriptRunsHtml(root.suffixText, root.suffixFillColor, withFillColor)
		}

		if (root._hasMixedScripts) {
			return root._buildScriptRunsHtml(root._plainText, root.fillColor, withFillColor)
		}

		var singleFamily = root._familyForPlainText(root._plainText)
		return root._span(
			root._plainText,
			singleFamily,
			root._weightForFamily(singleFamily),
			withFillColor ? root.fillColor : undefined)
	}

	Row {
		id: contentRow

		spacing: root._hasIcon ? root.iconTextSpacing : 0

		Item {
			visible: root._hasIcon
			width: root._hasIcon ? root.iconPixelSize : 0
			height: root._hasIcon ? root.iconPixelSize : 0

			SpriteSheet {
				anchors.fill: parent
				visible: root._hasSpriteIcon
				source: root._spriteSheetUrl
				spriteIndex: root.iconSpriteIndex
			}

			Image {
				anchors.fill: parent
				visible: root._hasImageIcon
				source: root._iconUrl
				fillMode: Image.PreserveAspectFit
				smooth: true
			}
		}

		Item {
			id: textRoot

			implicitWidth: root._wraps
				? root.width - (root._hasIcon ? root.iconPixelSize + root.iconTextSpacing : 0)
				: fillText.implicitWidth + root._outlinePad * 2
			implicitHeight: fillText.implicitHeight + root._outlinePad * 2

			layer.enabled: root.outlineWeight > 0
			layer.smooth: true
			layer.mipmap: true

			Item {
				id: stack

				anchors.left: parent.left
				anchors.top: parent.top
				anchors.leftMargin: root._outlinePad
				anchors.topMargin: root._outlinePad
				width: root._wraps ? root._contentWidth : fillText.implicitWidth
				height: fillText.implicitHeight

				Repeater {
					model: root.outlineWeight > 0 ? root._outlineSamples : 0

					Text {
						id: outlineSample

						readonly property real angle: (index / root._outlineSamples) * Math.PI * 2
						x: Math.cos(angle) * root._outlinePad
						y: Math.sin(angle) * root._outlinePad
						textFormat: Text.RichText
						text: root._outlineHtml
						wrapMode: root.wrapMode
						horizontalAlignment: root.horizontalAlignment
						font.letterSpacing: root.letterSpacing
						lineHeight: root.wordWrap ? root._lineHeight : 1
						lineHeightMode: root.wordWrap ? Text.FixedHeight : Text.ProportionalHeight
						color: root.outlineColor

						states: State {
							name: "wrapped"
							when: root._wraps
							PropertyChanges {
								target: outlineSample
								width: root._contentWidth
							}
						}
					}
				}

				Text {
					id: fillText

					opacity: root.fillOpacity
					textFormat: Text.RichText
					text: root._fillHtml
					wrapMode: root.wrapMode
					horizontalAlignment: root.horizontalAlignment
					font.letterSpacing: root.letterSpacing
					lineHeight: root.wordWrap ? root._lineHeight : 1
					lineHeightMode: root.wordWrap ? Text.FixedHeight : Text.ProportionalHeight

					states: State {
						name: "wrapped"
						when: root._wraps
						PropertyChanges {
							target: fillText
							width: root._contentWidth
						}
					}
				}
			}
		}
	}

	Connections {
		target: Theme
		function onFontsChanged() {
			root._fontEpoch++
		}
	}
}
