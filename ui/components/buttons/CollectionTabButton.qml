import QtQuick
import ui 1.0

Item {
    id: root

    property string locId: ""
    property string locTable: "General"
    property color activeColor: Theme.lightGrey
    property bool active: false
    property real scaleW: 4
    property real scaleH: 1

    signal clicked()

    readonly property real baseSize: 128
    readonly property real bakedWidth: baseSize * scaleW
    readonly property real bakedHeight: baseSize * scaleH
    readonly property real labelFontScale: 52 / 100

    readonly property real uniformScale: Math.min(
        width / bakedWidth,
        height / bakedHeight
    )

    implicitWidth: bakedWidth
    implicitHeight: bakedHeight

    Item {
        id: displayHost

        anchors.centerIn: parent
        width: root.bakedWidth * root.uniformScale
        height: root.bakedHeight * root.uniformScale

        Item {
            id: canvas

            width: root.bakedWidth
            height: root.bakedHeight
            transformOrigin: Item.TopLeft
            transform: Scale {
                xScale: displayHost.width / canvas.width
                yScale: displayHost.height / canvas.height
            }

            RectRoundButton {
                anchors.fill: parent
                scaleW: root.scaleW
                scaleH: root.scaleH
                fillColor: root.active ? root.activeColor : Theme.lightGrey
            }

            AppText {
                anchors.centerIn: parent
                locId: root.locId
                locTable: root.locTable
                pixelSize: canvas.height * root.labelFontScale
                fillColor: Theme.white
                outlineWeight: 6
            }

            MouseArea {
                anchors.fill: parent
                onClicked: root.clicked()
            }
        }
    }
}
