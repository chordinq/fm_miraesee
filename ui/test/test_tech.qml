pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
    id: window

    width: initWinWidth
    height: initWinHeight
    visible: true
    title: "TechTree test (Forge / Power / SkillsPetTech)"
    color: Theme.white

    readonly property int headerLabelSize: Math.max(16, Math.round(Math.min(width, height) * 0.028))
    readonly property int columnSpacing: Math.max(8, Math.round(width * 0.01))
    readonly property int outerMargin: Math.max(8, Math.round(Math.min(width, height) * 0.015))

    Component.onCompleted: {
        Theme.language = uiLanguage
    }

    Row {
        id: treeRow

        anchors.fill: parent
        anchors.margins: window.outerMargin
        spacing: window.columnSpacing

        Repeater {
            model: [
                { title: "Forge", model: testTechTreeForge },
                { title: "Power", model: testTechTreePower },
                { title: "SkillsPetTech", model: testTechTreeSkillsPetTech }
            ]

            delegate: Item {
                id: treeColumn

                required property var modelData

                readonly property var techTreeModel: modelData.model
                readonly property string treeTitle: modelData.title

                width: (treeRow.width - 2 * window.columnSpacing) / 3
                height: treeRow.height

                Rectangle {
                    anchors.fill: parent
                    color: Theme.white
                    border.color: Theme.darkGrey
                    border.width: 1
                    radius: 6
                }

                AppText {
                    id: columnTitle

                    anchors.top: parent.top
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.topMargin: parent.height * 0.012
                    width: parent.width * 0.92
                    text: treeColumn.treeTitle
                    fillColor: Theme.darkText
                    pixelSize: window.headerLabelSize
                    outlineWeight: 8
                }

                AppText {
                    id: columnProgress

                    anchors.top: columnTitle.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.topMargin: parent.height * 0.008
                    width: parent.width * 0.92
                    text: Math.round(treeColumn.techTreeModel.progress * 1000) / 10 + "% · "
                        + treeColumn.techTreeModel.nodeCount + " nodes · "
                        + "L0-" + treeColumn.techTreeModel.maxLayer
                    fillColor: Theme.darkText
                    pixelSize: Math.max(12, window.headerLabelSize - 4)
                    outlineWeight: 6
                }

                TechTree {
                    anchors.top: columnProgress.bottom
                    anchors.topMargin: parent.height * 0.012
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: parent.width * 0.02
                    anchors.rightMargin: parent.width * 0.02
                    anchors.bottomMargin: parent.height * 0.012
                    techTreeModel: treeColumn.techTreeModel
                    iconSizeRatio: 0.16
                }
            }
        }
    }
}