import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
    id: root

    property real maskAspectW: 4.0
    property real maskAspectH: 4.0
    property real tileScale: 4.0
    property real nativeTileSize: 256
    property real baseDuration: 7500
    property real patternOpacity: 21 / 32

    readonly property real bakedW: 128 * maskAspectW
    readonly property real bakedH: 128 * maskAspectH
    readonly property real scaledTileSize: nativeTileSize * tileScale
    readonly property string patternImage: Qt.resolvedUrl("../../../assets/sprites/UI/InterstellarBackground.png")

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
            id: contentHost
            anchors.fill: parent
            visible: false
            layer.enabled: true

            // 👉 1. 배경색: 투명도 없이 100% 본연의 색상으로 꽉 채웁니다.
            Rectangle {
                anchors.fill: parent
                color: Theme.colorInterstellar
            }

            // 👉 2. 하얀색 오버레이 패턴: 투명도를 오직 여기에만 적용합니다!
            Item {
                anchors.fill: parent
                // (참고: 만약 별이 반투명하지 않고 100% 쨍한 순백색이길 원하시면 
                // 아래 opacity 줄을 아예 삭제하시면 됩니다.)
                opacity: root.patternOpacity 
                clip: false

                Item {
                    width: parent.width + root.scaledTileSize
                    height: parent.height + root.scaledTileSize
                    anchors.right: parent.right
                    anchors.top: parent.top

                    Image {
                        width: parent.width / root.tileScale
                        height: parent.height / root.tileScale
                        source: root.patternImage
                        fillMode: Image.Tile
                        smooth: true
                        transformOrigin: Item.TopLeft
                        scale: root.tileScale
                    }

                    transform: Translate {
                        NumberAnimation on x {
                            from: 0
                            to: root.scaledTileSize
                            duration: root.baseDuration * root.tileScale
                            loops: Animation.Infinite
                        }
                        NumberAnimation on y {
                            from: 0
                            to: -root.scaledTileSize
                            duration: root.baseDuration * root.tileScale
                            loops: Animation.Infinite
                        }
                    }
                }
            }
        }

        RectRounded {
            id: maskShape
            anchors.fill: parent
            aspectW: root.maskAspectW
            aspectH: root.maskAspectH
		cornerRatioW: 255 / (512 * (root.maskAspectW))
		cornerRatioH: 255 / (512 * (root.maskAspectH))
            fillColor: Theme.white
            visible: false
            layer.enabled: true
        }

        // 👉 3. 최종 합성: 이제 MultiEffect에는 opacity를 주지 않아 100% 선명하게 렌더링됩니다.
        MultiEffect {
            anchors.fill: parent
            source: contentHost
            maskEnabled: true
            maskSource: maskShape
        }
    }
}