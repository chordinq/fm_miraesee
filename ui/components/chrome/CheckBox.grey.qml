import QtQuick
import ui 1.0

Item {
	id: root

	property bool checked: false

	signal clicked()

	readonly property int sourceNativeSize: 256

	implicitWidth: sourceNativeSize
	implicitHeight: sourceNativeSize

	RectRounded {
		anchors.fill: parent
		scaleW: 1.5
		scaleH: 1.5
		fillColor: Theme.checkBoxActiveGrey
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: 1.5
		scaleH: 1.5
		outlineColor: Theme.black
	}

	Image {
		anchors.centerIn: parent
		width: parent.width * 0.62
		height: width
		source: Qt.resolvedUrl("../../assets/sprites/General/CheckIcon.png")
		fillMode: Image.PreserveAspectFit
		smooth: true
		mipmap: true
		visible: root.checked
	}

	MouseArea {
		anchors.fill: parent
		onClicked: root.clicked()
	}
}
