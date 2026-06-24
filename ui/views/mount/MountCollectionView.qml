import QtQuick
import ui 1.0

Item {
    id: root

    property var mountCollectionModel: null

    MountSlotGrid {
        anchors.fill: parent
        mountCollectionModel: root.mountCollectionModel
    }
}
