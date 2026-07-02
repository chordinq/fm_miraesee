pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
    id: window

    width: initWinWidth
    height: initWinHeight
    x: mainWinX
    y: mainWinY
    visible: true
    title: "Miraesee"
    color: Theme.white

    readonly property real sidePanelWidthRatio: 1 / 8
    readonly property real collectionWidthRatio: 5 / 16
    readonly property real centerWidthRatio:
        1 - sidePanelWidthRatio - collectionWidthRatio

    property int activeTabIndex: 0
    property bool settingsOpen: false
    property bool languageOpen: false
    readonly property int allTabMask: (1 << 5) - 1
    property int tabLoadMask: allTabMask

    function tabIsLoaded(index) {
        return (tabLoadMask & (1 << index)) !== 0
    }

    function markTabLoaded(index) {
        if (!tabIsLoaded(index))
            tabLoadMask = tabLoadMask | (1 << index)
    }

    function selectTab(index) {
        if (index === activeTabIndex)
            return
        markTabLoaded(index)
        activeTabIndex = index
    }

    function syncUiLanguage() {
        gamePetEggTest.setUiLanguage(UiLocale.selectedCode)
        gamePetCollection.setUiLanguage(UiLocale.selectedCode)
        gameMountCollection.setUiLanguage(UiLocale.selectedCode)
        gameTest.skillCollection.setUiLanguage(UiLocale.selectedCode)
        gameTechTreeForge.setUiLanguage(UiLocale.selectedCode)
        gameTechTreePower.setUiLanguage(UiLocale.selectedCode)
        gameTechTreeSkillsPetTech.setUiLanguage(UiLocale.selectedCode)
    }

    Component.onCompleted: {
        UiLocale.setSelectedLocale(uiLanguage)
        syncUiLanguage()
    }

    Connections {
        target: UiLocale
        function onSelectedLocaleChanged() {
            syncUiLanguage()
        }
    }

    SettingsView {
        visible: window.settingsOpen
        anchors.fill: parent
        dimBackdrop: true
        z: 101
        onClosed: {
            window.settingsOpen = false
            window.languageOpen = false
        }
        onLanguagesClicked: window.languageOpen = true
    }

    LanguageSettingsView {
        visible: window.settingsOpen && window.languageOpen
        anchors.fill: parent
        z: 102
        onClosed: window.languageOpen = false
    }

    LoadingOverlay {
        parent: Overlay.overlay
        anchors.fill: parent
        active: UiLoading.active
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
            onLoadDumpClicked: UiLoading.defer(function() {
                gameSession.loadDumpFromClipboardSync()
            })
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
                active: window.tabIsLoaded(0)
                visible: window.activeTabIndex === 0
                sourceComponent: forgeMainComponent
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
        id: forgeMainComponent

        ForgeMainView {
            anchors.fill: parent
        }
    }

    Component {
        id: skillMainComponent

        SkillMainView {
            anchors.fill: parent
            skillController: gameTest
            sessionBridge: gameSession
            summonResultWidthRatio: 0.3
        }
    }

    Component {
        id: petMainComponent

        PetMainView {
            anchors.fill: parent
            petController: gamePetSummonTest
            petCollectionModel: gamePetCollection
            sessionBridge: gameSession
            summonResultWidthRatio: 0.3
        }
    }

    Component {
        id: mountMainComponent

        MountMainView {
            anchors.fill: parent
            mountController: gameMountSummonTest
            mountCollectionModel: gameMountCollection
            sessionBridge: gameSession
            summonResultWidthRatio: 0.3
        }
    }

    Component {
        id: techMainComponent

        TechMainView {
            anchors.fill: parent
            sessionBridge: gameSession
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
