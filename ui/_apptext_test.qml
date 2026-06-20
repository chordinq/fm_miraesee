import QtQuick
import ui 1.0

Window {
    width: 400; height: 200; visible: true
    title: "AppText test"

    Column {
        anchors.centerIn: parent
        spacing: 12

        AppText {
            segments: [{ text: "Lv. 10" }]
            pixelSize: 28
            fillColor: "black"
            outlineWeight: 0
        }

        AppText {
            segments: [{ locId: "4980716816252928" }]
            pixelSize: 28
            fillColor: "black"
            outlineWeight: 0
            locLetterSpacing: 4
        }
    }

    Component.onCompleted: Theme.language = "ko"
}
