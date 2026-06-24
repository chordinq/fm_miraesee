import QtQuick
import ui 1.0

Item {
    id: root

    property var techTreeModel: null

    TechTree {
        anchors.fill: parent
        techTreeModel: root.techTreeModel
    }
}
