pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property real aspectW: 5
	property real aspectH: 1.5
	property url iconSource: ""
	property int amount: 0
	property real barFillOpacity: 0.5
	property real iconSizeRatio: 1.5
	property real textSizeRatio: 0.8
	property real textRightMarginRatio: 0.08
	property real iconHorizontalOffset: 0
	property real iconVerticalOffset: 0

	readonly property real baseSize: 256
	readonly property real barAspect: aspectW / aspectH
	readonly property real implicitBarHeight: baseSize * aspectH
	readonly property real barHeight: height
	readonly property real iconSize: barHeight * iconSizeRatio
	readonly property real iconOverflow: Math.max(0, iconSize * 0.5 - iconHorizontalOffset)

	implicitHeight: implicitBarHeight
	implicitWidth: implicitBarHeight * barAspect
	width: height > 0 ? height * barAspect : implicitWidth

	Layout.preferredWidth: implicitWidth
	Layout.preferredHeight: implicitHeight
	Layout.fillWidth: false
	Layout.maximumWidth: height > 0 ? height * barAspect : implicitWidth

	function formatAmount(value) {
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		return NumberDisplay.formatInteger(value)
	}

	RectRounded {
		anchors.fill: parent
		aspectW: root.aspectW
		aspectH: root.aspectH
		cornerRatioW: 255 / (512 * (root.aspectW))
		cornerRatioH: 255 / (512 * (root.aspectH))
		fillColor: Theme.black
		fillOpacity: root.barFillOpacity
	}

	RectRoundedOutline {
		anchors.fill: parent
		aspectW: root.aspectW
		aspectH: root.aspectH
		cornerRatioW: 255 / (512 * (root.aspectW))
		cornerRatioH: 255 / (512 * (root.aspectH))
		outlineColor: Theme.black
		z: 1
	}

	Image {
		id: currencyIcon

		width: root.iconSize
		height: root.iconSize
		anchors.verticalCenter: parent.verticalCenter
		anchors.horizontalCenter: parent.left
		visible: root.iconSource !== ""
		source: root.iconSource
		fillMode: Image.PreserveAspectFit
		smooth: true
		mipmap: true
		z: 2
	}

	Item {
		id: textRegion

		anchors.left: parent.left
		anchors.leftMargin: root.iconSize * 0.5
		anchors.right: parent.right
		anchors.rightMargin: parent.width * root.textRightMarginRatio
		anchors.top: parent.top
		anchors.bottom: parent.bottom
		z: 2

		TMPText {
			anchors.centerIn: parent
			visible: root.iconSource !== ""
			tmpText: root.formatAmount(root.amount)
			pixelSize: root.barHeight * root.textSizeRatio
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}
	}
}
