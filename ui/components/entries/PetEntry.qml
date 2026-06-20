import QtQuick
import ui 1.0

Item {
	id: root

	property var petModel

	readonly property int iconSize: 256

	implicitWidth: iconSize
	implicitHeight: iconSize

	PetIcon {
		id: icon
		anchors.fill: parent
		visible: root.petModel !== null
		opacity: (root.petModel && root.petModel.isEquipped) ? 5 / 16 : 1
		rarity: root.petModel?.rarity ?? 0
		spriteIndex: root.petModel?.spriteIndex ?? 0
		spriteSheet: root.petModel?.spriteSheet ?? ""
		sheetCols: root.petModel?.sheetCols ?? 8
		sheetNativeSize: root.petModel?.sheetNativeSize ?? 2048
	}

	EquippedVisual {
		anchors.centerIn: icon
		visible: root.petModel?.isEquipped ?? false
		scaleHorizontal: 2.5
		width: iconSize * 1.2
	}

	AppText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * 0.09
		segments: [
			{ locId: "25799296414314496" },
			{ text: (root.petModel?.level ?? -1) + 1 }
		]
		segmentSpacing: iconSize * 0.015
		locLetterSpacing: 4
		rawLetterSpacing: 0
		fillColor: Theme.white
		pixelSize: iconSize * 5 / 16
		outlineColor: Theme.black
		outlineWeight: 8
	}
}
