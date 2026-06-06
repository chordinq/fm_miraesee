function read_qword(addr)
    local t = {{address = addr, flags = gg.TYPE_QWORD}}
    t = gg.getValues(t)
    return t[1].value and tonumber(t[1].value) or 0
end

function read_dword(addr)
    local t = {{address = addr, flags = gg.TYPE_DWORD}}
    t = gg.getValues(t)
    return t[1].value and tonumber(t[1].value) or 0
end

function extract_stats_blob(stats_ptr, num_chunks)
    num_chunks = num_chunks or 2
    local chunks = {}
    for i = 1, num_chunks do
        chunks[i] = "0000000000"
    end
    if stats_ptr ~= 0 then
        local dict_ptr = read_qword(stats_ptr + 0x10)
        if dict_ptr ~= 0 then
            local count = read_dword(dict_ptr + 0x20)
            local entries = read_qword(dict_ptr + 0x18)
            if entries ~= 0 and count > 0 then
                local limit = math.min(count, num_chunks)
                for i = 0, limit - 1 do
                    local off = i * 0x28
                    local k = read_dword(entries + 0x30 + off)
                    local v = read_qword(entries + 0x40 + off)
                    chunks[i + 1] = string.format("1%X%08X", k % 16, v % 4294967296)
                end
            end
        end
    end
    return table.concat(chunks)
end

function extract_stats_20char(stats_ptr)
    return extract_stats_blob(stats_ptr, 2)
end

function extract_summon_meta(summon_ptr, asc_ptr)
    local count, level, seed = 0, 0, 0
    local asc_lvl = 0

    if summon_ptr ~= 0 then
        -- IL SummonModel: +0x10 count, +0x14 level, +0x18 seed
        count = read_dword(summon_ptr + 0x10)
        level = read_dword(summon_ptr + 0x14)
        seed = read_qword(summon_ptr + 0x18)
    end

    if asc_ptr ~= 0 then
        asc_lvl = read_dword(asc_ptr + 0x14)
    end

    -- summon wire: level(1B) + count(1B) + seed(8B) + pad + asc
    return string.format("%02X%02X%016X00000000000%X", level % 256, count % 256, seed, asc_lvl % 16)
end

function extract_forge_meta(forge_ptr, asc_ptr)
    local count, level, seed, highest_age = 0, 0, 0, 0
    local asc_lvl = 0

    if forge_ptr ~= 0 then
        -- IL PlayerForgeModel: +0x18 ForgeSeed, +0x20 ForgeLevel, +0x3C ForgeCount, +0x40 HighestAge
        seed = read_qword(forge_ptr + 0x18)
        level = read_dword(forge_ptr + 0x20)
        count = read_dword(forge_ptr + 0x3C)
        highest_age = read_dword(forge_ptr + 0x40)
    end

    if asc_ptr ~= 0 then
        asc_lvl = read_dword(asc_ptr + 0x14)
    end

    -- dump v3 forge wire: level(1B) + forge_count(4B) + seed(8B) + highest_age(1B) + reserved(3) + asc
    return string.format("%02X%08X%016X%02X000%X", level % 256, count % 4294967296, seed, highest_age % 256, asc_lvl % 16)
end

function get_pointers(t_addr) gg.clearResults() gg.searchNumber(string.format("%X",t_addr).."h", gg.TYPE_QWORD) local r=gg.getResults(200) local p={} for _,v in ipairs(r) do if read_qword(v.address-0x8)==0 or read_qword(v.address+0x8)==0 then table.insert(p,v.address) end end return p end
function get_dict_pointers(t_addr) gg.clearResults() gg.searchNumber(string.format("%X",t_addr).."h", gg.TYPE_QWORD) local r=gg.getResults(200) local p={} for _,v in ipairs(r) do if read_qword(v.address-0x8)==0 then table.insert(p,v.address) end end return p end
function get_entries_pointers(t_addr) gg.clearResults() gg.searchNumber(string.format("%X",t_addr).."h", gg.TYPE_QWORD) local r=gg.getResults(200) local p={} for _,v in ipairs(r) do if read_qword(v.address-0x10)==0 then table.insert(p,v.address) end end return p end

function trace_player_model(entries_base)
    local entries_ptrs = get_entries_pointers(entries_base)
    for _, e_ptr in ipairs(entries_ptrs) do
        for _, d_ptr in ipairs(get_dict_pointers(e_ptr - 0x18)) do
            for _, c_ptr in ipairs(get_pointers(d_ptr - 0x10)) do
                local player_base = c_ptr - 0x210
                local check_val = read_dword(player_base + 0x20C)
                if check_val == 0 or check_val == 1 then
                    local skill_col = read_qword(player_base + 0x240)
                    if skill_col > 0x10000000 then return player_base end
                end
            end
        end
    end
    return nil
end

function extract_currency(player_ptr)
    local out = {"[CURRENCY]"}
    local model = read_qword(player_ptr + 0x210)
    if model == 0 then return out end
    local dict = read_qword(model + 0x10)
    if dict == 0 then return out end
    
    local count = read_dword(dict + 0x20)
    local entries = read_qword(dict + 0x18)
    local current_line = ""

    for i = 0, count - 1 do
        local amount = read_qword(entries + 0x40 + (i * 0x28))
        current_line = current_line .. string.format("%08X", amount % 4294967296)
        if (i + 1) % 4 == 0 then
            table.insert(out, current_line)
            current_line = ""
        end
    end
    if current_line ~= "" then
        while string.len(current_line) < 32 do current_line = current_line .. "00000000" end
        table.insert(out, current_line)
    end
    return out
end

function extract_techtree(player_ptr)
    local out = {"[TECH_TREE]"}
    local model = read_qword(player_ptr + 0x250)
    if model == 0 then return out end
    local dict = read_qword(model + 0x10)
    if dict == 0 then return out end

    local count = read_dword(dict + 0x20)
    local entries = read_qword(dict + 0x18)
    local current_line = ""
    local node_idx = 0

    for i = 0, count - 1 do
        local t_type = read_dword(entries + 0x30 + (i * 0x28))
        local inner_dict = read_qword(entries + 0x40 + (i * 0x28))
        if t_type ~= 3 and inner_dict ~= 0 then
            local i_cnt = read_dword(inner_dict + 0x20)
            local i_ent = read_qword(inner_dict + 0x18)
            for j = 0, i_cnt - 1 do
                local n_id = read_dword(i_ent + 0x30 + (j * 0x28))
                local n_mdl = read_qword(i_ent + 0x40 + (j * 0x28))
                if n_mdl ~= 0 then
                    local lvl = read_dword(n_mdl + 0x10)
                    if lvl < 0 or lvl > 15 then lvl = 15 end
                    current_line = current_line .. string.format("%X%02X%X", t_type % 16, n_id % 256, lvl % 16)
                    node_idx = node_idx + 1
                    if node_idx % 8 == 0 then
                        table.insert(out, current_line)
                        current_line = ""
                    end
                end
            end
        end
    end
    if current_line ~= "" then
        while string.len(current_line) < 32 do current_line = current_line .. "F000" end
        table.insert(out, current_line)
    end
    return out
end

function extract_forge(player_ptr)
    local forge_ptr = read_qword(player_ptr + 0x218)
    local asc_ptr = forge_ptr ~= 0 and read_qword(forge_ptr + 0x50) or 0
    return {"[FORGE]", extract_forge_meta(forge_ptr, asc_ptr)}
end

function extract_skill_meta(player_ptr)
    local col = read_qword(player_ptr + 0x240)
    local sum_ptr = col ~= 0 and read_qword(col + 0x20) or 0
    local asc_ptr = col ~= 0 and read_qword(col + 0x28) or 0
    return {"[SKILL]", extract_summon_meta(sum_ptr, asc_ptr)}
end

function extract_pet_meta(player_ptr)
    local col = read_qword(player_ptr + 0x258)
    local sum_ptr = col ~= 0 and read_qword(col + 0x28) or 0
    local asc_ptr = col ~= 0 and read_qword(col + 0x30) or 0
    return {"[PET]", extract_summon_meta(sum_ptr, asc_ptr)}
end

function extract_mount_meta(player_ptr)
    local col = read_qword(player_ptr + 0x278)
    local sum_ptr = col ~= 0 and read_qword(col + 0x18) or 0
    local asc_ptr = col ~= 0 and read_qword(col + 0x20) or 0
    return {"[MOUNT]", extract_summon_meta(sum_ptr, asc_ptr)}
end

function extract_hidden_levels(equip_model)
    -- MetaDictionary<ItemType, MetaDictionary<int,int>> @ PlayerEquipmentModel+0x50
    -- Outer: +0x18 entries ptr, +0x20 count (8 ItemTypes)
    -- Outer slot i: key @ entries+0x30+i*0x28, inner dict ptr @ entries+0x40+i*0x28
    -- Inner: +0x18 entries ptr, +0x20 count (10 ItemAges)
    -- Inner slot stride 0x1C (int,int — not 0x28):
    --   hash @ +0x0, key(age) @ +0x4, value(bracket) @ +0x8, next @ +0xC
    local out = {"[HIDDEN_LEVELS]"}
    if equip_model == 0 then return out end
    local outer_dict = read_qword(equip_model + 0x50)
    if outer_dict == 0 then return out end

    local count = read_dword(outer_dict + 0x20)
    local entries = read_qword(outer_dict + 0x18)
    local current_line = ""
    local idx = 0

    for i = 0, count - 1 do
        local t_type = read_dword(entries + 0x30 + (i * 0x28))
        local inner_dict = read_qword(entries + 0x40 + (i * 0x28))
        if inner_dict ~= 0 then
            local i_cnt = read_dword(inner_dict + 0x20)
            local i_ent = read_qword(inner_dict + 0x18)
            for j = 0, i_cnt - 1 do
                local slot = i_ent + 0x30 + (j * 0x1C)
                local age = read_dword(slot + 0x4)
                local lvl = read_dword(slot + 0x8)
                if age >= 0 and age <= 9 and lvl >= 0 and lvl <= 99 then
                    current_line = current_line .. string.format("%X%X%02X", t_type % 16, age % 16, lvl % 256)
                    idx = idx + 1
                    if idx % 8 == 0 then
                        table.insert(out, current_line)
                        current_line = ""
                    end
                end
            end
        end
    end
    if current_line ~= "" then
        while string.len(current_line) < 32 do current_line = current_line .. "F000" end
        table.insert(out, current_line)
    end
    return out
end

function extract_roundrobin(equip_model)
    local out = {"[ITEM_ROUND_ROBIN]"}
    if equip_model == 0 then return out end
    local outer_dict = read_qword(equip_model + 0x58)
    if outer_dict == 0 then return out end

    local active = {}
    local count = read_dword(outer_dict + 0x20)
    local entries = read_qword(outer_dict + 0x18)

    for i = 0, count - 1 do
        local t_type = read_dword(entries + 0x30 + (i * 0x28))
        local inner_dict = read_qword(entries + 0x40 + (i * 0x28))
        if inner_dict ~= 0 then
            local i_cnt = read_dword(inner_dict + 0x20)
            local i_ent = read_qword(inner_dict + 0x18)
            for j = 0, i_cnt - 1 do
                local age = read_dword(i_ent + 0x30 + (j * 0x28))
                local list = read_qword(i_ent + 0x40 + (j * 0x28))
                local bitmask = 0
                if list ~= 0 then
                    local l_cnt = read_dword(list + 0x18)
                    local l_arr = read_qword(list + 0x10)
                    for k = 0, l_cnt - 1 do
                        local idx_val = read_dword(l_arr + 0x20 + (k * 4))
                        if idx_val >= 0 and idx_val <= 7 then bitmask = bitmask | (1 << idx_val) end
                    end
                end
                table.insert(active, {t = t_type, a = age, m = bitmask})
            end
        end
    end

    table.sort(active, function(x, y) if x.t == y.t then return x.a < y.a end return x.t < y.t end)

    local current_line = ""
    for _, v in ipairs(active) do
        current_line = current_line .. string.format("%X%X%02X", v.t % 16, v.a % 16, v.m % 256)
        if string.len(current_line) == 32 then
            table.insert(out, current_line)
            current_line = ""
        end
    end
    if current_line ~= "" then
        while string.len(current_line) < 32 do current_line = current_line .. "0" end
        table.insert(out, current_line)
    end
    return out
end

function extract_equipment(equip_model)
    local out = {"[EQUIPMENT]"}
    if equip_model == 0 then return out end
    local offsets = {0x10, 0x18, 0x20, 0x28, 0x30, 0x38, 0x40, 0x48}

    for _, offset in ipairs(offsets) do
        local item_ptr = read_qword(equip_model + offset)
        if item_ptr == 0 then
            table.insert(out, "00000000000000000000000000000000")
        else
            local id_ptr = read_qword(item_ptr + 0x20)
            local header = string.format("0%X%X%X", read_dword(id_ptr + 0x10) % 16, read_dword(id_ptr + 0x14) % 16, read_dword(id_ptr + 0x18) % 16)
            local flags = 1 + ((read_dword(item_ptr + 0x2C) & 0xFF) * 2) + ((read_dword(item_ptr + 0x2D) & 0xFF) * 4)
            local prog = string.format("%02X00%04X", read_dword(item_ptr + 0x28) % 256, flags)
            table.insert(out, header .. prog .. extract_stats_20char(read_qword(item_ptr + 0x30)))
        end
    end
    return out
end

function extract_skills_collection(player_ptr)
    local out = {"[SKILL_COLLECTION]"}
    local col = read_qword(player_ptr + 0x240)
    if col == 0 then return out end

    local dict = read_qword(col + 0x10)
    if dict ~= 0 then
        local count = read_dword(dict + 0x20)
        local entries = read_qword(dict + 0x18)
        for i = 0, count - 1 do
            local s_enum = read_dword(entries + 0x30 + (i * 0x28))
            local model = read_qword(entries + 0x40 + (i * 0x28))
            if model ~= 0 then
                local header = string.format("1%02X0", s_enum % 256)
                local lvl = read_dword(model + 0x20)
                local shard = read_dword(model + 0x1C)
                local is_eq = read_dword(model + 0x14) % 256
                local slot = read_dword(model + 0x18)
                local prog = string.format("%02X%02X%02X%02X", lvl % 256, shard % 256, is_eq, slot % 256)
                table.insert(out, header .. prog .. "00000000000000000000")
            end
        end
    end
    return out
end

function extract_pets_eggs_collection(player_ptr)
    local out = {"[PET_EGG_COLLECTION]"}
    local col = read_qword(player_ptr + 0x258)
    if col == 0 then return out end

    local pets_list = read_qword(col + 0x10)
    if pets_list ~= 0 then
        local count = read_dword(pets_list + 0x18)
        local arr = read_qword(pets_list + 0x10)
        for i = 0, count - 1 do
            local model = read_qword(arr + 0x20 + (i * 8))
            if model ~= 0 then
                local p_id_ptr = read_qword(model + 0x20)
                local rarity = read_dword(p_id_ptr + 0x10)
                local p_id = read_dword(p_id_ptr + 0x14)
                local header = string.format("2%X%02X", rarity % 16, p_id % 256)
                local lvl = read_dword(model + 0x28)
                local exp = read_dword(model + 0x2C)
                local is_eq = read_dword(model + 0x30) % 256
                local slot = read_dword(model + 0x34) % 256
                local prog = string.format("%08X%08X%02X%02X", lvl, exp, is_eq, slot)
                table.insert(out, header .. prog .. extract_stats_20char(read_qword(model + 0x38)))
            end
        end
    end

    local eggs_list = read_qword(col + 0x18)
    if eggs_list ~= 0 then
        local count = read_dword(eggs_list + 0x18)
        local arr = read_qword(eggs_list + 0x10)
        for i = 0, count - 1 do
            local model = read_qword(arr + 0x20 + (i * 8))
            if model ~= 0 then
                local header = string.format("3%X00", read_dword(model + 0x20) % 16)
                local prog = string.format("0000%02X%02X", read_dword(model + 0x30) % 256, read_dword(model + 0x34) % 256)
                table.insert(out, header .. prog .. string.format("0000%016X", read_qword(model + 0x38)))
            end
        end
    end
    return out
end

function extract_mounts_collection(player_ptr)
    local out = {"[MOUNT_COLLECTION]"}
    local col = read_qword(player_ptr + 0x278)
    if col == 0 then return out end

    local mounts_list = read_qword(col + 0x10)
    if mounts_list ~= 0 then
        local count = read_dword(mounts_list + 0x18)
        local arr = read_qword(mounts_list + 0x10)
        for i = 0, count - 1 do
            local model = read_qword(arr + 0x20 + (i * 8))
            if model ~= 0 then
                local m_id_ptr = read_qword(model + 0x20)
                local header = string.format("4%X%02X", read_dword(m_id_ptr + 0x10) % 16, read_dword(m_id_ptr + 0x14) % 256)
                local lvl = read_dword(model + 0x28)
                local exp = read_dword(model + 0x2C)
                local is_eq = read_dword(model + 0x30) % 256
                local prog = string.format("%08X%08X%02X00", lvl, exp, is_eq)
                table.insert(out, header .. prog .. extract_stats_20char(read_qword(model + 0x38)))
            end
        end
    end
    return out
end

-- Extract PlayerSkinCollectionModel (player_ptr + 0x290)
-- Skin line format (35 chars):
--   5 <item_type:1hex> <idx:02hex> <is_eq:1hex> <level:02hex> <exp:08hex> <stats:20hex>
--
-- NOTE: EquippedSkinGuids = MetaDictionary<ItemType, Guid>.
--   Guid is a 16-byte value type, so entry stride is 0x30 (not the usual 0x28).
--   Verify by checking: if extracted equipped flags are wrong, adjust stride.
function extract_skin_collection(player_ptr)
    local out = {"[SKIN_COLLECTION]"}
    local col = read_qword(player_ptr + 0x290)
    if col == 0 then return out end

    local skins_dict   = read_qword(col + 0x10)
    local eq_guid_dict = read_qword(col + 0x20)

    -- Build equipped GUID map: item_type -> {lo, hi}
    -- MetaDictionary<ItemType, Guid> entry stride = 0x30 (Guid is 16 bytes)
    local eq_map = {}
    if eq_guid_dict ~= 0 then
        local eq_count   = read_dword(eq_guid_dict + 0x20)
        local eq_entries = read_qword(eq_guid_dict + 0x18)
        if eq_entries ~= 0 then
            for i = 0, eq_count - 1 do
                local off = i * 0x30
                local it      = read_dword(eq_entries + 0x30 + off)
                local guid_lo = read_qword(eq_entries + 0x40 + off)
                local guid_hi = read_qword(eq_entries + 0x48 + off)
                if guid_lo ~= 0 or guid_hi ~= 0 then
                    eq_map[it] = {lo = guid_lo, hi = guid_hi}
                end
            end
        end
    end

    if skins_dict == 0 then return out end

    local outer_count   = read_dword(skins_dict + 0x20)
    local outer_entries = read_qword(skins_dict + 0x18)
    if outer_entries == 0 then return out end

    for i = 0, outer_count - 1 do
        local off       = i * 0x28
        local item_type = read_dword(outer_entries + 0x30 + off)
        local list_ptr  = read_qword(outer_entries + 0x40 + off)
        if list_ptr ~= 0 then
            local l_count = read_dword(list_ptr + 0x18)
            local l_arr   = read_qword(list_ptr + 0x10)
            if l_arr ~= 0 and l_count > 0 then
                for j = 0, l_count - 1 do
                    local model = read_qword(l_arr + 0x20 + (j * 8))
                    if model ~= 0 then
                        local guid_lo   = read_qword(model + 0x10)
                        local guid_hi   = read_qword(model + 0x18)
                        local sid_ptr   = read_qword(model + 0x20)
                        local skin_idx  = sid_ptr ~= 0 and read_dword(sid_ptr + 0x14) or 0
                        local level     = read_dword(model + 0x30)
                        local exp       = read_dword(model + 0x34)
                        local stat_ptr  = read_qword(model + 0x28)

                        local eq = eq_map[item_type]
                        local is_eq = (eq and eq.lo == guid_lo and eq.hi == guid_hi) and 1 or 0

                        local line = string.format("5%X%02X%X%02X%08X",
                            item_type % 16, skin_idx % 256, is_eq,
                            level % 256, exp % 4294967296)
                        table.insert(out, line .. extract_stats_20char(stat_ptr))
                    end
                end
            end
        end
    end
    return out
end

function main()
    gg.clearResults()
    
    local prompt = gg.prompt({'현재 망치의 개수를 입력하세요.'}, {''}, {'number'})
    if not prompt then return end
    
    gg.searchNumber(tonumber(prompt[1]), gg.TYPE_DWORD)
    local count = gg.getResultCount()
    if count == 0 then gg.alert("망치 값 정제 실패.") return end

    local attempt = 0
    while count > 1 and attempt < 3 do
        attempt = attempt + 1
        gg.setVisible(false)
        for i = 5, 1, -1 do
            gg.toast(string.format("남은시간: %d초\n서둘러 망치의 개수를 바꾸세요.", i))
            gg.sleep(1000)
        end
        gg.setVisible(true)
        
        local refine_prompt = gg.prompt({string.format('[%d/3] 남은 주소: %d개\n바뀐 망치의 개수를 입력하세요.', attempt, count)}, {''}, {'number'})
        if not refine_prompt then return end
        gg.refineNumber(tonumber(refine_prompt[1]), gg.TYPE_DWORD)
        count = gg.getResultCount()
    end

    if count > 1 or count == 0 then 
        gg.alert("망치 값 정제 실패.") 
        return 
    end

    gg.toast("추출 중... 잠시만 기다려주세요.")
    
    local Hammer_Addr = gg.getResults(1)[1].address
    local PlayerModel_Base_Addr = trace_player_model(Hammer_Addr - 0x90)
    
    if not PlayerModel_Base_Addr then 
        gg.alert("PlayerModel 주소 찾기 실패.\n게임을 재시작한 뒤 다시 시도해주세요.") 
        return 
    end

    local final_output = {"[DUMP_VERSION]", "2"}
    
    local function append_data(data_table)
        for _, line in ipairs(data_table) do table.insert(final_output, line) end
    end

    local equip_model = read_qword(PlayerModel_Base_Addr + 0x220)

    append_data(extract_currency(PlayerModel_Base_Addr))
    append_data(extract_techtree(PlayerModel_Base_Addr))
    
    append_data(extract_forge(PlayerModel_Base_Addr))
    append_data(extract_skill_meta(PlayerModel_Base_Addr))
    append_data(extract_pet_meta(PlayerModel_Base_Addr))
    append_data(extract_mount_meta(PlayerModel_Base_Addr))
    
    append_data(extract_hidden_levels(equip_model))
    append_data(extract_roundrobin(equip_model))
    append_data(extract_equipment(equip_model))
    
    append_data(extract_skills_collection(PlayerModel_Base_Addr))
    append_data(extract_pets_eggs_collection(PlayerModel_Base_Addr))
    append_data(extract_mounts_collection(PlayerModel_Base_Addr))
    append_data(extract_skin_collection(PlayerModel_Base_Addr))
    table.insert(final_output, "[END]")
    table.insert(final_output, "")
    table.insert(final_output, "")

    local final_str = table.concat(final_output, "\n")
    gg.copyText(final_str)
    gg.alert("데이터 추출 완료!\n클립보드에 복사되었습니다.")
end

main()