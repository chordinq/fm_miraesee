import QtQuick
import ui 1.0

Item {
    id: root

    property var petCollectionModel: null
    property var eggHatchTest: null

    EggHatchPanel {
        id: hatchPanel

        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        petCollectionModel: root.petCollectionModel
        eggHatchTest: root.eggHatchTest
    }

    PetSlotGrid {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: hatchPanel.top
        petCollectionModel: root.petCollectionModel
        eggHatchTest: root.eggHatchTest
    }
}
