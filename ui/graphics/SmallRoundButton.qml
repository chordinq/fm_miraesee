import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root

    property color fillColor: "#FFFFFF"
    property real fillOpacity: 1.0

    readonly property int sourceNativeSize: 256

    implicitWidth: sourceNativeSize
    implicitHeight: sourceNativeSize

    Image {
        id: bgMask
        anchors.fill: parent
        source: Qt.resolvedUrl("../../assets/sprites/UI/SmallRoundButton.png")
        sourceSize: Qt.size(root.sourceNativeSize, root.sourceNativeSize)
        fillMode: Image.Stretch
        smooth: true
        visible: false
    }

    Image {
        id: bgBase
        anchors.fill: parent
        source: Qt.resolvedUrl("../../assets/sprites/UI/SmallRoundButton.png")
        sourceSize: Qt.size(root.sourceNativeSize, root.sourceNativeSize)
        fillMode: Image.Stretch
        smooth: true
        opacity: 0
        layer.enabled: true
        layer.smooth: true
    }

    ColorOverlay {
        id: fillTint
        anchors.fill: bgBase
        source: bgBase
        color: root.fillColor
        opacity: 0
        layer.enabled: true
        layer.smooth: true
    }

    Blend {
        id: tintedBlend
        anchors.fill: parent
        source: bgBase
        foregroundSource: fillTint
        mode: "multiply"
        opacity: 0
        layer.enabled: true
        layer.smooth: true
    }

    OpacityMask {
        anchors.fill: parent
        source: tintedBlend
        maskSource: bgMask
        opacity: root.fillOpacity
        visible: root.fillColor !== "#00000000" && root.fillOpacity > 0
    }
}
