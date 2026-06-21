import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
    id: window

    width: initWinWidth
    // 🌟 오타 수정: width -> height
    height: initWinHeight 
    visible: true
    title: "EggHatchPanel test (" + hatchTestFilledCount + " filled, "
        + hatchTestEmptyCount + " empty / " + testPetCollection.hatchSlotCount + " slots)"
    // 배경색은 기존 부화장 테스트와 어울리는 어두운 색상 유지
    color: "#1A1D26" 

    Component.onCompleted: {
        Theme.language = uiLanguage
    }

    EggHatchPanel {
        // 🌟 수정됨: top 앵커를 지우고 예시처럼 완벽한 중앙 정렬로 변경
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        
        // 🌟 수정됨: 창의 너비와 높이 중 더 제약이 심한 쪽에 맞춰 크기를 축소 (비율 방어)
        width: Math.min(parent.width * 0.9, parent.height * 12 / 5 * 0.9)
        
        petCollectionModel: testPetCollection
    }
}