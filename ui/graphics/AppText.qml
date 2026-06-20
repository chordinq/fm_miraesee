import QtQuick
import ui 1.0

Item {
    id: root

    property var segments: []
    property string defaultLocTable: "General"

    property real locLetterSpacing: 4
    property real rawLetterSpacing: 0
    property real segmentSpacing: pixelSize * 0.2

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

    implicitWidth: container.width + _actualOutlineWidth * 2
    implicitHeight: container.height + _actualOutlineWidth * 2

    layer.smooth: false

    function updateText() {
        var temp = []
        for (var i = 0; i < segments.length; i++) {
            var seg = segments[i]

            // 🌟 방어 로직 1: locId가 있으면 먼저 다국어로 처리해서 넣습니다.
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
            
            // 🌟 방어 로직 2: 'else if'가 아니라 그냥 'if'로 변경!
            // 사용자가 {locId: "...", text: "..."} 로 한 번에 넘겨도 알아서 분리해 냅니다.
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

            Row {
                readonly property real angle: (index / root.outlineSamples) * Math.PI * 2
                x: Math.cos(angle) * root._actualOutlineWidth
                y: Math.sin(angle) * root._actualOutlineWidth
                
                // 🌟 버그 해결 1: length 조건문을 삭제하고 무조건 spacing 값을 참조하게 강제합니다!
                spacing: root.segmentSpacing
                height: mainRow.height

                Repeater {
                    model: root._resolvedSegments

                    Text {
                        text: modelData.text
                        font.family: modelData.fontFamily
                        font.pixelSize: root.pixelSize
                        font.letterSpacing: modelData.spacing
                        color: root.outlineColor
                        verticalAlignment: Text.AlignVCenter
                        height: parent.height
                    }
                }
            }
        }

        Row {
            id: mainRow
            
            // 🌟 버그 해결 2: 메인 텍스트 영역도 무조건 spacing 적용
            spacing: root.segmentSpacing

            Repeater {
                model: root._resolvedSegments

                Text {
                    text: modelData.text
                    font.family: modelData.fontFamily
                    font.pixelSize: root.pixelSize
                    font.letterSpacing: modelData.spacing
                    color: root.fillColor
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }
}