import QtQuick
import ui 1.0

Item {
    id: root

    // 🌟 입력값은 깔끔하게 locId 또는 text 둘 중 하나만 받습니다.
    property string locId: ""
    property string locTable: "General"
    property var formatArgs: []
    property string text: ""

    property real pixelSize: 24
    property color fillColor: Theme.white
    property int outlineWeight: 4
    property color outlineColor: Theme.black
    property int outlineSamples: 32

    // 🌟 스마트 자간: 다국어(locId)가 들어오면 4, 일반 텍스트가 들어오면 0으로 자동 세팅!
    property real letterSpacing: locId !== "" ? 4 : 0

    readonly property real _actualOutlineWidth: pixelSize * (outlineWeight / 100.0)

    // 🌟 배열 루프 없이, 단일 텍스트 처리 (다국어 우선)
    readonly property string _resolvedText: {
        if (locId !== "") return LocManager.get_string(locId, Theme.language, locTable, formatArgs)
        return root.text.toString()
    }

    // 🌟 폰트 자동 감지 (단 한 번만 계산)
    readonly property string _dynamicFontFamily: {
        if (_resolvedText === "") return Theme.latinFontFamily
        var hasNonAscii = /[^\x00-\x7F]/.test(_resolvedText)
        return hasNonAscii ? Theme.uiFontFamily : Theme.latinFontFamily
    }

    readonly property bool _fontsReady: _dynamicFontFamily !== ""

    implicitWidth: mainText.implicitWidth + _actualOutlineWidth * 2
    implicitHeight: mainText.implicitHeight + _actualOutlineWidth * 2

    layer.enabled: root.outlineWeight > 0 && root._fontsReady
    layer.smooth: false

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
                
                text: root._resolvedText
                font.family: root._dynamicFontFamily
                font.pixelSize: root.pixelSize
                font.letterSpacing: root.letterSpacing
                color: root.outlineColor
            }
        }

        Text {
            id: mainText
            text: root._resolvedText
            font.family: root._dynamicFontFamily
            font.pixelSize: root.pixelSize
            font.letterSpacing: root.letterSpacing
            color: root.fillColor
        }
    }
}