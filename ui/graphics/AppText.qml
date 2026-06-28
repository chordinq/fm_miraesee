import QtQuick
import ui 1.0

Item {
    id: root

    property string locId: ""
    property string locTable: "General"
    property var formatArgs: []
    property string prefix: ""
    property string text: ""
    property string suffix: ""

    property real pixelSize: 24
    property color fillColor: Theme.white
    property int outlineWeight: 4
    property color outlineColor: Theme.black
    property int outlineSamples: 16

    property real letterSpacing: 0
    property real lineSpacing: 0.09
    property int wrapMode: Text.NoWrap
    property int horizontalAlignment: Text.AlignLeft

    property real _pixelSizeLatch: 0.65
    property real _stablePixelSize: 1
    property real _stableWrapWidth: 0
    property real wrapWidthHysteresis: 10

    readonly property bool _applyLineSpacing: root._wraps

    property int _fontEpoch: 0

    readonly property real _actualOutlineWidth: _stablePixelSize * (outlineWeight / 100.0)
    readonly property bool _wraps: root.wrapMode !== Text.NoWrap
    readonly property real _lineHeight: _stablePixelSize * (1.0 + root.lineSpacing)

    readonly property string _coreText: locId !== ""
        ? LocManager.get_string(locId, Theme.language, locTable, formatArgs)
        : text

    readonly property string _plainText: prefix + _coreText + suffix

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

    readonly property bool _useSplitFonts: root._hasMixedScripts && !root._wraps
    readonly property bool _useRichText: root._hasMixedScripts && root._wraps

    readonly property string _richText: {
        void root._fontEpoch
        if (!root._useRichText)
            return ""
        var out = ""
        for (var i = 0; i < root._textRuns.length; i++) {
            var run = root._textRuns[i]
            var family = run.latin ? Theme.latinFontFamily : Theme.fontFamilyForText(run.text)
            var weight = run.latin ? "normal" : "bold"
            out += "<span style=\"font-family:'" + family + "'; font-weight:" + weight + "\">"
            out += root._escapeRichText(run.text)
            out += "</span>"
        }
        return out
    }

    readonly property int _textFormat: root._useRichText ? Text.RichText : Text.PlainText
    readonly property string _displayText: root._useRichText ? root._richText : root._plainText

    readonly property bool _coreHasNonAscii: /[^\x00-\x7F]/.test(_coreText)

    readonly property string _singleFontFamily: {
        void root._fontEpoch
        return Theme.fontFamilyForText(_coreText)
    }

    readonly property int _singleFontWeight:
        Theme.fontFamilyForText(_coreText) === Theme.latinFontFamily ? Font.Normal : Font.Bold

    readonly property real _wrapWidthCandidate: root._wraps
        ? Math.max(1, root.width - root._actualOutlineWidth * 2)
        : mainText.implicitWidth

    readonly property real _textWidth: root._wraps
        ? root._stableWrapWidth
        : mainText.implicitWidth

    implicitWidth: root._useSplitFonts
        ? segmentHost.width
        : mainText.implicitWidth + root._actualOutlineWidth * 2
    implicitHeight: root._useSplitFonts
        ? segmentHost.height
        : mainText.implicitHeight + root._actualOutlineWidth * 2
    height: implicitHeight

    baselineOffset: root._useSplitFonts
        ? segmentHost.y + segmentRow.y + segmentRow.baselineOffset
        : container.y + mainText.baselineOffset

    function _escapeRichText(value) {
        return value
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
    }

    function updateStablePixelSize() {
        var target = Math.max(1, root.pixelSize)
        if (root._stablePixelSize <= 0) {
            root._stablePixelSize = target
            return
        }
        if (target > root._stablePixelSize && root.pixelSize >= root._stablePixelSize + root._pixelSizeLatch)
            root._stablePixelSize = target
        else if (target < root._stablePixelSize && root.pixelSize <= root._stablePixelSize - root._pixelSizeLatch)
            root._stablePixelSize = target
    }

    function updateStableWrapWidth() {
        if (!root._wraps) {
            root._stableWrapWidth = 0
            return
        }
        var candidate = root._wrapWidthCandidate
        if (root._stableWrapWidth <= 0) {
            root._stableWrapWidth = candidate
            return
        }
        wrapProbe.width = root._stableWrapWidth
        var stableLines = wrapProbe.lineCount
        wrapProbe.width = candidate
        var candidateLines = wrapProbe.lineCount
        if (stableLines !== candidateLines) {
            if (Math.abs(candidate - root._stableWrapWidth) >= root.wrapWidthHysteresis)
                root._stableWrapWidth = candidate
        } else {
            root._stableWrapWidth = candidate
        }
    }

    function refreshStableLayout() {
        updateStablePixelSize()
        updateStableWrapWidth()
    }

    Component.onCompleted: refreshStableLayout()

    onPixelSizeChanged: refreshStableLayout()
    onWidthChanged: updateStableWrapWidth()
    onLocIdChanged: updateStableWrapWidth()
    onFormatArgsChanged: updateStableWrapWidth()
    onTextChanged: updateStableWrapWidth()
    onPrefixChanged: updateStableWrapWidth()
    onSuffixChanged: updateStableWrapWidth()
    onWrapModeChanged: refreshStableLayout()
    onOutlineWeightChanged: updateStableWrapWidth()
    on_StablePixelSizeChanged: updateStableWrapWidth()

    Connections {
        target: Theme
        function onFontsChanged() {
            root._fontEpoch++
            root.updateStableWrapWidth()
        }
    }

    Text {
        id: wrapProbe

        visible: false
        height: 0
        textFormat: root._textFormat
        text: root._displayText
        wrapMode: Text.WordWrap
        font.family: root._singleFontFamily
        font.pixelSize: root._stablePixelSize
        font.weight: root._singleFontWeight
        font.letterSpacing: root.letterSpacing
    }

    layer.enabled: root.outlineWeight > 0
    layer.smooth: true
    layer.mipmap: true

    Item {
        id: segmentHost

        visible: root._useSplitFonts
        anchors.centerIn: parent
        width: segmentRow.width + root._actualOutlineWidth * 2
        height: segmentRow.height + root._actualOutlineWidth * 2

        Row {
            id: segmentRow

            x: root._actualOutlineWidth
            y: root._actualOutlineWidth
            spacing: 0

            property real baselineOffset: children.length > 0 ? children[0].baselineOffset : 0

            Repeater {
                model: root._textRuns

                Item {
                    id: segmentRoot

                    required property var modelData

                    readonly property string segmentText: modelData.text
                    readonly property bool segmentLatin: modelData.latin
                    readonly property string segmentFontFamily: {
                        void root._fontEpoch
                        return segmentLatin
                            ? Theme.latinFontFamily
                            : Theme.fontFamilyForText(segmentText)
                    }
                    readonly property int segmentFontWeight: segmentLatin ? Font.Normal : Font.Bold

                    width: segmentTextItem.implicitWidth
                    height: segmentTextItem.implicitHeight + root._actualOutlineWidth * 2

                    baselineOffset: segmentOutlineHost.y + segmentTextItem.baselineOffset

                    Item {
                        id: segmentOutlineHost

                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        width: segmentTextItem.implicitWidth
                        height: segmentTextItem.implicitHeight

                        Repeater {
                            model: root.outlineWeight > 0 ? root.outlineSamples : 0

                            Text {
                                readonly property real angle: (index / root.outlineSamples) * Math.PI * 2
                                x: Math.cos(angle) * root._actualOutlineWidth
                                y: Math.sin(angle) * root._actualOutlineWidth
                                text: segmentRoot.segmentText
                                font.family: segmentRoot.segmentFontFamily
                                font.pixelSize: root._stablePixelSize
                                font.weight: segmentRoot.segmentFontWeight
                                font.letterSpacing: root.letterSpacing
                                color: root.outlineColor
                            }
                        }

                        Text {
                            id: segmentTextItem

                            text: segmentRoot.segmentText
                            font.family: segmentRoot.segmentFontFamily
                            font.pixelSize: root._stablePixelSize
                            font.weight: segmentRoot.segmentFontWeight
                            font.letterSpacing: root.letterSpacing
                            color: root.fillColor
                        }
                    }
                }
            }
        }
    }

    Item {
        id: container

        visible: !root._useSplitFonts
        anchors.centerIn: root._wraps ? undefined : parent
        anchors.left: root._wraps ? parent.left : undefined
        anchors.top: root._wraps ? parent.top : undefined
        anchors.leftMargin: root._wraps ? root._actualOutlineWidth : 0
        anchors.topMargin: root._wraps ? root._actualOutlineWidth : 0
        width: root._textWidth
        height: mainText.implicitHeight

        Repeater {
            model: root.outlineWeight > 0 ? root.outlineSamples : 0

            Text {
                readonly property real angle: (index / root.outlineSamples) * Math.PI * 2
                x: Math.cos(angle) * root._actualOutlineWidth
                y: Math.sin(angle) * root._actualOutlineWidth

                width: root._textWidth
                wrapMode: root.wrapMode
                horizontalAlignment: root.horizontalAlignment
                textFormat: root._textFormat
                text: root._displayText
                font.family: root._singleFontFamily
                font.pixelSize: root._stablePixelSize
                font.weight: root._singleFontWeight
                font.letterSpacing: root.letterSpacing
                lineHeight: root._applyLineSpacing ? root._lineHeight : 1
                lineHeightMode: root._applyLineSpacing
                    ? Text.FixedHeight
                    : Text.ProportionalHeight
                color: root.outlineColor
            }
        }

        Text {
            id: mainText

            width: root._textWidth
            wrapMode: root.wrapMode
            horizontalAlignment: root.horizontalAlignment
            textFormat: root._textFormat
            text: root._displayText
            font.family: root._singleFontFamily
            font.pixelSize: root._stablePixelSize
            font.weight: root._singleFontWeight
            font.letterSpacing: root.letterSpacing
            lineHeight: root._applyLineSpacing ? root._lineHeight : 1
            lineHeightMode: root._applyLineSpacing
                ? Text.FixedHeight
                : Text.ProportionalHeight
            color: root.fillColor
        }
    }
}
