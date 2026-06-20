import QtQuick
import ui 1.0

Item {
	id: root

	property var eggModel

	readonly property int iconSize: 256

	implicitWidth: iconSize
	implicitHeight: iconSize

	EggIcon {
		id: icon
		anchors.fill: parent
		visible: root.eggModel !== null
		source: root.eggModel?.spriteSheet ?? ""
		spriteIndex: root.eggModel?.spriteIndex ?? -1
		sheetCols: root.eggModel?.sheetCols ?? 8
		sheetNativeSize: root.eggModel?.sheetNativeSize ?? 2048
	}

	AppText {
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * 0.09
		segments: [{ locId: "1084108339605504", table: "Stats" }]
		locLetterSpacing: 4
		fillColor: Theme.white
		pixelSize: iconSize * 5 / 16
		outlineColor: Theme.black
		outlineWeight: 8
	}
}
