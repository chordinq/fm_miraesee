import QtQuick
import ui 1.0

Item {
	id: root

	property string spriteSheet: ""
	property int sheetCols: 1
	property int sheetNativeSize: 256
	property int spriteIndex: 0
	property int itemAge: 0
	property real iconSizeRatio: 0.85

	readonly property int itemAgeInterstellar: 5
	readonly property int itemAgeMultiverse: 6
	readonly property int itemAgeQuantum: 7
	readonly property int itemAgeUnderworld: 8
	readonly property int itemAgeDivine: 9
	readonly property int logicalSize: 256

	implicitWidth: logicalSize
	implicitHeight: logicalSize

	layer.enabled: true
	layer.smooth: true
	layer.mipmap: true

	RectRounded {
		anchors.fill: parent
		scaleW: 4
		scaleH: 4
		fillColor: Theme.itemAgeColors[root.itemAge]
		fillOpacity: 1.0
	}

	Loader {
		anchors.fill: parent
		source: {
			switch (root.itemAge) {
			case root.itemAgeInterstellar:
				return Qt.resolvedUrl("../../graphics/background/InterstellarBackground.qml")
			case root.itemAgeQuantum:
				return Qt.resolvedUrl("../../graphics/background/QuantumBackground.qml")
			case root.itemAgeMultiverse:
				return Qt.resolvedUrl("../../graphics/background/MultiverseBackground.qml")
			case root.itemAgeUnderworld:
				return Qt.resolvedUrl("../../graphics/background/UnderworldBackground.qml")
			case root.itemAgeDivine:
				return Qt.resolvedUrl("../../graphics/background/DivineBackgound.qml")
			default:
				return ""
			}
		}
		onLoaded: {
			if (item) {
				item.scaleW = 4
				item.scaleH = 4
			}
		}
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: 4
		scaleH: 4
		outlineColor: Theme.black
		outlineOpacity: 1.0
	}

	SpriteSheet {
		anchors.fill: parent
		source: root.spriteSheet
		spriteIndex: root.spriteIndex
		sheetCols: root.sheetCols
		sheetNativeSize: root.sheetNativeSize
		sizeRatio: root.iconSizeRatio
	}
}
