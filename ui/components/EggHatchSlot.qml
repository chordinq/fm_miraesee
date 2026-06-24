import QtQuick
import ui 1.0

Item {
	id: root

	property var eggModel: null
	property int ascensionLevel: 0

	signal clicked()

	readonly property int rarity: eggModel?.rarity ?? -1
	readonly property real lampTopRatio: -0.38 - (3.5 / 7.25 / 2)
	readonly property real bedBottomRatio: 0.34 + (5.8 / 7.25 / 2)
	readonly property real totalHeightRatio: bedBottomRatio - lampTopRatio
	readonly property real centerCorrectionRatio: (bedBottomRatio + lampTopRatio) / 2

	implicitWidth: 256
	implicitHeight: 256 * totalHeightRatio

	readonly property string emptyOutlineSource: Qt.resolvedUrl("../../assets/sprites/Egg/EggEmpty_Outline.png")
	readonly property string emptyFilledSource: Qt.resolvedUrl("../../assets/sprites/Egg/EggEmpty_Filled.png")
	readonly property string bedSource: Qt.resolvedUrl("../../assets/sprites/HatchSlot/HatchBed.png")
	readonly property string lampOnSource: Qt.resolvedUrl("../../assets/sprites/HatchSlot/HatchLamp.png")
	readonly property string lampOffSource: Qt.resolvedUrl("../../assets/sprites/HatchSlot/HatchLamp_off.png")
	readonly property string lampConeSource: Qt.resolvedUrl("../../assets/sprites/HatchSlot/HatchLampCone.png")

	Item {
		id: bedImage
		width: parent.width * 6.4 / 7.25
		height: parent.width * 5.8 / 7.25
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (0.34 - centerCorrectionRatio)

		Image {
			source: bedSource
			anchors.fill: parent
			smooth: true
			mipmap: true
		}
	}

	Item {
		id: lampConeImage
		visible: rarity >= 0
		width: parent.width
		height: parent.width
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (0 - centerCorrectionRatio)

		Image {
			source: lampConeSource
			anchors.fill: parent
			smooth: true
			mipmap: true
		}
	}

	Item {
		id: lampImage
		width: parent.width * 3.5 / 7.25
		height: parent.width * 3.5 / 7.25
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (-0.38 - centerCorrectionRatio)

		Image {
			source: eggModel ? lampOnSource : lampOffSource
			anchors.fill: parent
			smooth: true
			mipmap: true
		}
	}

    EggIcon {
		visible: eggModel
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (0.23 - centerCorrectionRatio)
		width: parent.width * 3.5 / 7.25
		height: parent.width * 3.5 / 7.25
		rarity: eggModel?.rarity ?? -1
		ascensionLevel: parent.ascensionLevel
	}

	Item {
		id: emptyEgg
		visible: !eggModel
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (0.23 - centerCorrectionRatio)
		width: parent.width * 3.5 / 7.25
		height: parent.width * 3.5 / 7.25

		Image {
			source: emptyFilledSource
			anchors.fill: parent
			opacity: 0.17
			smooth: true
			mipmap: true
		}

		Image {
			source: emptyOutlineSource
			anchors.fill: parent
			smooth: true
			mipmap: true
		}
	}
    
	AppText {
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (0.71 - centerCorrectionRatio)
		locId: eggModel ? "153364393986" : "153364393985"
		locTable: "Pets"
		suffix: eggModel ? "!" : ""
		pixelSize: parent.width * 0.165
		outlineWeight: 6
		fillColor: eggModel ? Theme.green : Theme.white
	}

	MouseArea {
		anchors.fill: parent
		enabled: root.eggModel !== null
		onClicked: root.clicked()
	}
}
