import QtQuick
import ui 1.0

Item {
    id: root

    property var skillCollectionModel: null

    SkillGrid {
        anchors.fill: parent
        skillCollectionModel: root.skillCollectionModel
    }
}
