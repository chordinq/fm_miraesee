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
    property bool settingsOpen: false
    property bool languageOpen: false
    property int tabLoadMask: 1

    function tabIsLoaded(index) {
        return (tabLoadMask & (1 << index)) !== 0
    }

    function markTabLoaded(index) {
        if (!tabIsLoaded(index))
            tabLoadMask = tabLoadMask | (1 << index)
    }

    function selectTab(index) {
        markTabLoaded(index)
        activeTabIndex = index
    }

    Component.onCompleted: {
        Theme.language = uiLanguage
        gamePetEggTest.setUiLanguage(Theme.language)
        tabPreloadStartTimer.start()
    }

    Timer {
        id: tabPreloadStartTimer
        interval: 100
        repeat: false
        onTriggered: tabPreloadTimer.start()
    }

    Timer {
        id: tabPreloadTimer
        interval: 150
        repeat: true
        property int nextIndex: 1
        onTriggered: {
            if (nextIndex >= 5) {
                stop()
                return
            }
            window.markTabLoaded(nextIndex)
            nextIndex++
        }
    }

    Connections {
        target: Theme
        function onLanguageChanged() {
            gamePetEggTest.setUiLanguage(Theme.language)
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#80000000"
        visible: window.settingsOpen
        z: 100

        MouseArea {
            anchors.fill: parent
        }
    }

    SettingsView {
        visible: window.settingsOpen
        anchors.centerIn: parent
        z: 101
        onClosed: {
            window.settingsOpen = false
            window.languageOpen = false
        }
        onLanguagesClicked: window.languageOpen = true
    }

    LanguageSettingsView {
        visible: window.settingsOpen && window.languageOpen
        anchors.centerIn: parent
        z: 102
        onClosed: window.languageOpen = false
    }

    Row {
        anchors.fill: parent
        spacing: 0

        SidePanel {
            width: parent.width * window.sidePanelWidthRatio
            height: parent.height
            activeTabIndex: window.activeTabIndex
            onTabClicked: function(index) { window.selectTab(index) }
            onSettingsClicked: window.settingsOpen = true
            onLoadDumpClicked: gameSession.loadDumpFromClipboard()
        }

        Item {
            id: centerPanel

            width: parent.width * window.centerWidthRatio
            height: parent.height

            Rectangle {
                anchors.fill: parent
                color: Qt.darker(Theme.darkBlue, 1.5)
                visible: window.activeTabIndex !== 1
                    && window.activeTabIndex !== 2
                    && window.activeTabIndex !== 3
                    && window.activeTabIndex !== 4
            }

            Loader {
                anchors.fill: parent
                active: window.tabIsLoaded(4)
                visible: window.activeTabIndex === 4
                sourceComponent: techMainComponent
            }

            Loader {
                anchors.fill: parent
                active: window.tabIsLoaded(1)
                visible: window.activeTabIndex === 1
                sourceComponent: skillMainComponent
            }

            Loader {
                anchors.fill: parent
                active: window.tabIsLoaded(2)
                visible: window.activeTabIndex === 2
                sourceComponent: petMainComponent
            }

            Loader {
                anchors.fill: parent
                active: window.tabIsLoaded(3)
                visible: window.activeTabIndex === 3
                sourceComponent: mountMainComponent
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

                Loader {
                    anchors.fill: parent
                    active: window.tabIsLoaded(0)
                    visible: window.activeTabIndex === 0
                    z: window.activeTabIndex === 0 ? 1 : 0
                    sourceComponent: forgeCollectionComponent
                }

                Loader {
                    anchors.fill: parent
                    active: window.tabIsLoaded(1)
                    visible: window.activeTabIndex === 1
                    z: window.activeTabIndex === 1 ? 1 : 0
                    sourceComponent: skillCollectionComponent
                }

                Loader {
                    anchors.fill: parent
                    active: window.tabIsLoaded(2)
                    visible: window.activeTabIndex === 2
                    z: window.activeTabIndex === 2 ? 1 : 0
                    sourceComponent: petCollectionComponent
                }

                Loader {
                    anchors.fill: parent
                    active: window.tabIsLoaded(3)
                    visible: window.activeTabIndex === 3
                    z: window.activeTabIndex === 3 ? 1 : 0
                    sourceComponent: mountCollectionComponent
                }

                Loader {
                    anchors.fill: parent
                    active: window.tabIsLoaded(4)
                    visible: window.activeTabIndex === 4
                    z: window.activeTabIndex === 4 ? 1 : 0
                    sourceComponent: techCollectionComponent
                }
            }
        }
    }

    Component {
        id: skillMainComponent

        SkillMainView {
            anchors.fill: parent
            skillController: gameTest
            summonResultWidthRatio: 0.25
        }
    }

    Component {
        id: petMainComponent

        PetMainView {
            anchors.fill: parent
            petController: gamePetSummonTest
            petCollectionModel: gamePetCollection
            summonResultWidthRatio: 0.25
        }
    }

    Component {
        id: mountMainComponent

        MountMainView {
            anchors.fill: parent
            mountController: gameMountSummonTest
            mountCollectionModel: gameMountCollection
            summonResultWidthRatio: 0.25
        }
    }

    Component {
        id: techMainComponent

        TechMainView {
            anchors.fill: parent
            gameSession: gameSession
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
            skillController: gameTest
        }
    }

    Component {
        id: petCollectionComponent

        PetCollectionView {
            anchors.fill: parent
            petCollectionModel: gamePetCollection
            petController: gamePetSummonTest
            eggController: gamePetEggTest
        }
    }

    Component {
        id: mountCollectionComponent

        MountCollectionView {
            anchors.fill: parent
            mountCollectionModel: gameMountCollection
            mountController: gameMountSummonTest
        }
    }

    Component {
        id: techCollectionComponent

        TechCollectionView {
            anchors.fill: parent
            techTreeForgeModel: gameTechTreeForge
            techTreePowerModel: gameTechTreePower
            techTreeSkillsPetTechModel: gameTechTreeSkillsPetTech
        }
    }
}
