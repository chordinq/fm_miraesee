pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
    id: window

    width: initWinWidth
    height: initWinHeight
    visible: true
    title: "Game shell test"
    color: Theme.white

    readonly property real sidePanelWidthRatio: 1 / 8
    readonly property real collectionWidthRatio: 5 / 16
    readonly property real centerWidthRatio:
        1 - sidePanelWidthRatio - collectionWidthRatio

    property int activeTabIndex: 0

    Component.onCompleted: {
        Theme.language = uiLanguage
    }

    Row {
        anchors.fill: parent
        spacing: 0

        Item {
            id: sidePanel

            width: parent.width * window.sidePanelWidthRatio
            height: parent.height

            Rectangle {
                anchors.fill: parent
                color: Theme.darkGrey
            }

            Column {
                id: sideTabColumn

                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: Math.max(4, sidePanel.width * 0.06)
                height: parent.height * 0.3

                Repeater {
                    model: [
                        { locId: "12856879411200", locTable: "Forge", color: Theme.darkGrey },
                        { locId: "2109395617640448", locTable: "Stats", color: Theme.lightGreen },
                        { locId: "2110564712771584", locTable: "Stats", color: Theme.lightBlue },
                        { locId: "990866679984128", locTable: "Stats", color: Theme.orange },
                        { locId: "280318681088", locTable: "TechTree", color: Theme.red }
                    ]

                    delegate: CollectionTabButton {
                        required property var modelData
                        required property int index

                        width: sideTabColumn.width
                        height: sideTabColumn.height / 5

                        locId: modelData.locId
                        locTable: modelData.locTable
                        activeColor: modelData.color
                        active: window.activeTabIndex === index
                        onClicked: window.activeTabIndex = index
                    }
                }
            }
        }

        Item {
            id: centerPanel

            width: parent.width * window.centerWidthRatio
            height: parent.height

            Rectangle {
                anchors.fill: parent
                color: Qt.darker(Theme.darkBlue, 1.5)
            }
        }

        Item {
            id: collectionPanel

            width: parent.width * window.collectionWidthRatio
            height: parent.height

            Rectangle {
                anchors.fill: parent
                color: Theme.white
            }

            Item {
                id: collectionHost

                anchors.fill: parent
                anchors.margins: 8

                property bool forgeReady: false
                property bool skillReady: false
                property bool petReady: false
                property bool mountReady: false
                property bool techReady: false

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 0 || collectionHost.forgeReady
                    visible: window.activeTabIndex === 0
                    z: window.activeTabIndex === 0 ? 1 : 0
                    sourceComponent: forgeCollectionComponent
                    onLoaded: collectionHost.forgeReady = true
                }

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 1 || collectionHost.skillReady
                    visible: window.activeTabIndex === 1
                    z: window.activeTabIndex === 1 ? 1 : 0
                    sourceComponent: skillCollectionComponent
                    onLoaded: collectionHost.skillReady = true
                }

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 2 || collectionHost.petReady
                    visible: window.activeTabIndex === 2
                    z: window.activeTabIndex === 2 ? 1 : 0
                    sourceComponent: petCollectionComponent
                    onLoaded: collectionHost.petReady = true
                }

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 3 || collectionHost.mountReady
                    visible: window.activeTabIndex === 3
                    z: window.activeTabIndex === 3 ? 1 : 0
                    sourceComponent: mountCollectionComponent
                    onLoaded: collectionHost.mountReady = true
                }

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 4 || collectionHost.techReady
                    visible: window.activeTabIndex === 4
                    z: window.activeTabIndex === 4 ? 1 : 0
                    sourceComponent: techCollectionComponent
                    onLoaded: collectionHost.techReady = true
                }
            }
        }
    }

    Component {
        id: forgeCollectionComponent

        ForgeCollectionView {
            anchors.fill: parent
            equipmentCollectionModel: gameEquipmentCollection
        }
    }

    Component {
        id: skillCollectionComponent

        SkillCollectionView {
            anchors.fill: parent
            skillCollectionModel: gameTest.skillCollection
        }
    }

    Component {
        id: petCollectionComponent

        PetCollectionView {
            anchors.fill: parent
            petCollectionModel: gamePetCollection
            eggHatchTest: gamePetEggTest
        }
    }

    Component {
        id: mountCollectionComponent

        MountCollectionView {
            anchors.fill: parent
            mountCollectionModel: gameMountCollection
        }
    }

    Component {
        id: techCollectionComponent

        TechCollectionView {
            anchors.fill: parent
            techTreeModel: gameTechTree
        }
    }
}
