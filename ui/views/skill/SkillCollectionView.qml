import QtQuick
import ui 1.0

Item {
	id: root

	property var skillCollectionModel: null
	property var skillController: null

	property bool detailsOpen: false
	property var selectedSkillModel: null
	property int selectedCombatSkillType: -1

	readonly property real bottomBarMargin: Math.max(8, height * 0.02)
	readonly property real actionButtonScaleW: 2.56
	readonly property real actionButtonScaleH: 1
	readonly property real actionButtonWidthRatio: 0.3
	readonly property real actionRowSpacingRatio: 0.15
	readonly property real actionButtonWidth: width * actionButtonWidthRatio
	readonly property real actionRowSpacing: actionButtonWidth * actionRowSpacingRatio
	readonly property real actionButtonHeight:
		actionButtonWidth * actionButtonScaleH / actionButtonScaleW

	Row {
		id: actionRow

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: parent.bottom
		anchors.bottomMargin: root.bottomBarMargin
		spacing: root.actionRowSpacing

		UpgradeAllButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			onClicked: {
				if (root.skillController)
					root.skillController.performUpgradeAll()
			}
		}

		QuickEquipButton {
			width: root.actionButtonWidth
			height: root.actionButtonHeight
			onClicked: {
				if (root.skillController)
					root.skillController.performQuickEquip()
			}
		}
	}

	SkillGrid {
		id: skillGrid

		anchors.top: parent.top
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: actionRow.top
		anchors.bottomMargin: root.bottomBarMargin
		skillCollectionModel: root.skillCollectionModel
		onSkillClicked: function(skillModel) {
			root.selectedCombatSkillType = skillModel.combatSkillType
			root.selectedSkillModel = skillModel
			root.detailsOpen = true
		}
	}

	Connections {
		target: root.skillCollectionModel
		function onChanged() {
			if (root.selectedCombatSkillType < 0)
				return
			var skills = root.skillCollectionModel.skills
			for (var i = 0; i < skills.length; i++) {
				if (skills[i].combatSkillType === root.selectedCombatSkillType) {
					root.selectedSkillModel = skills[i]
					return
				}
			}
		}
	}

	SkillDetailsView {
		id: skillDetails

		z: 10
		visible: root.detailsOpen && root.selectedSkillModel !== null
		anchors.fill: parent
		skillModel: root.selectedSkillModel
		skillController: root.skillController
		ascensionLevel: skillGrid.ascensionLevel
		onClosed: {
			root.detailsOpen = false
			root.selectedCombatSkillType = -1
			root.selectedSkillModel = null
		}
	}
}
