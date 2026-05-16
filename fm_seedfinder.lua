function main()
    gg.clearResults()
    
    local prompt = gg.prompt({'현재 망치 개수를 입력하세요:'}, {''}, {'number'})
    if not prompt then return end
    local hammer_count = tonumber(prompt[1])
    
    gg.searchNumber(hammer_count, gg.TYPE_DWORD)
    local count = gg.getResultCount()
    
    if count == 0 then
        gg.alert("검색 결과가 없습니다.")
        return
    end
    
    if count > 1 then
        gg.setVisible(false)
        for i = 10, 1, -1 do
            gg.toast(string.format("10초 뒤 다시 입력창이 뜹니다.\n[남은 시간: %d초] 망치 개수를 줄여두세요!", i))
            gg.sleep(1000)
        end
        gg.setVisible(true)
        
        local refine_prompt = gg.prompt({'10초가 지났습니다.\n바뀐(줄어든) 망치의 개수를 입력하세요:'}, {''}, {'number'})
        if not refine_prompt then return end
        local new_count = tonumber(refine_prompt[1])
        
        gg.refineNumber(new_count, gg.TYPE_DWORD)
        count = gg.getResultCount()
    end
    
    if count == 0 then
        gg.alert("값 정제 실패. 처음부터 다시 시도해주세요.")
        return
    end
    
    local results = gg.getResults(1)
    local Hammer_Addr = results[1].address
    local Entries_Base_Addr = Hammer_Addr - 0x90
    
    gg.toast("PlayerModel 다중 경로 추적 중... 잠시만 기다려주세요.")
    
    local PlayerModel_Base_Addr = trace_player_model(Entries_Base_Addr)
    
    if not PlayerModel_Base_Addr then
        gg.alert("모든 포인터 갈래를 탐색했으나 진짜 PlayerModel을 찾지 못했습니다.")
        return
    end
    
    -- [스킬 추출]
    local SkillCollection = read_qword(PlayerModel_Base_Addr + 0x240)
    local Skill_SummonModel = read_qword(SkillCollection + 0x20)
    local Skill_Seed_Addr = Skill_SummonModel + 0x18
    local Skill_State_Addr = Skill_SummonModel + 0x10
    local Skill_Seed = read_qword(Skill_Seed_Addr)
    local Skill_State = read_qword(Skill_State_Addr)
    
    -- [펫 추출]
    local PetCollection = read_qword(PlayerModel_Base_Addr + 0x258)
    local Pet_SummonModel = read_qword(PetCollection + 0x28)
    local Pet_Seed_Addr = Pet_SummonModel + 0x18
    local Pet_State_Addr = Pet_SummonModel + 0x10
    local Pet_Seed = read_qword(Pet_Seed_Addr)
    local Pet_State = read_qword(Pet_State_Addr)
    
    -- [탈것 추출]
    local MountCollection = read_qword(PlayerModel_Base_Addr + 0x278)
    local Mount_SummonModel = read_qword(MountCollection + 0x18)
    local Mount_Seed_Addr = Mount_SummonModel + 0x18
    local Mount_State_Addr = Mount_SummonModel + 0x10
    local Mount_Seed = read_qword(Mount_Seed_Addr)
    local Mount_State = read_qword(Mount_State_Addr)
    
    -- 클립보드에 복사할 텍스트 포맷 (웹 시뮬레이터에 붙여넣기 편하게 구성)
    local copy_text = string.format(
        "[스킬]\nSeed: %016X\nLevel/Count: %016X\n\n" ..
        "[펫]\nSeed: %016X\nLevel/Count: %016X\n\n" ..
        "[탈것]\nSeed: %016X\nLevel/Count: %016X",
        Skill_Seed, Skill_State,
        Pet_Seed, Pet_State,
        Mount_Seed, Mount_State
    )
    
    -- 게임가디언 API를 이용해 클립보드에 즉시 복사
    gg.copyText(copy_text)
    
    local msg = "추적 및 클립보드 복사 완료\n\n" .. copy_text
    
    gg.alert(msg)
    
    gg.clearResults()
    gg.addListItems({
        {address = Skill_Seed_Addr, flags = gg.TYPE_QWORD, name = "Seed_Skill"},
        {address = Skill_State_Addr, flags = gg.TYPE_QWORD, name = "State_Skill"},
        {address = Pet_Seed_Addr, flags = gg.TYPE_QWORD, name = "Seed_Pet"},
        {address = Pet_State_Addr, flags = gg.TYPE_QWORD, name = "State_Pet"},
        {address = Mount_Seed_Addr, flags = gg.TYPE_QWORD, name = "Seed_Mount"},
        {address = Mount_State_Addr, flags = gg.TYPE_QWORD, name = "State_Mount"}
    })
end

function get_pointers(target_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", target_addr) .. "h", gg.TYPE_QWORD)
    
    local count = gg.getResultCount()
    if count == 0 then return {} end
    if count > 50 then count = 50 end
    
    local results = gg.getResults(count)
    local good_ptrs = {}
    local bad_ptrs = {}
    
    for i, v in ipairs(results) do
        local upper_val = read_qword(v.address - 0x8)
        if upper_val == 0 then
            table.insert(good_ptrs, v.address)
        else
            table.insert(bad_ptrs, v.address)
        end
    end
    
    local sorted_ptrs = {}
    for _, v in ipairs(good_ptrs) do table.insert(sorted_ptrs, v) end
    for _, v in ipairs(bad_ptrs) do table.insert(sorted_ptrs, v) end
    
    return sorted_ptrs
end

function trace_player_model(entries_base)
    local entries_ptrs = get_pointers(entries_base)
    
    for _, e_ptr in ipairs(entries_ptrs) do
        local dict_base = e_ptr - 0x18
        local dict_ptrs = get_pointers(dict_base)
        
        for _, d_ptr in ipairs(dict_ptrs) do
            local currency_base = d_ptr - 0x10
            local currency_ptrs = get_pointers(currency_base)
            
            for _, c_ptr in ipairs(currency_ptrs) do
                local player_base = c_ptr - 0x210
                
                local check_val = read_dword(player_base + 0x20C)
                if check_val == 0 or check_val == 1 then
                    local skill_col = read_qword(player_base + 0x240)
                    if skill_col > 0x10000000 then 
                        return player_base
                    end
                end
            end
        end
    end
    return nil
end

function read_qword(addr)
    local t = {{address = addr, flags = gg.TYPE_QWORD}}
    t = gg.getValues(t)
    if t[1].value then return tonumber(t[1].value) else return 0 end
end

function read_dword(addr)
    local t = {{address = addr, flags = gg.TYPE_DWORD}}
    t = gg.getValues(t)
    if t[1].value then return tonumber(t[1].value) else return 0 end
end

main()