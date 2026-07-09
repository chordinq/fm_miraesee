import QtQuick
import QtQuick.Effects
import ui 1.0

Item {
    id: root

    property real maskAspectW: 2
    property real maskAspectH: 2
    property real tileScale: 10
    property real nativeTileSize: 32
    property real baseDuration: 2500
    property real patternOpacity: 21 / 32

    readonly property real bakedW: 128 * maskAspectW
    readonly property real bakedH: 128 * maskAspectH
    readonly property real scaledTileSize: nativeTileSize * tileScale
    readonly property string patternImage: Qt.resolvedUrl("../../../assets/sprites/UI/MultiverseBackground.png")

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

            // 👉 1. 배경색
            Rectangle {
                anchors.fill: parent
                color: Theme.colorMultiverse
            }

            // 👉 2. 하얀색 오버레이 패턴
            Item {
                anchors.fill: parent
                opacity: root.patternOpacity 
                clip: false

                Item {
                    width: parent.width
                    height: parent.height + root.scaledTileSize
                    anchors.bottom: parent.bottom

                    Image {
                        width: parent.width / root.tileScale
                        height: parent.height / root.tileScale
                        source: root.patternImage
                        fillMode: Image.Tile
                        smooth: false
                        transformOrigin: Item.TopLeft
                        scale: root.tileScale
                    }

                    transform: Translate {
                        NumberAnimation on y {
                            from: 0
                            to: root.scaledTileSize
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

        // 👉 3. 최종 합성 (투명도 없이 렌더링)
        MultiEffect {
            anchors.fill: parent
            source: contentHost
            maskEnabled: true
            maskSource: maskShape
        }
    }
}