import QtQuick
import QtQuick.Layouts
import ui 1.0

Item {
    id: root

    property var segments: []
    property string defaultLocTable: "General"

    property real locLetterSpacing: 4
    property real rawLetterSpacing: 0
    property real segmentSpacing: pixelSize * 0.15

    property real pixelSize: 24
    property color fillColor: Theme.white
    property int outlineWeight: 4
    property color outlineColor: Theme.black
    property int outlineSamples: 32

    readonly property real _actualOutlineWidth: pixelSize * (outlineWeight / 100.0)

    property var _resolvedSegments: []

    readonly property bool _fontsReady: {
        if (_resolvedSegments.length === 0)
            return false
        for (var i = 0; i < _resolvedSegments.length; i++) {
            if (!_resolvedSegments[i].fontFamily)
                return false
        }
        return true
    }

    // 🌟 safePadding 제거: 순수하게 아웃라인 두께만큼만 더해줍니다.
    implicitWidth: container.width + _actualOutlineWidth * 2
    implicitHeight: container.height + _actualOutlineWidth * 2

    layer.smooth: false

    function updateText() {
        var temp = []
        for (var i = 0; i < segments.length; i++) {
            var seg = segments[i]

            if (seg.locId) {
                var table = seg.table || root.defaultLocTable
                var args = seg.args || []
                var resolvedLoc = LocManager.get_string(seg.locId, Theme.language, table, args)

                if (resolvedLoc !== "") {
                    var hasNonAsciiLoc = /[^\x00-\x7F]/.test(resolvedLoc)
                    temp.push({
                        text: resolvedLoc,
                        fontFamily: hasNonAsciiLoc ? Theme.uiFontFamily : Theme.latinFontFamily,
                        spacing: root.locLetterSpacing
                    })
                }
            }

            if (seg.text !== undefined) {
                var resolvedRaw = seg.text.toString()

                if (resolvedRaw !== "") {
                    var hasNonAsciiRaw = /[^\x00-\x7F]/.test(resolvedRaw)
                    temp.push({
                        text: resolvedRaw,
                        fontFamily: hasNonAsciiRaw ? Theme.uiFontFamily : Theme.latinFontFamily,
                        spacing: root.rawLetterSpacing
                    })
                }
            }
        }
        _resolvedSegments = temp
        syncLayer()
    }

    function syncLayer() {
        root.layer.enabled = false
        if (root.outlineWeight <= 0 || !root._fontsReady)
            return
        Qt.callLater(function() {
            if (root.outlineWeight > 0 && root._fontsReady)
                root.layer.enabled = true
        })
    }

    onSegmentsChanged: updateText()
    onOutlineWeightChanged: syncLayer()
    onLocLetterSpacingChanged: updateText()
    onRawLetterSpacingChanged: updateText()

    Connections {
        target: Theme
        function onLanguageChanged() { root.updateText() }
        function onFontsChanged() { root.updateText() }
    }

    Component.onCompleted: updateText()

    Item {
        id: container
        anchors.centerIn: parent
        width: mainRow.implicitWidth
        height: mainRow.implicitHeight

        Repeater {
            model: root.outlineWeight > 0 ? root.outlineSamples : 0

            RowLayout {
                readonly property real angle: (index / root.outlineSamples) * Math.PI * 2
                x: Math.cos(angle) * root._actualOutlineWidth
                y: Math.sin(angle) * root._actualOutlineWidth
                spacing: root.segmentSpacing

                Repeater {
                    model: root._resolvedSegments

                    Text {
                        text: modelData.text
                        font.family: modelData.fontFamily
                        font.pixelSize: root.pixelSize
                        font.letterSpacing: modelData.spacing
                        color: root.outlineColor
                        Layout.alignment: Qt.AlignBaseline
                    }
                }
            }
        }

        RowLayout {
            id: mainRow
            spacing: root.segmentSpacing

            Repeater {
                model: root._resolvedSegments

                Text {
                    text: modelData.text
                    font.family: modelData.fontFamily
                    font.pixelSize: root.pixelSize
                    font.letterSpacing: modelData.spacing
                    color: root.fillColor
                    Layout.alignment: Qt.AlignBaseline
                }
            }
        }
    }
}