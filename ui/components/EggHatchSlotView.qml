import QtQuick
import ui 1.0

Item {
	id: root

	property var eggModel: null
	property int ascensionLevel: 0

	signal clicked()

	readonly property int rarity: eggModel?.rarity ?? -1

	readonly property real bedWidthRatio: 6.4 / 7.25
	readonly property real bedHeightRatio: 5.8 / 7.25
	readonly property real bedCenterOffsetRatio: 0.34
	readonly property real lampWidthRatio: 3.5 / 7.25
	readonly property real lampCenterOffsetRatio: -0.38
	readonly property real eggCenterOffsetRatio: 0.23
	readonly property real labelCenterOffsetRatio: 0.71
	readonly property real labelPixelSizeRatio: 0.165

	readonly property real lampTopRatio: lampCenterOffsetRatio - (lampWidthRatio / 2)
	readonly property real bedBottomRatio: bedCenterOffsetRatio + (bedHeightRatio / 2)
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
		width: parent.width * root.bedWidthRatio
		height: parent.width * root.bedHeightRatio
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (root.bedCenterOffsetRatio - root.centerCorrectionRatio)

		Image {
			source: root.bedSource
			anchors.fill: parent
			smooth: true
			mipmap: true
		}
	}

	Item {
		id: lampConeImage
		visible: root.rarity >= 0
		width: parent.width
		height: parent.width
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (0 - root.centerCorrectionRatio)

		Image {
			source: root.lampConeSource
			anchors.fill: parent
			smooth: true
			mipmap: true
		}
	}

	Item {
		id: lampImage
		width: parent.width * root.lampWidthRatio
		height: parent.width * root.lampWidthRatio
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (root.lampCenterOffsetRatio - root.centerCorrectionRatio)

		Image {
			source: root.eggModel ? root.lampOnSource : root.lampOffSource
			anchors.fill: parent
			smooth: true
			mipmap: true
		}
	}

	EggIcon {
		visible: root.eggModel
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (root.eggCenterOffsetRatio - root.centerCorrectionRatio)
		width: parent.width * root.lampWidthRatio
		height: parent.width * root.lampWidthRatio
		rarity: root.rarity
		ascensionLevel: root.ascensionLevel
	}

	Item {
		id: emptyEgg
		visible: !root.eggModel
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (root.eggCenterOffsetRatio - root.centerCorrectionRatio)
		width: parent.width * root.lampWidthRatio
		height: parent.width * root.lampWidthRatio

		Image {
			source: root.emptyFilledSource
			anchors.fill: parent
			opacity: 0.17
			smooth: true
			mipmap: true
		}

		Image {
			source: root.emptyOutlineSource
			anchors.fill: parent
			smooth: true
			mipmap: true
		}
	}

	AppText {
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.verticalCenter: parent.verticalCenter
		anchors.verticalCenterOffset: parent.width * (root.labelCenterOffsetRatio - root.centerCorrectionRatio)
		locId: root.eggModel ? "153364393986" : "153364393985"
		locTable: "Pets"
		suffix: root.eggModel ? "!" : ""
		pixelSize: parent.width * root.labelPixelSizeRatio
		outlineWeight: 6
		fillColor: root.eggModel ? Theme.green : Theme.white
	}

	MouseArea {
		anchors.fill: parent
		enabled: root.eggModel !== null
		onClicked: root.clicked()
	}
}
