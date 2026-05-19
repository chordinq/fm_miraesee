function main()
    gg.clearResults()
    
    local prompt = gg.prompt({'현재 망치 개수를 입력하세요.'}, {''}, {'number'})
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
            gg.toast(string.format("[남은 시간: %d초]\n서둘러 망치를 소모하거나 오프보상을 수령하세요.\n망치의 개수가 바뀌어야합니다.", i))
            gg.sleep(1000)
        end
        gg.setVisible(true)
        
        local refine_prompt = gg.prompt({'10초가 지났습니다.\n현재 망치의 개수를 입력하세요.'}, {''}, {'number'})
        if not refine_prompt then return end
        local new_count = tonumber(refine_prompt[1])
        
        gg.refineNumber(new_count, gg.TYPE_DWORD)
        count = gg.getResultCount()
    end
    
    if count == 0 then
        gg.alert("망치 값 정제 실패.\n처음부터 다시 시도해주세요.")
        return
    end
    
    local results = gg.getResults(1)
    local Hammer_Addr = results[1].address
    local Entries_Base_Addr = Hammer_Addr - 0x90
    
    gg.toast("추출 중... 잠시만 기다려주세요.")
    
    local PlayerModel_Base_Addr = trace_player_model(Entries_Base_Addr)
    
    if not PlayerModel_Base_Addr then
        gg.alert("PlayerModel의 주소를 찾지 못했습니다.\n처음부터 다시 시도해주세요.")
        return
    end
    
    -- [ 대장간 (Forge) ]
    local PlayerForgeModel = read_qword(PlayerModel_Base_Addr + 0x218)
    local Forge_Seed_Addr = PlayerForgeModel + 0x18
    local Forge_Level_Addr = PlayerForgeModel + 0x20
    local Forge_Seed = read_qword(Forge_Seed_Addr)
    local Forge_Level = read_qword(Forge_Level_Addr)
    local Forge_Asc_Ptr = read_qword(PlayerForgeModel + 0x50)
    local Forge_Ascension = 0
    if Forge_Asc_Ptr ~= 0 then Forge_Ascension = read_dword(Forge_Asc_Ptr + 0x14) end

    -- [ 스킬 (Skill) ]
    local SkillCollection = read_qword(PlayerModel_Base_Addr + 0x240)
    local Skill_SummonModel = read_qword(SkillCollection + 0x20)
    local Skill_Seed_Addr = Skill_SummonModel + 0x18
    local Skill_State_Addr = Skill_SummonModel + 0x10
    local Skill_Seed = read_qword(Skill_Seed_Addr)
    local Skill_State = read_qword(Skill_State_Addr)
    local Skill_Asc_Ptr = read_qword(SkillCollection + 0x28)
    local Skill_Ascension = 0
    if Skill_Asc_Ptr ~= 0 then Skill_Ascension = read_dword(Skill_Asc_Ptr + 0x14) end
    
    -- [ 펫 (Pet) ]
    local PetCollection = read_qword(PlayerModel_Base_Addr + 0x258)
    local Pet_SummonModel = read_qword(PetCollection + 0x28)
    local Pet_Seed_Addr = Pet_SummonModel + 0x18
    local Pet_State_Addr = Pet_SummonModel + 0x10
    local Pet_Seed = read_qword(Pet_Seed_Addr)
    local Pet_State = read_qword(Pet_State_Addr)
    local Pet_Asc_Ptr = read_qword(PetCollection + 0x30)
    local Pet_Ascension = 0
    if Pet_Asc_Ptr ~= 0 then Pet_Ascension = read_dword(Pet_Asc_Ptr + 0x14) end
    
    -- [ 탈것 (Mount) ]
    local MountCollection = read_qword(PlayerModel_Base_Addr + 0x278)
    local Mount_SummonModel = read_qword(MountCollection + 0x18)
    local Mount_Seed_Addr = Mount_SummonModel + 0x18
    local Mount_State_Addr = Mount_SummonModel + 0x10
    local Mount_Seed = read_qword(Mount_Seed_Addr)
    local Mount_State = read_qword(Mount_State_Addr)
    local Mount_Asc_Ptr = read_qword(MountCollection + 0x20)
    local Mount_Ascension = 0
    if Mount_Asc_Ptr ~= 0 then Mount_Ascension = read_dword(Mount_Asc_Ptr + 0x14) end
    
    -- 12줄로 포맷팅 (시드, 상태, 승천)
    local copy_text = string.format(
        "%016X\n%016X\n%016X\n" ..
        "%016X\n%016X\n%016X\n" ..
        "%016X\n%016X\n%016X\n" ..
        "%016X\n%016X\n%016X",
        Forge_Seed, Forge_Level, Forge_Ascension,
        Skill_Seed, Skill_State, Skill_Ascension,
        Pet_Seed, Pet_State, Pet_Ascension,
        Mount_Seed, Mount_State, Mount_Ascension
    )
    
    gg.copyText(copy_text)
    
    local msg = "클립보드 복사 완료! (12줄)\n\n" .. copy_text
    gg.alert(msg)
    
    -- GG 리스트에도 승천 레벨 주소를 추가
    gg.clearResults()
    local list_items = {
        {address = Forge_Seed_Addr, flags = gg.TYPE_QWORD, name = "Seed_Forge"},
        {address = Forge_Level_Addr, flags = gg.TYPE_QWORD, name = "Level_Forge"},
        {address = Skill_Seed_Addr, flags = gg.TYPE_QWORD, name = "Seed_Skill"},
        {address = Skill_State_Addr, flags = gg.TYPE_QWORD, name = "State_Skill"},
        {address = Pet_Seed_Addr, flags = gg.TYPE_QWORD, name = "Seed_Pet"},
        {address = Pet_State_Addr, flags = gg.TYPE_QWORD, name = "State_Pet"},
        {address = Mount_Seed_Addr, flags = gg.TYPE_QWORD, name = "Seed_Mount"},
        {address = Mount_State_Addr, flags = gg.TYPE_QWORD, name = "State_Mount"}
    }
    
    if Forge_Asc_Ptr ~= 0 then table.insert(list_items, {address = Forge_Asc_Ptr + 0x14, flags = gg.TYPE_DWORD, name = "Asc_Forge"}) end
    if Skill_Asc_Ptr ~= 0 then table.insert(list_items, {address = Skill_Asc_Ptr + 0x14, flags = gg.TYPE_DWORD, name = "Asc_Skill"}) end
    if Pet_Asc_Ptr ~= 0 then table.insert(list_items, {address = Pet_Asc_Ptr + 0x14, flags = gg.TYPE_DWORD, name = "Asc_Pet"}) end
    if Mount_Asc_Ptr ~= 0 then table.insert(list_items, {address = Mount_Asc_Ptr + 0x14, flags = gg.TYPE_DWORD, name = "Asc_Mount"}) end

    gg.addListItems(list_items)
end

-- [1] Entries 전용 포인터 검색 ( -0x10 위치가 무조건 0이어야 함 )
function get_entries_pointers(target_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", target_addr) .. "h", gg.TYPE_QWORD)
    local count = gg.getResultCount()
    if count == 0 then return {} end
    if count > 200 then count = 200 end 
    
    local results = gg.getResults(count)
    local good_ptrs, bad_ptrs = {}, {}
    
    for i, v in ipairs(results) do
        local val_10 = read_qword(v.address - 0x10)
        if val_10 == 0 then
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

-- [2] Dict 전용 포인터 검색 ( -0x8 위치가 무조건 0이어야 함 )
function get_dict_pointers(target_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", target_addr) .. "h", gg.TYPE_QWORD)
    local count = gg.getResultCount()
    if count == 0 then return {} end
    if count > 200 then count = 200 end 
    
    local results = gg.getResults(count)
    local good_ptrs, bad_ptrs = {}, {}
    
    for i, v in ipairs(results) do
        local val_8 = read_qword(v.address - 0x8)
        if val_8 == 0 then
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

-- [3] 일반 포인터 검색 (가짜 주소 밀집 영역 필터링 포함)
function get_pointers(target_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", target_addr) .. "h", gg.TYPE_QWORD)
    local count = gg.getResultCount()
    if count == 0 then return {} end
    if count > 200 then count = 200 end
    
    local results = gg.getResults(count)
    local good_ptrs, bad_ptrs = {}, {}
    
    for i, v in ipairs(results) do
        -- 가짜 주소 방지: 위아래(-0x8, +0x8)에 빈틈없이 값이 꽉 차있다면 가짜일 확률 높음
        local m8 = read_qword(v.address - 0x8)
        local p8 = read_qword(v.address + 0x8)
        
        if m8 == 0 or p8 == 0 then
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
    -- 1단계: Entries 추적 ( -0x10이 0인 것 우선 )
    local entries_ptrs = get_entries_pointers(entries_base)
    
    for _, e_ptr in ipairs(entries_ptrs) do
        local dict_base = e_ptr - 0x18
        
        -- 2단계: Dict 추적 ( -0x8이 0인 것 우선 )
        local dict_ptrs = get_dict_pointers(dict_base)
        
        for _, d_ptr in ipairs(dict_ptrs) do
            local currency_base = d_ptr - 0x10
            
            -- 3단계: Currency 및 PlayerModel 추적 (빼곡한 가짜주소 필터링 적용)
            local currency_ptrs = get_pointers(currency_base)
            
            for _, c_ptr in ipairs(currency_ptrs) do
                local player_base = c_ptr - 0x210
                
                -- 최종 검증 로직 (안정성을 위해 변경하지 않음)
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