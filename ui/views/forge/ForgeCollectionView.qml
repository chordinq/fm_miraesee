import QtQuick
import ui 1.0

Item {
    id: root

    property var equipmentCollectionModel: null

    EquipmentGrid {
        anchors.fill: parent
        equipmentCollectionModel: root.equipmentCollectionModel
    }
}
