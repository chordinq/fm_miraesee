import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "EquipSlot test"
	color: Theme.darkBlue

	readonly property real slotScaleW: 20
	readonly property real slotScaleH: 4
	readonly property real bannerScaleW: 8
	readonly property real slotHeight: Math.min(height * 0.14, width * 0.14 / (slotScaleW / slotScaleH))
	readonly property real slotWidth: slotHeight * (slotScaleW / slotScaleH)
	readonly property real bannerWidth: slotHeight * (bannerScaleW / slotScaleH)
	readonly property real bannerFontScale: 11 / 16

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	Item {
		id: preview
		anchors.centerIn: parent
		width: slotWidth
		height: slotHeight

		EquipSlot {
			id: equipSlot
			anchors.fill: parent
			scaleW: window.slotScaleW
			scaleH: window.slotScaleH
		}

		TagBanner {
			id: tagBanner
			scaleW: window.bannerScaleW
			scaleH: window.slotScaleH
			width: window.bannerWidth
			height: parent.height
			anchors.verticalCenter: parent.verticalCenter
			anchors.horizontalCenter: parent.left
		}

		AppText {
			anchors.centerIn: tagBanner
			locId: "27927471772594177"
			fillColor: Theme.black
			pixelSize: tagBanner.height * bannerFontScale
			outlineWeight: 0
		}
	}
}
