import QtQuick
import ui 1.0

Item {
	id: root

	property bool isLocked: false

	signal clicked()

	readonly property real _baseSize: 256
	readonly property url _unlockedIconSource: Qt.resolvedUrl("../../../assets/sprites/General/Unlocked Lock Icon.png")
	readonly property url _lockedIconSource: Qt.resolvedUrl("../../../assets/sprites/General/Solid Lock Icon Inverted.png")

	implicitWidth: _baseSize
	implicitHeight: _baseSize

	BakedIconButton {
		id: unlockedButton

		anchors.fill: parent
		visible: !root.isLocked
		fillColor: Theme.blue
		iconSource: root._unlockedIconSource
		iconScale: 0.65
		iconVerticalCenterOffsetRatio: -0.08
		onClicked: root.clicked()
	}

	Item {
		id: lockedButton

		anchors.fill: parent
		visible: root.isLocked

		Image {
			anchors.fill: parent
			source: root._lockedIconSource
			fillMode: Image.PreserveAspectFit
			smooth: true
			mipmap: true
		}

		MouseArea {
			anchors.fill: parent
			onClicked: root.clicked()
		}
	}
}
