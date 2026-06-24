import QtQuick
import ui 1.0

Rectangle {
    id: root

    color: "#F8C8D4"

    AppText {
        anchors.centerIn: parent
        width: parent.width * 0.9
        text: "Forge"
        fillColor: Theme.darkText
        pixelSize: Math.max(18, parent.height * 0.04)
        outlineWeight: 0
    }
}
