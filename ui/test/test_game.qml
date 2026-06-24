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

    readonly property real section1WidthRatio: 1 / 3
    readonly property real sectionRightWidthRatio: 2 / 3
    readonly property real topBarHeightRatio: 1 / 15
    readonly property real tabBarWidthRatio: 4 / 5

    property int activeTabIndex: 0

    Component.onCompleted: {
        Theme.language = uiLanguage
    }

    Row {
        anchors.fill: parent
        spacing: 0

        Item {
            id: section1

            width: parent.width * window.section1WidthRatio
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

        Item {
            id: sectionRight

            width: parent.width * window.sectionRightWidthRatio
            height: parent.height

            Item {
                id: topBar

                width: parent.width
                height: parent.height * window.topBarHeightRatio

                Row {
                    id: tabRow

                    width: parent.width * window.tabBarWidthRatio
                    height: parent.height
                    spacing: 0

                    Repeater {
                        model: [
                            { label: "3", title: "Forge", color: Theme.darkGrey },
                            { label: "4", title: "Skill", color: Theme.lightGreen },
                            { label: "5", title: "Pet", color: Theme.lightBlue },
                            { label: "6", title: "Mount", color: Theme.orange },
                            { label: "7", title: "Tech", color: Theme.red }
                        ]

                        delegate: Item {
                            id: tabButton

                            required property var modelData
                            required property int index

                            width: tabRow.width / 5
                            height: tabRow.height

                            readonly property bool isActive: window.activeTabIndex === index

                            RectRoundButton {
                                anchors.fill: parent
                                anchors.margins: 2
                                scaleW: 2
                                scaleH: 1
                                fillColor: tabButton.isActive
                                    ? tabButton.modelData.color
                                    : Theme.lightGrey
                            }

                            AppText {
                                anchors.centerIn: parent
                                text: tabButton.modelData.label
                                pixelSize: Math.max(14, parent.height * 0.35)
                                fillColor: Theme.white
                                outlineWeight: 6
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: window.activeTabIndex = tabButton.index
                            }
                        }
                    }
                }

                Item {
                    x: tabRow.width
                    width: parent.width - tabRow.width
                    height: parent.height

                    Rectangle {
                        anchors.fill: parent
                        color: Theme.darkGrey
                    }

                    AppText {
                        anchors.centerIn: parent
                        text: "\u2699"
                        pixelSize: Math.max(16, parent.height * 0.45)
                        fillColor: Theme.white
                        outlineWeight: 0
                    }

                    MouseArea {
                        anchors.fill: parent
                    }
                }
            }

            Item {
                id: mainHost

                width: parent.width
                y: topBar.height
                height: parent.height - topBar.height

                property bool forgeReady: false
                property bool skillReady: false
                property bool petReady: false
                property bool mountReady: false
                property bool techReady: false

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 0 || mainHost.forgeReady
                    visible: window.activeTabIndex === 0
                    z: window.activeTabIndex === 0 ? 1 : 0
                    sourceComponent: forgeMainComponent
                    onLoaded: mainHost.forgeReady = true
                }

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 1 || mainHost.skillReady
                    visible: window.activeTabIndex === 1
                    z: window.activeTabIndex === 1 ? 1 : 0
                    sourceComponent: skillMainComponent
                    onLoaded: mainHost.skillReady = true
                }

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 2 || mainHost.petReady
                    visible: window.activeTabIndex === 2
                    z: window.activeTabIndex === 2 ? 1 : 0
                    sourceComponent: petMainComponent
                    onLoaded: mainHost.petReady = true
                }

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 3 || mainHost.mountReady
                    visible: window.activeTabIndex === 3
                    z: window.activeTabIndex === 3 ? 1 : 0
                    sourceComponent: mountMainComponent
                    onLoaded: mainHost.mountReady = true
                }

                Loader {
                    anchors.fill: parent
                    active: window.activeTabIndex === 4 || mainHost.techReady
                    visible: window.activeTabIndex === 4
                    z: window.activeTabIndex === 4 ? 1 : 0
                    sourceComponent: techMainComponent
                    onLoaded: mainHost.techReady = true
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

    Component {
        id: forgeMainComponent

        ForgeMainView {
            anchors.fill: parent
        }
    }

    Component {
        id: skillMainComponent

        SkillMainView {
            anchors.fill: parent
            skillSummonTest: gameTest
        }
    }

    Component {
        id: petMainComponent

        PetMainView {
            anchors.fill: parent
            eggHatchTest: gamePetEggTest
        }
    }

    Component {
        id: mountMainComponent

        MountMainView {
            anchors.fill: parent
        }
    }

    Component {
        id: techMainComponent

        TechMainView {
            anchors.fill: parent
        }
    }
}
