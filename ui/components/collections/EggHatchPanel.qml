import QtQuick
import ui 1.0

Rectangle {
    id: root

    property var petCollectionModel: null
    property var eggHatchTest: null

    readonly property int ascensionLevel: petCollectionModel ? petCollectionModel.ascensionLevel : 0
    readonly property int slotCount: petCollectionModel ? petCollectionModel.hatchSlotCount : 0
    readonly property var eggModels: petCollectionModel ? petCollectionModel.hatchEggModels : []

    implicitWidth: 1200
    height: width * (5 / 12)

    readonly property real slotWidth: width * 0.235
    readonly property real slotSpacing: slotWidth * -0.12

    color: Qt.lighter(Theme.darkBlue, 2.22)

    Column {
        anchors.fill: parent

        Rectangle { width: parent.width; height: root.height * 0.01; color: Theme.black }
        Rectangle { width: parent.width; height: root.height * 0.03; color: Qt.darker(Theme.darkBlue, 2) }
        Rectangle { width: parent.width; height: root.height * 0.01; color: Theme.black }
        Rectangle { width: parent.width; height: root.height * 0.02; color: Theme.darkBlue }
        Rectangle { width: parent.width; height: root.height * 0.01; color: Theme.black }

        Rectangle {
            width: parent.width
            height: root.height * 0.88
            color: "transparent"

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: slotWidth * -0.14
                spacing: root.slotSpacing

                Repeater {
                    model: root.slotCount

                    EggHatchSlot {
                        required property int index

                        anchors.top: parent.top
                        eggModel: root.eggModels[index]
                        ascensionLevel: root.ascensionLevel
                        width: root.slotWidth
                        onClicked: {
                            if (root.eggHatchTest && eggModel)
                                root.eggHatchTest.predictHatch(eggModel.guid)
                        }
                    }
                }
            }
        }

		Rectangle { width: parent.width; height: root.height * 0.02; color: Theme.darkBlue }
		Rectangle { width: parent.width; height: root.height * 0.02; color: Theme.black }
    }
}