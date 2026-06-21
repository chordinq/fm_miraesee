import QtQuick
import ui 1.0

Item {
    id: root

    property var eggModel: null

    readonly property real lampTopRatio: -0.38 - (3.5 / 7.25 / 2)
    readonly property real bedBottomRatio: 0.34 + (5.8 / 7.25 / 2)
    readonly property real totalHeightRatio: bedBottomRatio - lampTopRatio
    readonly property real centerCorrectionRatio: (bedBottomRatio + lampTopRatio) / 2

    implicitWidth: 256
    implicitHeight: 256 * totalHeightRatio

    readonly property string bedSource: Qt.resolvedUrl("../../assets/sprites/HatchSlot/HatchBed.png")
    readonly property string lampOnSource: Qt.resolvedUrl("../../assets/sprites/HatchSlot/HatchLamp.png")
    readonly property string lampOffSource: Qt.resolvedUrl("../../assets/sprites/HatchSlot/HatchLamp_off.png")
    readonly property string lampConeSource: Qt.resolvedUrl("../../assets/sprites/HatchSlot/HatchLampCone.png")

    Item {
        id: bedImage
        visible: true
        width: root.width * 6.4 / 7.25
        height: root.width * 5.8 / 7.25
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.width * (0.34 - root.centerCorrectionRatio)

        Image {
            source: root.bedSource
            anchors.fill: parent
            smooth: true
            mipmap: true
        }
    }

	EggIcon {
		visible: root.eggModel !== null
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.width * (0.24 - root.centerCorrectionRatio)
		width: root.width * 3.5 / 7.25
		height: root.width * 3.5 / 7.25
		source: root.eggModel?.spriteSheet ?? ""
		spriteIndex: root.eggModel?.spriteIndex ?? -1
		sheetCols: root.eggModel?.sheetCols ?? 8
		sheetNativeSize: root.eggModel?.sheetNativeSize ?? 2048
	}

    Item {
        id: lampConeImage
        visible: root.eggModel !== null
        width: root.width
        height: root.width
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.width * (0 - root.centerCorrectionRatio)

        Image {
            source: root.lampConeSource
            anchors.fill: parent
            smooth: true
            mipmap: true
        }
    }

    Item {
        id: lampOnImage
        visible: root.eggModel !== null
        width: root.width * 3.5 / 7.25
        height: root.width * 3.5 / 7.25
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.width * (-0.38 - root.centerCorrectionRatio)

        Image {
            source: root.lampOnSource
            anchors.fill: parent
            smooth: true
            mipmap: true
        }
    }

    Item {
        id: lampOffImage
        visible: root.eggModel == null
        width: root.width * 3.5 / 7.25
        height: root.width * 3.5 / 7.25
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.width * (-0.38 - root.centerCorrectionRatio)

        Image {
            source: root.lampOffSource
            anchors.fill: parent
            smooth: true
            mipmap: true
        }
    }
}
