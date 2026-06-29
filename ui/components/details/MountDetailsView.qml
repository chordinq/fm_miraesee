import QtQuick
import ui 1.0

DetailsView {
	id: root

	property var mountModel: null
	property var mountController: null
	property int ascensionLevel: 0

	property bool comingSoonVisible: false

	readonly property color titleColor: mountModel
		? Theme.rarityColors[mountModel.rarity]
		: Theme.darkText

	readonly property string upgradeLocId: "25788540620828672"
	readonly property string equipLocId: "27933087392002048"
	readonly property string removeLocId: "27927471772594176"
	readonly property string comingSoonLocId: "29372916365455360"

	MountEntryView {
		parent: root.slotHost
		anchors.left: root.slotHost.left
		anchors.top: root.slotHost.top
		mountModel: root.mountModel
		ascensionLevel: root.ascensionLevel
		scale: root.slotScale
		transformOrigin: Item.TopLeft
	}

	Row {
		parent: root.titleRow
		spacing: root.width * root.titleRowSpacingRatio

		AppText {
			prefix: "["
			locTable: root.mountModel ? root.mountModel.rarityLocTable : "General"
			locId: root.mountModel ? root.mountModel.rarityLocId : ""
			suffix: "]"
			fillColor: root.titleColor
			pixelSize: root.width * root.titleFontScale
			outlineWeight: 8
		}

		AppText {
			locTable: root.mountModel ? root.mountModel.nameLocTable : "Pets"
			locId: root.mountModel ? root.mountModel.nameLocId : ""
			fillColor: root.titleColor
			pixelSize: root.width * root.titleFontScale
			outlineWeight: 8
		}
	}

	Repeater {
		parent: root.bodyColumn
		model: root.mountModel ? root.mountModel.statLines : []

		Row {
			required property var modelData

			readonly property bool isSecondary: modelData.secondary
			readonly property color lineColor: isSecondary ? Theme.darkGreyText : Theme.black
			spacing: root.width * 0.012

			AppText {
				text: root.formatStatLine(modelData)
				fillColor: parent.lineColor
				pixelSize: root.width * root.statFontScale
				outlineWeight: 0
			}

			StatLocLabel {
				locSegments: modelData.labelLocSegments
				fillColor: parent.lineColor
				pixelSize: root.width * root.statFontScale
				outlineWeight: 0
			}
		}
	}

	AppText {
		parent: root.statusHost
		anchors.horizontalCenter: parent.horizontalCenter
		visible: root.comingSoonVisible
		locTable: "General"
		locId: root.comingSoonLocId
		suffix: "!"
		fillColor: Theme.red
		pixelSize: root.width * root.titleFontScale
		outlineWeight: 0
	}

	Row {
		parent: root.actionRow
		spacing: root.actionRowSpacing

		RectRoundButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			labelPixelSize: root.actionButtonFontPixelSize
			locTable: "General"
			locId: root.upgradeLocId
			fillColor: Theme.blue
			enabled: root.mountController !== null && root.mountModel !== null
			onClicked: root.comingSoonVisible = true
		}

		RectRoundButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			labelPixelSize: root.actionButtonFontPixelSize
			visible: root.mountModel && !root.mountModel.isEquipped
			locId: root.equipLocId
			fillColor: root.mountModel && root.mountModel.canEquip
				? Theme.blue
				: Theme.lightGrey
			enabled: root.mountController !== null
				&& root.mountModel !== null
				&& root.mountModel.canEquip
			onClicked: {
				if (root.mountController && root.mountModel)
					root.mountController.performMountEquip(root.mountModel.guid)
			}
		}

		RectRoundButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			scaleW: root.actionButtonScaleW
			scaleH: root.actionButtonScaleH
			labelPixelSize: root.actionButtonFontPixelSize
			visible: root.mountModel && root.mountModel.isEquipped
			locId: root.removeLocId
			fillColor: Theme.lightRed
			enabled: root.mountController !== null && root.mountModel !== null
			onClicked: {
				if (root.mountController && root.mountModel)
					root.mountController.performMountUnequip(root.mountModel.guid)
			}
		}
	}

	Timer {
		interval: 2000
		running: root.comingSoonVisible
		onTriggered: root.comingSoonVisible = false
	}

	onClosed: root.comingSoonVisible = false
}
