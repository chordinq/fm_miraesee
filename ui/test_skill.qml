import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "SkillCollection test (" + testSkillCollection.skillCount + " skills)"
	color: Theme.white

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	SkillCollection {
		anchors.fill: parent
		skillCollectionModel: testSkillCollection
	}
}
