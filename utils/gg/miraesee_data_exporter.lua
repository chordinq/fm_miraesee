function read_qword(addr)
    local t = {{address = addr, flags = gg.TYPE_QWORD}}
    t = gg.getValues(t)
    return t[1].value and tonumber(t[1].value) or 0
end

LINE_WIDTH = 32

function pad32(payload)
    local s = string.upper(tostring(payload or ""))
    if string.len(s) > LINE_WIDTH then
        return string.sub(s, 1, LINE_WIDTH)
    end
    while string.len(s) < LINE_WIDTH do
        s = s .. "0"
    end
    return s
end

function format_u64_hex16(value)
    local s = string.upper(string.format("%X", value or 0))
    if string.len(s) > 16 then
        s = string.sub(s, -16)
    end
    while string.len(s) < 16 do
        s = "0" .. s
    end
    return s
end

function read_bytes_hex(addr, count)
    if addr == 0 or count <= 0 then
        return ""
    end
    local batch = {}
    for i = 0, count - 1 do
        batch[#batch + 1] = {address = addr + i, flags = gg.TYPE_BYTE}
    end
    local vals = gg.getValues(batch)
    local parts = {}
    for i = 1, count do
        local b = vals[i].value
        if type(b) == "string" then
            b = tonumber(b:gsub("h$", ""), 16) or tonumber(b) or 0
        else
            b = tonumber(b) or 0
        end
        parts[#parts + 1] = string.format("%02X", b % 256)
    end
    return table.concat(parts)
end

function read_guid_hex32(addr)
    if addr == 0 then
        return string.rep("0", 32)
    end
    local hex = read_bytes_hex(addr, 16)
    while string.len(hex) < 32 do
        hex = "0" .. hex
    end
    if string.len(hex) > 32 then
        hex = string.sub(hex, -32)
    end
    return hex
end

function split_guid_hex32(hex)
    while string.len(hex) < 32 do
        hex = "0" .. hex
    end
    if string.len(hex) > 32 then
        hex = string.sub(hex, -32)
    end
    return string.sub(hex, 1, 16), string.sub(hex, 17, 32)
end

function append_stats_line(out, stats_ptr)
    table.insert(out, pad32("8" .. extract_stats_20char(stats_ptr)))
end

function append_timer_lines(out, timer_ptr)
    local start_ms, end_ms = read_timer_epoch_ms(timer_ptr)
    if end_ms > start_ms and start_ms > 0 then
        table.insert(out, pad32(string.format("9%016X", start_ms)))
        table.insert(out, pad32(string.format("A%016X", end_ms)))
    end
end

function read_dword(addr)
    local t = {{address = addr, flags = gg.TYPE_DWORD}}
    t = gg.getValues(t)
    return t[1].value and tonumber(t[1].value) or 0
end

function read_timer_epoch_ms(timer_ptr)
    if timer_ptr == 0 then
        return 0, 0
    end
    local start_ms = read_qword(timer_ptr + 0x10)
    local end_ms = read_qword(timer_ptr + 0x18)
    return start_ms, end_ms
end

function format_timer_suffix(timer_ptr)
    local start_ms, end_ms = read_timer_epoch_ms(timer_ptr)
    return string.format("%016X%016X", start_ms, end_ms)
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

function read_f64_raw(f64_ptr)
    if f64_ptr == 0 then
        return 0
    end
    if f64_ptr > 0x10000 then
        return read_qword(f64_ptr + 0x10)
    end
    return f64_ptr
end

function read_stat_contribution_raw(contrib)
    if contrib == 0 then
        return 0
    end
    -- IL: StatContribution.Value is inline F64 struct @ +0x18; F64.Raw is 8 bytes (long).
    return read_qword(contrib + 0x18)
end

-- MetaDictionary<ItemType, Guid> ChainEntry (IL + live dump):
--   entries array @ dict+0x18, count @ dict+0x20
--   slot = entries + 0x20 + i * 0x28
--   hashcode @ slot+0x10, key @ slot+0x14, Guid @ slot+0x18 (16 bytes)
function meta_dict_read_guid_map(dict_ptr)
    local map = {}
    if dict_ptr == 0 then
        return map
    end
    local count = read_dword(dict_ptr + 0x20)
    local entries = read_qword(dict_ptr + 0x18)
    if entries == 0 or count <= 0 then
        return map
    end
    local array_len = read_dword(entries + 0x18)
    local limit = array_len
    if limit <= 0 or limit > count + 4 then
        limit = count + 4
    end
    for i = 0, limit - 1 do
        local slot = entries + 0x20 + (i * 0x28)
        local hashcode = read_dword(slot + 0x10)
        if hashcode ~= -1 and hashcode ~= 0xFFFFFFFF then
            local key = read_dword(slot + 0x14)
            local guid_hex = read_guid_hex32(slot + 0x18)
            if guid_hex ~= string.rep("0", 32) then
                map[key] = guid_hex
            end
        end
    end
    return map
end

function extract_skin_stats_blob(stat_contrib_ptr, num_chunks)
    num_chunks = num_chunks or 2
    local chunks = {}
    for i = 1, num_chunks do
        chunks[i] = "0000000000"
    end
    if stat_contrib_ptr == 0 then
        return table.concat(chunks)
    end

    local list_ptr = read_qword(stat_contrib_ptr + 0x10)
    if list_ptr == 0 then
        return table.concat(chunks)
    end

    local count = read_dword(list_ptr + 0x18)
    local arr = read_qword(list_ptr + 0x10)
    if arr == 0 or count <= 0 then
        return table.concat(chunks)
    end

    local limit = math.min(count, num_chunks)
    for i = 0, limit - 1 do
        local contrib = read_qword(arr + 0x20 + (i * 8))
        if contrib ~= 0 then
            local f64_raw = read_stat_contribution_raw(contrib)
            if f64_raw ~= 0 then
                chunks[i + 1] = string.format("1%X%08X", i % 16, f64_raw % 4294967296)
            end
        end
    end
    return table.concat(chunks)
end

function extract_skin_stats_20char(stat_contrib_ptr)
    return extract_skin_stats_blob(stat_contrib_ptr, 2)
end

function append_skin_stats_line(out, stat_contrib_ptr)
    table.insert(out, pad32("8" .. extract_skin_stats_20char(stat_contrib_ptr)))
end

function extract_summon_meta(summon_ptr, asc_ptr)
    local count, level, seed = 0, 0, 0
    local asc_lvl = 0

    if summon_ptr ~= 0 then
        count = read_dword(summon_ptr + 0x10)
        level = read_dword(summon_ptr + 0x14)
        seed = read_qword(summon_ptr + 0x18)
    end

    if asc_ptr ~= 0 then
        asc_lvl = read_dword(asc_ptr + 0x14)
    end

    return pad32(string.format(
        "%02X%02X%s00000000000%X",
        level % 256,
        count % 256,
        format_u64_hex16(seed),
        asc_lvl % 16
    ))
end

function extract_pet_meta_line(summon_ptr, asc_ptr, hatch_slots_count)
    local count, level, seed = 0, 0, 0
    local asc_lvl = 0

    if summon_ptr ~= 0 then
        count = read_dword(summon_ptr + 0x10)
        level = read_dword(summon_ptr + 0x14)
        seed = read_qword(summon_ptr + 0x18)
    end

    if asc_ptr ~= 0 then
        asc_lvl = read_dword(asc_ptr + 0x14)
    end

    return pad32(string.format(
        "%02X%02X%s%02X00000000%X",
        level % 256,
        count % 256,
        format_u64_hex16(seed),
        hatch_slots_count % 256,
        asc_lvl % 16
    ))
end

function extract_forge_meta(forge_ptr, asc_ptr)
    local count, level, seed, highest_age = 0, 0, 0, 0
    local asc_lvl = 0

    if forge_ptr ~= 0 then
        seed = read_qword(forge_ptr + 0x18)
        level = read_dword(forge_ptr + 0x20)
        count = read_dword(forge_ptr + 0x3C)
        highest_age = read_dword(forge_ptr + 0x40)
    end

    if asc_ptr ~= 0 then
        asc_lvl = read_dword(asc_ptr + 0x14)
    end

    return pad32(string.format(
        "%02X%08X%s%02X000%X",
        level % 256,
        count % 4294967296,
        format_u64_hex16(seed),
        highest_age % 256,
        asc_lvl % 16
    ))
end

local PM_HAMMER_TO_ENTRIES = 0x90
local PM_SESSION_FILE = "miraesee_session.txt"
local PM_U32 = 0x100000000
local PM_PTR_HI_MIN = 0x1000
local PM_PTR_HI_MAX = 0x7FFF

local PM_OFF = {
    PLAYER_GAME_PAUSED = 0x20C,
    PLAYER_FORGE = 0x218,
    PLAYER_SKILL_COL = 0x240,
    FORGE_FORGE_COUNT = 0x3C,
}

local function pm_normalize_u64(v)
    if v == nil then
        return 0
    end
    if type(v) == "string" then
        v = tonumber(v:gsub("h$", ""):gsub("LL$", ""), 16) or tonumber(v) or 0
    else
        v = tonumber(v) or 0
    end
    if v < 0 then
        v = v + 0x10000000000000000
    end
    return v
end

local function pm_ptr_lo32(ptr)
    return pm_normalize_u64(ptr) % PM_U32
end

local function pm_ptr_hi32(ptr)
    return math.floor(pm_normalize_u64(ptr) / PM_U32) % PM_U32
end

local function pm_ptr_from_hi_lo(hi, lo)
    hi = math.floor(tonumber(hi) or 0) % PM_U32
    lo = math.floor(tonumber(lo) or 0) % PM_U32
    return hi * PM_U32 + lo
end

local function pm_ptr_add(base, offset)
    base = pm_normalize_u64(base)
    offset = pm_normalize_u64(offset)
    local lo = pm_ptr_lo32(base) + (offset % PM_U32)
    local hi = pm_ptr_hi32(base) + math.floor(offset / PM_U32)
    if lo >= PM_U32 then
        lo = lo - PM_U32
        hi = hi + 1
    end
    hi = hi % PM_U32
    return pm_ptr_from_hi_lo(hi, lo)
end

local function pm_is_valid_address(addr)
    addr = pm_normalize_u64(addr)
    if addr == 0 then
        return false
    end
    local hi = pm_ptr_hi32(addr)
    local lo = pm_ptr_lo32(addr)
    if hi < PM_PTR_HI_MIN or hi > PM_PTR_HI_MAX then
        return false
    end
    if lo >= PM_U32 then
        return false
    end
    return true
end

local function pm_read(addr, flags)
    if not pm_is_valid_address(addr) then
        return nil
    end
    addr = pm_ptr_from_hi_lo(pm_ptr_hi32(addr), pm_ptr_lo32(addr))
    local ok, t = pcall(function()
        return gg.getValues({ { address = addr, flags = flags } })
    end)
    if not ok or not t or not t[1] then
        return nil
    end
    return t[1].value
end

local function pm_read_qword(addr)
    return pm_normalize_u64(pm_read(addr, gg.TYPE_QWORD))
end

local function pm_read_dword(addr)
    local v = pm_read(addr, gg.TYPE_DWORD)
    return v and tonumber(v) or 0
end

local function pm_get_pointers(t_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
    local r = gg.getResults(200)
    local p = {}
    for _, v in ipairs(r) do
        if pm_read_qword(v.address - 0x8) == 0 or pm_read_qword(v.address + 0x8) == 0 then
            p[#p + 1] = v.address
        end
    end
    return p
end

local function pm_get_dict_pointers(t_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
    local r = gg.getResults(200)
    local p = {}
    for _, v in ipairs(r) do
        if pm_read_qword(v.address - 0x8) == 0 then
            p[#p + 1] = v.address
        end
    end
    return p
end

local function pm_get_entries_pointers(t_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
    local r = gg.getResults(200)
    local p = {}
    for _, v in ipairs(r) do
        if pm_read_qword(v.address - 0x10) == 0 then
            p[#p + 1] = v.address
        end
    end
    return p
end

local function pm_trace_player_model(entries_base)
    local entries_ptrs = pm_get_entries_pointers(entries_base)
    for _, e_ptr in ipairs(entries_ptrs) do
        for _, d_ptr in ipairs(pm_get_dict_pointers(e_ptr - 0x18)) do
            for _, c_ptr in ipairs(pm_get_pointers(d_ptr - 0x10)) do
                local player_base = c_ptr - 0x210
                local paused = pm_read_dword(pm_ptr_add(player_base, PM_OFF.PLAYER_GAME_PAUSED))
                if paused == 0 or paused == 1 then
                    local skill_col = pm_read_qword(pm_ptr_add(player_base, PM_OFF.PLAYER_SKILL_COL))
                    if skill_col > 0x10000000 then
                        return player_base
                    end
                end
            end
        end
    end
    return nil
end

local function pm_shared_paths(file_name)
    return {
        "/sdcard/Pictures/" .. file_name,
        "/mnt/shared/Pictures/" .. file_name,
        "/storage/emulated/0/Pictures/" .. file_name,
        "/sdcard/Download/" .. file_name,
        "/storage/emulated/0/Download/" .. file_name,
    }
end

local function pm_save_text(file_name, text)
    for _, path in ipairs(pm_shared_paths(file_name)) do
        local file = io.open(path, "w")
        if file then
            file:write(text)
            file:close()
            return true, path
        end
    end
    return false, nil
end

local function pm_load_session()
    for _, path in ipairs(pm_shared_paths(PM_SESSION_FILE)) do
        local f = io.open(path, "r")
        if f then
            local text = f:read("*a")
            f:close()
            local hammer = text:match("hammer=(%x+)")
            local player = text:match("player=(%x+)")
            local forge = text:match("forge=(%d+)")
            if player then
                return {
                    path = path,
                    hammer = hammer and tonumber(hammer, 16) or 0,
                    player = tonumber(player, 16),
                    forge_hint = forge and tonumber(forge) or 0,
                }
            end
        end
    end
    return nil
end

local function pm_save_session(hammer_addr, player_addr, forge_count)
    local text = string.format(
        "hammer=%X\nplayer=%X\nforge=%d\n",
        hammer_addr or 0,
        player_addr or 0,
        forge_count or 0
    )
    return pm_save_text(PM_SESSION_FILE, text)
end

local function pm_read_forge_count(player_addr)
    local forge_ptr = pm_read_qword(pm_ptr_add(player_addr, PM_OFF.PLAYER_FORGE))
    if forge_ptr == 0 then
        return 0
    end
    return pm_read_dword(pm_ptr_add(forge_ptr, PM_OFF.FORGE_FORGE_COUNT))
end

local function pm_validate_player_addr(player_addr)
    if player_addr == nil or player_addr == 0 then
        return nil
    end
    local paused = pm_read_dword(pm_ptr_add(player_addr, PM_OFF.PLAYER_GAME_PAUSED))
    if paused ~= 0 and paused ~= 1 then
        return nil
    end
    local skill_col = pm_read_qword(pm_ptr_add(player_addr, PM_OFF.PLAYER_SKILL_COL))
    if skill_col <= 0x10000000 then
        return nil
    end
    local forge_count = pm_read_forge_count(player_addr)
    if forge_count <= 0 then
        return nil
    end
    return player_addr
end

local function pm_try_session_player()
    local session = pm_load_session()
    if not session then
        return nil, "session_missing"
    end
    local player_addr = pm_validate_player_addr(session.player)
    if not player_addr then
        return nil, "session_stale"
    end
    return player_addr, "session"
end

local function pm_hammer_search_with_refine()
    local prompt = gg.prompt({ "현재 망치의 개수를 입력하세요." }, { "" }, { "number" })
    if not prompt then
        return nil, "cancelled"
    end

    local hammer_search = tonumber(prompt[1])
    gg.clearResults()
    gg.searchNumber(hammer_search, gg.TYPE_DWORD)
    local count = gg.getResultCount()
    if count == 0 then
        return nil, "hammer_hits_zero"
    end

    local attempt = 0
    while count > 1 and attempt < 3 do
        attempt = attempt + 1
        gg.setVisible(false)
        for i = 5, 1, -1 do
            gg.toast(string.format("남은시간: %d초\n서둘러 망치의 개수를 바꾸세요.", i))
            gg.sleep(1000)
        end
        gg.setVisible(true)

        local refine_prompt = gg.prompt({
            string.format("[%d/3] 남은 주소: %d개\n바뀐 망치의 개수를 입력하세요.", attempt, count),
        }, { "" }, { "number" })
        if not refine_prompt then
            return nil, "refine_cancelled"
        end

        gg.refineNumber(tonumber(refine_prompt[1]), gg.TYPE_DWORD)
        count = gg.getResultCount()
    end

    if count ~= 1 then
        return nil, "refine_failed hits=" .. tostring(count)
    end

    return gg.getResults(1)[1].address, "ok"
end

local function pm_resolve_player_via_hammer()
    gg.toast("망치 search...")
    local hammer_addr, status = pm_hammer_search_with_refine()
    if not hammer_addr then
        return nil, status
    end

    gg.toast("PlayerModel trace...")
    local player_addr = pm_trace_player_model(hammer_addr - PM_HAMMER_TO_ENTRIES)
    if not player_addr then
        return nil, "trace_failed"
    end

    local forge_count = pm_read_forge_count(player_addr)
    if forge_count <= 0 then
        return nil, "forge_count_zero"
    end

    pm_save_session(hammer_addr, player_addr, forge_count)
    return player_addr, "hammer"
end

function resolve_player_model()
    gg.toast("Session...")
    local player_addr, status = pm_try_session_player()
    if player_addr then
        return player_addr, status
    end
    return pm_resolve_player_via_hammer()
end

function save_finder_report(report)
    local text = table.concat(report, "\n")
    local paths = {
        "/sdcard/Pictures/miraesee_exporter_finder.txt",
        "/mnt/shared/Pictures/miraesee_exporter_finder.txt",
        "/storage/emulated/0/Pictures/miraesee_exporter_finder.txt",
    }
    for _, path in ipairs(paths) do
        local file = io.open(path, "w")
        if file then
            file:write(text)
            file:close()
            return path
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

function extract_techtree_timers(player_ptr)
    local out = {"[TECH_TREE_TIMERS]"}
    local model = read_qword(player_ptr + 0x250)
    if model == 0 then return out end
    local dict = read_qword(model + 0x10)
    if dict == 0 then return out end

    local count = read_dword(dict + 0x20)
    local entries = read_qword(dict + 0x18)

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
                    local timer_ptr = read_qword(n_mdl + 0x18)
                    local start_ms, end_ms = read_timer_epoch_ms(timer_ptr)
                    if end_ms > start_ms and start_ms > 0 then
                        table.insert(out, pad32(string.format("%X%02X%016X", t_type % 16, n_id % 256, start_ms)))
                        table.insert(out, pad32(string.format("A%016X", end_ms)))
                    end
                end
            end
        end
    end
    return out
end

function extract_forge(player_ptr)
    local forge_ptr = read_qword(player_ptr + 0x218)
    local asc_ptr = forge_ptr ~= 0 and read_qword(forge_ptr + 0x50) or 0
    local out = {"[FORGE]", extract_forge_meta(forge_ptr, asc_ptr)}
    local timer_ptr = forge_ptr ~= 0 and read_qword(forge_ptr + 0x28) or 0
    append_timer_lines(out, timer_ptr)
    return out
end

function extract_skill_meta(player_ptr)
    local col = read_qword(player_ptr + 0x240)
    local sum_ptr = col ~= 0 and read_qword(col + 0x20) or 0
    local asc_ptr = col ~= 0 and read_qword(col + 0x28) or 0
    return {"[SKILL]", extract_summon_meta(sum_ptr, asc_ptr)}
end

function extract_pet_meta(player_ptr)
    local col = read_qword(player_ptr + 0x258)
    local hatch_slots = col ~= 0 and read_dword(col + 0x20) or 0
    local sum_ptr = col ~= 0 and read_qword(col + 0x28) or 0
    local asc_ptr = col ~= 0 and read_qword(col + 0x30) or 0
    return {"[PET]", extract_pet_meta_line(sum_ptr, asc_ptr, hatch_slots)}
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
                table.insert(out, pad32(header .. prog))
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
                local lvl = read_dword(model + 0x28)
                local exp = read_dword(model + 0x2C)
                local is_eq = read_dword(model + 0x30) % 256
                local slot = read_dword(model + 0x34) % 256
                local is_locked = read_dword(model + 0x40) % 256
                table.insert(out, pad32(string.format(
                    "2%X%02X%08X%08X%02X%02X%02X",
                    rarity % 16, p_id % 256, lvl, exp, is_eq, slot, is_locked
                )))
                append_stats_line(out, read_qword(model + 0x38))
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
                local rarity = read_dword(model + 0x20) % 16
                local is_eq = read_dword(model + 0x30) % 256
                local slot = read_dword(model + 0x34) % 256
                local seed = read_qword(model + 0x38)
                table.insert(out, pad32(string.format("3%X%02X%02X%016X", rarity, is_eq, slot, seed)))
                append_timer_lines(out, read_qword(model + 0x28))
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
                local lvl = read_dword(model + 0x28)
                local exp = read_dword(model + 0x2C)
                local is_eq = read_dword(model + 0x30) % 256
                local is_locked = read_dword(model + 0x40) % 256
                table.insert(out, pad32(string.format(
                    "4%X%02X%08X%08X%02X%02X",
                    read_dword(m_id_ptr + 0x10) % 16, read_dword(m_id_ptr + 0x14) % 256,
                    lvl, exp, is_eq, is_locked
                )))
                append_stats_line(out, read_qword(model + 0x38))
            end
        end
    end
    return out
end

-- Dump v4: every data line is 32 hex chars.
-- Primary: 2=pet 3=egg 4=mount 5=skin 5E=exporter rev 5F=skin meta
-- Continuation: 8=stats (pet/mount=MetaDictionary, skin=StatContributions list)
-- Skin primary is_eq nibble: derived from EquippedSkinGuids GUID match (IL IsEquipped),
-- not a field on PlayerSkinModel. No per-skin GUID lines on the wire.
local SKIN_EXPORT_REV = 6

function extract_skin_collection(player_ptr)
    local out = {"[SKIN_COLLECTION]"}
    local col = read_qword(player_ptr + 0x290)
    if col == 0 then return out end

    local skins_dict   = read_qword(col + 0x10)
    local eq_guid_dict = read_qword(col + 0x20)
    local skins_seed   = read_qword(col + 0x30)

    table.insert(out, pad32(string.format("5F%s", format_u64_hex16(skins_seed))))
    table.insert(out, pad32(string.format("5E%030X", SKIN_EXPORT_REV)))

    local eq_map = meta_dict_read_guid_map(eq_guid_dict)

    if skins_dict == 0 then
        return out
    end

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
                        local guid_hex = read_guid_hex32(model + 0x10)
                        local sid_ptr  = read_qword(model + 0x20)
                        local skin_idx = sid_ptr ~= 0 and read_dword(sid_ptr + 0x14) or 0
                        local level    = read_dword(model + 0x30)
                        local exp      = read_dword(model + 0x34)
                        local stat_ptr = read_qword(model + 0x28)

                        local equipped_hex = eq_map[item_type]
                        local is_eq = (equipped_hex and equipped_hex == guid_hex) and 1 or 0

                        table.insert(out, pad32(string.format(
                            "5%X%02X%X%02X%08X",
                            item_type % 16, skin_idx % 256, is_eq,
                            level % 256, exp % 4294967296
                        )))
                        append_skin_stats_line(out, stat_ptr)
                    end
                end
            end
        end
    end
    return out
end

function save_dump_to_shared_folder(text)
    local file_name = "user_dump.txt"
    local paths = {
        "/sdcard/Pictures/" .. file_name,
        "/mnt/shared/Pictures/" .. file_name,
        "/storage/emulated/0/Pictures/" .. file_name,
        "/sdcard/Download/" .. file_name,
    }
    for _, path in ipairs(paths) do
        local file = io.open(path, "w")
        if file then
            file:write(text)
            file:close()
            return true, path
        end
    end
    return false, nil
end

function main()
    gg.clearResults()
    gg.setVisible(false)

    local report = {
        "[MIRAESEE DATA EXPORTER]",
        "mode=session_then_hammer",
    }

    local PlayerModel_Base_Addr, resolve_status = resolve_player_model()
    gg.clearResults()

    if not PlayerModel_Base_Addr then
        report[#report + 1] = "resolve_status=" .. tostring(resolve_status)
        gg.setVisible(true)
        save_finder_report(report)
        gg.alert(
            "PlayerModel 주소 찾기 실패.\n\n" ..
            "상태: " .. tostring(resolve_status) .. "\n\n" ..
            "메인 화면 로그인 후 재시도하거나\n" ..
            "망치 search/refine 단계를 완료해주세요.\n\n" ..
            "로그: Pictures/miraesee_exporter_finder.txt"
        )
        return
    end

    report[#report + 1] = "resolve_status=" .. tostring(resolve_status)
    report[#report + 1] = string.format("player=0x%X", PlayerModel_Base_Addr)
    gg.toast("추출 중... 잠시만 기다려주세요.")

    local final_output = {"[DUMP_VERSION]", "4"}
    
    local function append_data(data_table)
        for _, line in ipairs(data_table) do table.insert(final_output, line) end
    end

    local equip_model = read_qword(PlayerModel_Base_Addr + 0x220)

    append_data(extract_currency(PlayerModel_Base_Addr))
    append_data(extract_techtree(PlayerModel_Base_Addr))
    append_data(extract_techtree_timers(PlayerModel_Base_Addr))
    
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
    local line_count = #final_output
    local char_count = string.len(final_str)
    save_dump_to_shared_folder(final_str)
    gg.copyText(final_str, false)
    gg.setVisible(true)

    gg.alert(string.format(
        "데이터 추출 완료! (%d줄 / %d자)\n\n클립보드에 복사되지 않는 경우\n공유폴더(Ctrl + 5) → user_dump.txt를 확인해보세요.",
        line_count,
        char_count
    ))
end

main()