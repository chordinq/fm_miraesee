import QtQuick
import ui 1.0

Item {
	id: root

	property var nodeModel: null
	property color fillColor: Theme.white

	readonly property int iconSize: 256
	readonly property int nodeType: nodeModel?.nodeType ?? -1
	readonly property int iconLevel: nodeModel?.iconLevel ?? -2
	readonly property int levelMax: nodeModel?.levelMax ?? 0
	readonly property bool maxLevel: nodeModel?.maxLevel ?? false
	readonly property string progressText: {
		if (levelMax <= 0)
			return ""
		if (maxLevel)
			return "Max"
		if (iconLevel < 0)
			return "0/" + levelMax
		return (iconLevel + 1) + "/" + levelMax
	}

	implicitWidth: iconSize
	implicitHeight: iconSize

	TechTreeIcon {
		id: icon
		anchors.fill: parent
		nodeType: root.nodeType
		fillColor: root.fillColor
	}

	AppText {
		id: progressLabel
		anchors.horizontalCenter: icon.horizontalCenter
		anchors.verticalCenter: icon.bottom
		anchors.verticalCenterOffset: icon.height * 0.17
		text: root.progressText
		visible: root.nodeType >= 0
		pixelSize: iconSize * 17 / 64
		fillColor: Theme.white
		outlineWeight: 8
	}
}
