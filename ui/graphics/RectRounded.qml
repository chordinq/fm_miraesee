import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
    id: root

    property real scaleW: 1.0
    property real scaleH: 1.0

    property color fillColor: Theme.white
    property real fillOpacity: 1.0

    readonly property real baseSize: 256

    implicitWidth: baseSize * scaleW
    implicitHeight: baseSize * scaleH

    // 🌟 작성자님의 완벽한 수학 공식 원상 복구!
    readonly property real bakedW: 512 * scaleW
    readonly property real bakedH: 512 * scaleH

    Item {
        anchors.fill: parent
        opacity: root.fillOpacity
        visible: root.fillColor.a > 0 && root.fillOpacity > 0

        // 🌟 GPU 구원자 컨테이너: 최종 스크린 사이즈(예: 5120x1024)를 가집니다.
        Item {
            id: effectSource
            anchors.fill: parent
            visible: false // MultiEffect의 재료로 쓸 거니까 숨깁니다.

            BorderImage {
                // 내부는 10240x2048 사이즈로 계산하지만...
                width: root.bakedW
                height: root.bakedH
                transformOrigin: Item.TopLeft
                // 🌟 수학적으로 먼저 0.5배 축소를 걸어버립니다!
                transform: Scale {
                    xScale: root.width / root.bakedW
                    yScale: root.height / root.bakedH
                }
                source: Qt.resolvedUrl("../../assets/sprites/UI/Rect_Rounded_Filled.png")
                border.left: 255
                border.top: 255
                border.right: 255
                border.bottom: 255
                smooth: true
                // ❌ 치명적이었던 layer.enabled: true 완전 삭제!
            }
        }

        // 🌟 이펙트는 이미 0.5배로 줄어든 effectSource(5120x1024)를 기반으로 작동하므로
        // 16384 텍스처 제한에 절대 걸리지 않습니다!
        MultiEffect {
            anchors.fill: effectSource
            source: effectSource
            colorization: 1.0
            colorizationColor: root.fillColor
        }
    }
}