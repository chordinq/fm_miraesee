import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root

    property real scaleW: 8.0
    property real scaleH: 8.0

    property color fillColor: "#FFFFFF"
    property real fillOpacity: 1.0

    readonly property real baseSize: 256

    implicitWidth: baseSize * scaleW
    implicitHeight: baseSize * scaleH

    readonly property real bakedW: 512 * scaleW
    readonly property real bakedH: 512 * scaleH

    Item {
        id: bakeCanvas
        width: root.bakedW
        height: root.bakedH
        transformOrigin: Item.TopLeft
        transform: Scale {
            xScale: root.width / root.bakedW
            yScale: root.height / root.bakedH
            origin.x: 0
            origin.y: 0
        }

        Item {
            anchors.fill: parent
            opacity: root.fillOpacity
            visible: root.fillColor !== "#00000000" && root.fillOpacity > 0

            BorderImage {
                id: bgMask
                anchors.fill: parent
                source: Qt.resolvedUrl("../../assets/sprites/UI/Button.png")
                border.left: 100
                border.top: 100
                border.right: 100
                border.bottom: 370
                smooth: true
                visible: false
            }

            BorderImage {
                id: bgBase
                anchors.fill: parent
                source: Qt.resolvedUrl("../../assets/sprites/UI/Button.png")
                border.left: 100
                border.top: 100
                border.right: 100
                border.bottom: 370
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
            }
        }
    }
}
