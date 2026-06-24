import QtQuick
import ui 1.0

Item {
	id: root

	property var skillCollectionModel: null

	property bool detailsOpen: false
	property var selectedSkillModel: null

	SkillGrid {
		id: skillGrid

		anchors.fill: parent
		skillCollectionModel: root.skillCollectionModel
		onSkillClicked: function(skillModel) {
			root.selectedSkillModel = skillModel
			root.detailsOpen = true
		}
	}

	SkillDetailsView {
		id: skillDetails

		z: 10
		visible: root.detailsOpen && root.selectedSkillModel !== null
		anchors.centerIn: parent
		skillModel: root.selectedSkillModel
		ascensionLevel: skillGrid.ascensionLevel
		onClosed: root.detailsOpen = false
	}
}
