import QtQuick
import ui 1.0

Window {
    width: 400; height: 200; visible: true
    title: "AppText test"

    Column {
        anchors.centerIn: parent
        spacing: 12

        AppText {
            pixelSize: 28
            fillColor: "black"
            outlineWeight: 0
            prefix: "Lv. 10"
        }

        AppText {
            pixelSize: 28
            fillColor: "black"
            outlineWeight: 0
            useUiFont: true
            locId: "4980716816252928"
            locTable: "General"
        }
    }

    Component.onCompleted: Theme.language = "ko"
}
