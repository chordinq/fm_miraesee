pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property var summonController: null

	readonly property string maxedLabel: {
		UiLocale.selectedCode
		return TmpTextBridge.maxed_progress_label(UiLocale.selectedCode)
	}

	readonly property int summonLevel: root.summonController
		? root.summonController.summonLevel
		: 1
	readonly property int progressCount: root.summonController
		? root.summonController.summonProgressCount
		: 0
	readonly property int progressRequired: root.summonController
		? root.summonController.summonProgressRequired
		: 1
	readonly property real progressFraction: root.summonController
		? root.summonController.summonProgressFraction
		: 0
	readonly property bool showMaxed: root.summonController
		? root.summonController.summonProgressMaxed
		: false
	readonly property bool showProgress: !root.showMaxed
	readonly property string progressLabel: {
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		return NumberDisplay.formatProgressPair(
			root.progressCount,
			root.progressRequired
		)
	}

	readonly property int ascensionLevel: root.summonController
		? root.summonController.ascensionLevel
		: 0

	readonly property real infoButtonSize: height * 0.3
	readonly property real levelPixelSize: height * 0.17
	readonly property real ascensionStarSize: height * 0.18
	readonly property real progressScaleW: 72 / 16
	readonly property real progressScaleH: 17 / 16
	readonly property real progressFontScale: 12 / 16
	readonly property real progressWidth: height * 0.9
	readonly property real progressBarHeight: progressWidth * progressScaleH / progressScaleW
	readonly property real columnSpacing: height * 0.04
	readonly property real infoVerticalCenterOffset: -(
		root.levelPixelSize / 2 + root.columnSpacing / 2 + root.infoButtonSize / 2
	)
	readonly property real progressVerticalCenterOffset:
		root.levelPixelSize / 2 + root.columnSpacing + root.progressBarHeight / 2
	readonly property real ascensionStarVerticalCenterOffset: progressVerticalCenterOffset * 3/2
	readonly property real infoHorizontalCenterOffset: 0
	readonly property real progressHorizontalCenterOffset: 0

	signal infoClicked()

	implicitWidth: progressWidth
	implicitHeight: infoButtonSize + columnSpacing + levelPixelSize + columnSpacing + progressBarHeight

	Item {
		id: levelAnchor

		anchors.centerIn: parent

		LevelText {
			id: levelText

			anchors.centerIn: parent
			visible: !root.showMaxed
			level: root.summonLevel
			pixelSize: root.levelPixelSize
			fillColor: Theme.black
			outlineWeight: 0
		}

		TMPText {
			id: maxedText

			anchors.centerIn: parent
			visible: root.showMaxed
			tmpText: root.maxedLabel
			pixelSize: root.levelPixelSize
			fillColor: Theme.black
			outlineWeight: 0
		}
	}

	InfoButton {
		width: root.infoButtonSize
		height: width
		anchors.horizontalCenter: levelAnchor.horizontalCenter
		anchors.horizontalCenterOffset: root.infoHorizontalCenterOffset
		anchors.verticalCenter: levelAnchor.verticalCenter
		anchors.verticalCenterOffset: root.infoVerticalCenterOffset
		onClicked: root.infoClicked()
	}

	ProgressBar {
		visible: root.showProgress
		width: root.progressWidth
		scaleW: root.progressScaleW
		scaleH: root.progressScaleH
		progressFraction: root.progressFraction
		fillColor: Theme.blue
		trackFillOpacity: 14 / 16
		labelText: root.progressLabel
		labelFontScale: root.progressFontScale
		labelVerticalCenterOffsetRatio: 1 / 6
		anchors.horizontalCenter: levelAnchor.horizontalCenter
		anchors.horizontalCenterOffset: root.progressHorizontalCenterOffset
		anchors.verticalCenter: levelAnchor.verticalCenter
		anchors.verticalCenterOffset: root.progressVerticalCenterOffset
	}

	AscensionStarView {
		visible: root.ascensionLevel >  0
		ascensionLevel: root.ascensionLevel
		starSize: root.ascensionStarSize
		anchors.horizontalCenter: levelAnchor.horizontalCenter
		anchors.verticalCenter: levelAnchor.verticalCenter
		anchors.verticalCenterOffset: root.ascensionStarVerticalCenterOffset
	}
}
