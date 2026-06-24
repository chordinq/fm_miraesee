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
    property int outlineSamples: 32

    property real letterSpacing: 0
    property int wrapMode: Text.NoWrap
    property int horizontalAlignment: Text.AlignLeft

    readonly property real _actualOutlineWidth: pixelSize * (outlineWeight / 100.0)
    readonly property bool _wraps: root.wrapMode !== Text.NoWrap

    readonly property string _coreText: locId !== ""
        ? LocManager.get_string(locId, Theme.language, locTable, formatArgs)
        : text

    readonly property string _resolvedText: prefix + _coreText + suffix

    readonly property string _dynamicFontFamily: {
        if (_resolvedText === "") return Theme.latinFontFamily
        var hasNonAscii = /[^\x00-\x7F]/.test(_resolvedText)
        return hasNonAscii ? Theme.uiFontFamily : Theme.latinFontFamily
    }

    readonly property bool _fontsReady: _dynamicFontFamily !== ""

    readonly property real _textWidth: root._wraps
        ? Math.max(0, root.width - root._actualOutlineWidth * 2)
        : mainText.implicitWidth

    implicitWidth: root._wraps
        ? root.width
        : mainText.implicitWidth + _actualOutlineWidth * 2
    implicitHeight: mainText.implicitHeight + _actualOutlineWidth * 2

    baselineOffset: container.y + mainText.baselineOffset

    layer.enabled: root.outlineWeight > 0 && root._fontsReady
    layer.smooth: false

    Item {
        id: container

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
                text: root._resolvedText
                font.family: root._dynamicFontFamily
                font.pixelSize: root.pixelSize
                font.letterSpacing: root.letterSpacing
                color: root.outlineColor
            }
        }

        Text {
            id: mainText

            width: root._textWidth
            wrapMode: root.wrapMode
            horizontalAlignment: root.horizontalAlignment
            text: root._resolvedText
            font.family: root._dynamicFontFamily
            font.pixelSize: root.pixelSize
            font.letterSpacing: root.letterSpacing
            color: root.fillColor
        }
    }
}
