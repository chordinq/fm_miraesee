import QtQuick
import ui 1.0

Item {
	id: root

	property var skillCollectionModel: null
	property var skillController: null

	property bool detailsOpen: false
	property var selectedSkillModel: null
	property int selectedCombatSkillType: -1

	SkillGrid {
		id: skillGrid

		anchors.fill: parent
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
