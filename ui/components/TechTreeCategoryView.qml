import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property string treeType: "forge"
	property real progress: 0
	property int progressLevelSum: 0
	property int progressMaxSum: 0
	property bool researchActive: false
	property bool researchComplete: false
	property string researchRemainingText: ""

	signal clicked()

	property real scaleW: 12
	property real scaleH: 10
	property real headerHeightRatio: 0.195

	readonly property real rectOutlineScaleW: scaleW * 2
	readonly property real rectOutlineScaleH: scaleH * 2
	readonly property real headerHeight: height * headerHeightRatio
	readonly property real rectBorderWidth: width * 63 / (128 * scaleW)
	readonly property real titleFontScale: 0.6
	readonly property real progressFontScale: 0.145
	readonly property real iconWidthRatio: 0.435

	readonly property var typeConfig: {
		switch (treeType) {
		case "power":
			return {
				locId: "280343846913",
				image: "TechTreePower.png"
			}
		case "skillsPetTech":
			return {
				locId: "280343846914",
				image: "TechTreeMeta.png"
			}
		default:
			return {
				locId: "280343846912",
				image: "TechTreeForge.png"
			}
		}
	}

	readonly property string progressText: {
		NumberDisplay.revision
		UiSettings.preciseNumberEnabled
		if (root.progressMaxSum > 0)
			return NumberDisplay.formatPercentageRational(
				root.progressLevelSum,
				root.progressMaxSum
			)
		return NumberDisplay.formatPercentageFraction(root.progress)
	}

	readonly property string titleLabel: {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text_table(
			root.typeConfig.locId,
			UiLocale.selectedCode,
			"TechTree"
		)
	}

	readonly property string completeSuffix: {
		UiLocale.selectedCode
		if (!root.researchComplete)
			return ""
		return TmpTextBridge.tech_tree_complete_suffix(UiLocale.selectedCode)
	}

	readonly property string activeResearchSuffix: {
		if (!root.researchActive || root.researchComplete)
			return ""
		return TmpTextBridge.tech_tree_active_research_suffix(
			root.researchRemainingText
		)
	}

	readonly property string progressSuffix: {
		if (root.researchComplete)
			return root.completeSuffix
		if (root.researchActive)
			return root.activeResearchSuffix
		return ""
	}

	readonly property real titlePixelSize: headerHeight * titleFontScale
	readonly property real titleWidthRatio: 0.92

	implicitWidth: 256
	implicitHeight: implicitWidth * (scaleH / scaleW)
	height: width * (scaleH / scaleW)

	clip: true

	RectRounded {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		fillColor: Theme.white
	}

	Item {
		id: headerClip

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		height: root.headerHeight
		clip: true

		RectRounded {
			anchors.left: parent.left
			anchors.right: parent.right
			y: 0
			height: root.height
			scaleW: root.scaleW
			scaleH: root.scaleH
			fillColor: Theme.checkBoxActiveGrey
		}

		Item {
			id: titleHost

			anchors.centerIn: parent
			width: headerClip.width * root.titleWidthRatio
			height: titleText.implicitHeight

			TMPText {
				id: titleText

				anchors.centerIn: parent
				tmpText: root.titleLabel
				pixelSize: root.titlePixelSize
				letterSpacing: 0
				fillColor: Theme.white
				outlineWeight: 8
				scale: Math.min(1, titleHost.width / Math.max(implicitWidth, 1))
				transformOrigin: Item.Center
			}
		}
	}

	Item {
		id: dividerClip

		anchors.left: parent.left
		anchors.right: parent.right
		y: root.headerHeight - root.rectBorderWidth
		height: root.rectBorderWidth
		clip: true

		RectOutline {
			anchors.left: parent.left
			anchors.right: parent.right
			y: dividerClip.height - root.height
			height: root.height
			scaleW: root.rectOutlineScaleW
			scaleH: root.rectOutlineScaleH
			outlineColor: Theme.black
		}
	}

	Item {
		id: bodyArea

		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		height: root.height - root.headerHeight

		Image {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.verticalCenter: parent.verticalCenter
			anchors.verticalCenterOffset: -bodyArea.height * 0.12
			width: bodyArea.width * root.iconWidthRatio
			height: width
			source: Qt.resolvedUrl(
				"../../assets/sprites/TechTree/" + root.typeConfig.image)
			fillMode: Image.PreserveAspectFit
			smooth: true
			mipmap: true
		}

		TMPText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			anchors.bottomMargin: bodyArea.height * 0.05
			tmpText: root.progressText
			suffixText: root.progressSuffix
			suffixFillColor: root.progressSuffix !== "" ? Theme.green : "transparent"
			pixelSize: bodyArea.height * root.progressFontScale
			letterSpacing: 0
			fillColor: Theme.white
			outlineWeight: 8
		}
	}

	RectRoundedOutline {
		anchors.fill: parent
		scaleW: root.scaleW
		scaleH: root.scaleH
		outlineColor: Theme.black
	}

	MouseArea {
		anchors.fill: parent
		onClicked: root.clicked()
	}
}
