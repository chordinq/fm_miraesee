import QtQuick
import ui 1.0

Item {
	id: root

	property string tmpText: ""
	property string iconSource: ""
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

	readonly property bool _hasIcon: root.iconSource.length > 0
	readonly property url _iconUrl: root._hasIcon ? Qt.resolvedUrl(root.iconSource) : ""
	readonly property int wrapMode: root.wordWrap ? Text.WordWrap : Text.NoWrap
	readonly property int _outlineSamples: 16
	readonly property real _fontPx: Math.max(1, root.bodyPixelSize)
	readonly property real _outlinePad: root._fontPx * (root.outlineWeight / 100.0)
	readonly property real _lineHeight: root._fontPx * (1.0 + root.lineSpacing)
	readonly property bool _wraps: root.wordWrap && textRoot.width > 0
	readonly property real _contentWidth: root._wraps
		? textRoot.width - root._outlinePad * 2
		: 0

	readonly property string _plainText: root.tmpText

	readonly property var _textRuns: {
		if (root._plainText === "")
			return []
		var runs = []
		var pattern = /[\x00-\x7F]+|[^\x00-\x7F]+/g
		var match
		while ((match = pattern.exec(root._plainText)) !== null)
			runs.push({ text: match[0], latin: /^[\x00-\x7F]+$/.test(match[0]) })
		return runs
	}

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

	function _buildHtml(withFillColor) {
		void root._fontEpoch
		if (root._plainText === "")
			return ""

		if (root._hasMixedScripts) {
			var mixed = ""
			for (var i = 0; i < root._textRuns.length; i++) {
				var run = root._textRuns[i]
				var runFamily = run.latin ? Theme.latinFontFamily : Theme.fontFamilyForText(run.text)
				var runWeight = run.latin ? "normal" : "bold"
				mixed += root._span(
					run.text,
					runFamily,
					runWeight,
					withFillColor ? root.fillColor : undefined)
			}
			return mixed
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

		Image {
			visible: root._hasIcon
			width: root.iconPixelSize
			height: root.iconPixelSize
			source: root._iconUrl
			fillMode: Image.PreserveAspectFit
			smooth: true
			anchors.verticalCenter: parent.verticalCenter
		}

		Item {
			id: textRoot

			implicitWidth: root._wraps
				? root.width - (root._hasIcon ? root.iconPixelSize + root.iconTextSpacing : 0)
				: fillText.implicitWidth + root._outlinePad * 2
			implicitHeight: fillText.implicitHeight + root._outlinePad * 2
			width: implicitWidth
			height: implicitHeight

			layer.enabled: root.outlineWeight > 0
			layer.smooth: true

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
