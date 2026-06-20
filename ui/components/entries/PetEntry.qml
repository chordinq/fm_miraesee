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
		locId: "25799296414314496"
		locTable: "General"
		suffix: "\u200A" + ((root.petModel?.level ?? -1) + 1)
		useUiFont: true
		fillColor: Theme.white
		pixelSize: iconSize * 5 / 16
		letterSpacing: 4
		outlineColor: Theme.black
		outlineWeight: 8
	}
}
