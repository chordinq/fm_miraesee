local OFF = {
    PLAYER_LIVE_OPS_EVENTS = 0x1C8,
    LIVE_OPS_EVENT_MODELS  = 0x10,
    SS_EVENT_MINI_GAME     = 0x50,
    MINI_GAME_FINAL_X      = 0x10,
    MINI_GAME_STATE        = 0x18,
    MINI_GAME_SEED         = 0x20,
    STATE_LAST_SOLID_TILE  = 0x18,
}

local WAIT_SECONDS = 5
local POLL_SECONDS = 15
local POLL_INTERVAL_MS = 500

function read_qword(addr)
    local t = {{address = addr, flags = gg.TYPE_QWORD}}
    t = gg.getValues(t)
    local v = t[1].value
    if v == nil then
        return 0
    end
    if type(v) == "string" then
        return tonumber(v, 16) or 0
    end
    v = tonumber(v) or 0
    if v < 0 then
        v = v + 0x10000000000000000
    end
    return v
end

function read_dword(addr)
    local t = {{address = addr, flags = gg.TYPE_DWORD}}
    t = gg.getValues(t)
    return t[1].value and tonumber(t[1].value) or 0
end

function read_int32(addr)
    local v = read_dword(addr)
    if v >= 0x80000000 then
        return v - 0x100000000
    end
    return v
end

function get_pointers(t_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
    local r = gg.getResults(200)
    local p = {}
    for _, v in ipairs(r) do
        if read_qword(v.address - 0x8) == 0 or read_qword(v.address + 0x8) == 0 then
            table.insert(p, v.address)
        end
    end
    return p
end

function get_dict_pointers(t_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
    local r = gg.getResults(200)
    local p = {}
    for _, v in ipairs(r) do
        if read_qword(v.address - 0x8) == 0 then
            table.insert(p, v.address)
        end
    end
    return p
end

function get_entries_pointers(t_addr)
    gg.clearResults()
    gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
    local r = gg.getResults(200)
    local p = {}
    for _, v in ipairs(r) do
        if read_qword(v.address - 0x10) == 0 then
            table.insert(p, v.address)
        end
    end
    return p
end

function trace_player_model(entries_base)
    local entries_ptrs = get_entries_pointers(entries_base)
    for _, e_ptr in ipairs(entries_ptrs) do
        for _, d_ptr in ipairs(get_dict_pointers(e_ptr - 0x18)) do
            for _, c_ptr in ipairs(get_pointers(d_ptr - 0x10)) do
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

local DICT_COUNT_OFF   = 0x20
local DICT_ENTRIES_OFF = 0x18
local ARRAY_LENGTH_OFF = 0x18

local LIVE_OPS_EVENT_DICT = {
    ENTRY_STRIDE   = 0x30,
    ARRAY_BASE     = 0x20,
    HASHCODE_OFF   = 0x10,
    VALUE_IN_ENTRY = 0x28,
}

function ptr_hi32(ptr)
    return math.floor(ptr / 0x100000000) % 0x100000000
end

function is_ptr(ptr)
    return ptr ~= 0 and ptr >= 0x10000000 and ptr <= 0x0000FFFFFFFFFFFF
end

function looks_like_heap_ptr(ptr, ref_ptr)
    if not is_ptr(ptr) then
        return false
    end
    if ref_ptr ~= 0 then
        return ptr_hi32(ptr) == ptr_hi32(ref_ptr)
    end
    return ptr_hi32(ptr) ~= 0
end

function is_plausible_event_model(event_model, ref_ptr)
    if not looks_like_heap_ptr(event_model, ref_ptr) then
        return false
    end
    return is_ptr(read_qword(event_model))
end

function is_mini_game_ongoing(mini_ptr)
    local state_ptr = read_qword(mini_ptr + OFF.MINI_GAME_STATE)
    if state_ptr == 0 or state_ptr < 0x10000000 then
        return false
    end
    return read_dword(state_ptr + 0x10) == 0
end

function read_event_model_from_slot(entries, slot, ref_ptr)
    local cfg = LIVE_OPS_EVENT_DICT
    local slot_base = entries + cfg.ARRAY_BASE + slot * cfg.ENTRY_STRIDE
    if read_dword(slot_base + cfg.HASHCODE_OFF) == 0 then
        return 0
    end
    local value = read_qword(slot_base + cfg.VALUE_IN_ENTRY)
    if is_plausible_event_model(value, ref_ptr) then
        return value
    end
    for _, off in ipairs({0x28, 0x20, 0x18}) do
        value = read_qword(slot_base + off)
        if is_plausible_event_model(value, ref_ptr) then
            return value
        end
    end
    return 0
end

function foreach_live_ops_event_model(dict, ref_ptr, fn)
    if dict == 0 then
        return 0
    end

    local entries = read_qword(dict + DICT_ENTRIES_OFF)
    if entries == 0 then
        return 0
    end

    local count = read_dword(dict + DICT_COUNT_OFF)
    local capacity = read_dword(entries + ARRAY_LENGTH_OFF)
    if capacity <= 0 then
        capacity = count
    end
    if capacity <= 0 then
        return 0
    end
    if capacity > 256 then
        capacity = 256
    end

    local cfg = LIVE_OPS_EVENT_DICT
    local visited = 0
    for i = 0, capacity - 1 do
        local event_model = read_event_model_from_slot(entries, i, ref_ptr)
        if event_model ~= 0 then
            visited = visited + 1
            if fn(event_model, i) then
                return visited
            end
        end
    end

    return visited
end

function looks_like_seed(seed, ref_ptr)
    if seed == 0 then
        return false
    end
    if is_ptr(seed) then
        return false
    end
    if ref_ptr ~= 0 and ptr_hi32(seed) == ptr_hi32(ref_ptr) then
        return false
    end
    return true
end

function is_active_mini_game(mini_ptr, ref_ptr)
    if mini_ptr == 0 or mini_ptr < 0x10000000 then
        return false
    end
    if ref_ptr and ref_ptr ~= 0 and not looks_like_heap_ptr(mini_ptr, ref_ptr) then
        return false
    end
    if not is_mini_game_ongoing(mini_ptr) then
        return false
    end

    local seed = read_qword(mini_ptr + OFF.MINI_GAME_SEED)
    if seed == 0 then
        return false
    end
    if ref_ptr and ref_ptr ~= 0 and not looks_like_seed(seed, ref_ptr) then
        return false
    end

    return true
end

function is_complete_mini_game(mini_ptr, ref_ptr)
    if not is_active_mini_game(mini_ptr, ref_ptr) then
        return false
    end
    local final_x = read_int32(mini_ptr + OFF.MINI_GAME_FINAL_X)
    return final_x >= 0 and final_x <= 128
end

function is_plausible_mini_game(mini_ptr, ref_ptr)
    if not is_complete_mini_game(mini_ptr, ref_ptr) then
        return false
    end

    local final_x = read_int32(mini_ptr + OFF.MINI_GAME_FINAL_X)
    local state_ptr = read_qword(mini_ptr + OFF.MINI_GAME_STATE)
    if state_ptr == 0 or state_ptr < 0x10000000 then
        return true
    end

    local tile_x = read_int32(state_ptr + OFF.STATE_LAST_SOLID_TILE)
    local tile_y = read_int32(state_ptr + OFF.STATE_LAST_SOLID_TILE + 4)
    if tile_x < -1 or tile_x > final_x + 1 then
        return false
    end
    if tile_y < -1 or tile_y > 32 then
        return false
    end

    return true
end

function read_mini_game(mini_ptr)
    local state_ptr = read_qword(mini_ptr + OFF.MINI_GAME_STATE)
    local last_x, last_y = -1, -1
    if state_ptr ~= 0 then
        last_x = read_int32(state_ptr + OFF.STATE_LAST_SOLID_TILE)
        last_y = read_int32(state_ptr + OFF.STATE_LAST_SOLID_TILE + 4)
    end
    local final_x = read_int32(mini_ptr + OFF.MINI_GAME_FINAL_X)
    return {
        mini_ptr = mini_ptr,
        final_x = final_x,
        seed = read_qword(mini_ptr + OFF.MINI_GAME_SEED),
        last_x = last_x,
        last_y = last_y,
        state_ptr = state_ptr,
        ongoing = is_mini_game_ongoing(mini_ptr),
        seed_only = final_x < 0,
    }
end

function try_mini_game_from_event(event_model, ref_ptr)
    if event_model == 0 then
        return nil
    end
    local mini_ptr = read_qword(event_model + OFF.SS_EVENT_MINI_GAME)
    if is_active_mini_game(mini_ptr, ref_ptr) then
        return read_mini_game(mini_ptr)
    end
    return nil
end

function find_active_mini_game(player_ptr)
    local live_ops = read_qword(player_ptr + OFF.PLAYER_LIVE_OPS_EVENTS)
    if live_ops == 0 then
        return nil
    end

    local dict = read_qword(live_ops + OFF.LIVE_OPS_EVENT_MODELS)
    if dict == 0 then
        return nil
    end

    local best = nil
    foreach_live_ops_event_model(dict, live_ops, function(event_model)
        local info = try_mini_game_from_event(event_model, live_ops)
        if info then
            best = info
            return true
        end
        return false
    end)

    return best
end

function find_active_mini_game_or_error(player_ptr)
    local live_ops = read_qword(player_ptr + OFF.PLAYER_LIVE_OPS_EVENTS)
    if live_ops == 0 then
        return nil, "LiveOpsEvents 없음 (player+0x1C8)"
    end

    local dict = read_qword(live_ops + OFF.LIVE_OPS_EVENT_MODELS)
    if dict == 0 then
        return nil, "EventModels dict 없음 (liveOps+0x10)"
    end

    local entries = read_qword(dict + DICT_ENTRIES_OFF)
    if entries == 0 then
        return nil, "EventModels entries 없음"
    end

    local info = find_active_mini_game(player_ptr)
    if info then
        return info, nil
    end

    local count = read_dword(dict + DICT_COUNT_OFF)
    local capacity = read_dword(entries + ARRAY_LENGTH_OFF)
    local event_model = read_event_model_from_slot(entries, 0, live_ops)
    local mini_ptr = event_model ~= 0 and read_qword(event_model + OFF.SS_EVENT_MINI_GAME) or 0
    local ongoing = mini_ptr ~= 0 and is_mini_game_ongoing(mini_ptr) or false
    local final_x = mini_ptr ~= 0 and read_int32(mini_ptr + OFF.MINI_GAME_FINAL_X) or -1
    local seed = mini_ptr ~= 0 and read_qword(mini_ptr + OFF.MINI_GAME_SEED) or 0
    return nil, string.format(
        "SteppingStoneMiniGame 미발견\n" ..
        "LiveOps=0x%X dict=0x%X count=%d capacity=%d\n" ..
        "EventModel=0x%X MiniGame(+0x50)=0x%X ongoing=%s\n" ..
        "seed=%016X final_x=%d\n" ..
        "→ 런 시작 직후~플레이 중에만 seed 유효\n" ..
        "  FinalX=-1은 첫 열 loose (seed는 읽힐 수 있음)\n" ..
        "  종료 후 EndReason set → ongoing=false",
        live_ops,
        dict,
        count,
        capacity,
        event_model,
        mini_ptr,
        ongoing and "true" or "false",
        seed,
        final_x
    )
end

function verify_live_ops_chain(player_ptr)
    local lines = {
        string.format("PlayerModel = 0x%X", player_ptr),
        string.format("  +0x210 CurrencyModel = 0x%X", read_qword(player_ptr + 0x210)),
        string.format("  +0x240 SkillCollection = 0x%X", read_qword(player_ptr + 0x240)),
        string.format("  +0x1C8 LiveOpsEvents  = 0x%X  <-- IL: get_LiveOpsEvents", read_qword(player_ptr + OFF.PLAYER_LIVE_OPS_EVENTS)),
    }

    local live_ops = read_qword(player_ptr + OFF.PLAYER_LIVE_OPS_EVENTS)
    if live_ops == 0 then
        table.insert(lines, "  LiveOpsEvents NULL → 0x1C8 체인 끊김")
        return table.concat(lines, "\n")
    end

    local dict = read_qword(live_ops + OFF.LIVE_OPS_EVENT_MODELS)
    local count = dict ~= 0 and read_dword(dict + DICT_COUNT_OFF) or 0
    local entries = dict ~= 0 and read_qword(dict + DICT_ENTRIES_OFF) or 0
    local capacity = entries ~= 0 and read_dword(entries + ARRAY_LENGTH_OFF) or 0

    table.insert(lines, string.format("  LiveOps+0x10 EventModels = 0x%X  <-- IL: get_EventModels", dict))
    table.insert(lines, string.format("  dict count=%d capacity=%d", count, capacity))
    table.insert(lines, string.format(
        "  dict layout: MetaGuid stride=0x%X hash=entry+0x10 guid=entry+0x18 value=entry+0x28",
        LIVE_OPS_EVENT_DICT.ENTRY_STRIDE
    ))

    local cfg = LIVE_OPS_EVENT_DICT
    for i = 0, math.min(capacity, 8) - 1 do
        if capacity <= 0 then
            break
        end
        local slot_base = entries + cfg.ARRAY_BASE + i * cfg.ENTRY_STRIDE
        local hash = read_dword(slot_base + cfg.HASHCODE_OFF)
        local guid_lo = read_qword(slot_base + 0x18)
        local event_model = read_event_model_from_slot(entries, i, live_ops)
        if hash ~= 0 or guid_lo ~= 0 or event_model ~= 0 then
            table.insert(lines, string.format(
                "  raw slot[%d] hash=0x%X guid_lo=0x%X EventModel=0x%X",
                i, hash, guid_lo, event_model
            ))
        end
    end

    local slot_hits = 0
    foreach_live_ops_event_model(dict, live_ops, function(event_model, slot)
        slot_hits = slot_hits + 1
        local mini = read_qword(event_model + OFF.SS_EVENT_MINI_GAME)
        table.insert(lines, string.format(
            "  slot[%d] EventModel=0x%X  +0x50 MiniGame=0x%X",
            slot, event_model, mini
        ))
        if is_active_mini_game(mini, live_ops) then
            table.insert(lines, string.format(
                "    -> seed=%016X final_x=%d",
                read_qword(mini + OFF.MINI_GAME_SEED),
                read_int32(mini + OFF.MINI_GAME_FINAL_X)
            ))
        end
        return false
    end)

    if slot_hits == 0 then
        table.insert(lines, "  EventModels 슬롯 비어 있음 (이벤트 기간/로드 확인)")
    end

    return table.concat(lines, "\n")
end

function resolve_player_ptr()
    local prompt = gg.prompt({"현재 망치의 개수를 입력하세요."}, {""}, {"number"})
    if not prompt then
        return nil
    end

    gg.searchNumber(tonumber(prompt[1]), gg.TYPE_DWORD)
    local count = gg.getResultCount()
    if count == 0 then
        gg.alert("망치 값 정제 실패.")
        return nil
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

        local refine_prompt = gg.prompt(
            {string.format("[%d/3] 남은 주소: %d개\n바뀐 망치의 개수를 입력하세요.", attempt, count)},
            {""},
            {"number"}
        )
        if not refine_prompt then
            return nil
        end
        gg.refineNumber(tonumber(refine_prompt[1]), gg.TYPE_DWORD)
        count = gg.getResultCount()
    end

    if count > 1 or count == 0 then
        gg.alert("망치 값 정제 실패.")
        return nil
    end

    local hammer_addr = gg.getResults(1)[1].address
    local player_ptr = trace_player_model(hammer_addr - 0x90)
    if not player_ptr then
        gg.alert("PlayerModel 주소 찾기 실패.\n게임을 재시작한 뒤 다시 시도해주세요.")
        return nil
    end

    return player_ptr
end

function wait_for_stepping_run(player_ptr)
    gg.setVisible(false)
    for i = WAIT_SECONDS, 1, -1 do
        gg.toast(string.format("%d초 안에 디딤돌 런을 시작하세요!", i))
        gg.sleep(1000)
    end
    gg.setVisible(true)

    local polls = math.floor(POLL_SECONDS * 1000 / POLL_INTERVAL_MS)
    for i = 1, polls do
        local info = find_active_mini_game(player_ptr)
        if info then
            return info, nil
        end
        gg.toast(string.format("디딤돌 런 대기 중... (%d/%d)", i, polls))
        gg.sleep(POLL_INTERVAL_MS)
    end

    local _, err = find_active_mini_game_or_error(player_ptr)
    if err then
        return nil, err
    end

    return nil, string.format(
        "%d초 안에 디딤돌 런이 감지되지 않았습니다.\n토큰 소모 후 런이 시작됐는지 확인하세요.",
        WAIT_SECONDS + POLL_SECONDS
    )
end

function format_result(info, player_ptr)
    local safe_line
    if info.final_x >= 0 then
        safe_line = string.format("safe_columns=0..%d\nfall_from_column=%d\n", info.final_x, info.final_x + 1)
    else
        safe_line = "safe_columns=none (FinalX=-1, column 0 loose)\n"
    end
    return string.format(
        "[STEPPING_STONE]\n" ..
        "seed=%016X\n" ..
        "final_x=%d\n" ..
        "%s" ..
        "last_solid_tile=(%d,%d)\n" ..
        "player=0x%X\n" ..
        "mini_game=0x%X\n" ..
        "state=0x%X",
        info.seed,
        info.final_x,
        safe_line,
        info.last_x,
        info.last_y,
        player_ptr,
        info.mini_ptr,
        info.state_ptr
    )
end

function main()
    gg.clearResults()
    gg.alert(
        "디딤돌 시드 추출기\n\n" ..
        "1) 메인 화면에서 실행 (디딤돌 안에 있지 않은 상태)\n" ..
        "2) 망치 개수로 PlayerModel 고정\n" ..
        "3) 5초 안에 디딤돌 런 시작\n" ..
        "4) 시드 / FinalX 자동 추출"
    )

    gg.toast("PlayerModel 탐색 중...")
    local player_ptr = resolve_player_ptr()
    if not player_ptr then
        return
    end

    gg.toast(string.format("PlayerModel: 0x%X", player_ptr))

    local chain_report = verify_live_ops_chain(player_ptr)
    gg.copyText(chain_report, false)
    gg.alert(
        "LiveOps 체인 검증 (클립보드 복사됨)\n\n" ..
        chain_report .. "\n\n" ..
        "0x1C8 근거: PlayerModelBase.get_LiveOpsEvents IL\n" ..
        "  return *(param_1 + 0x1C8)\n\n" ..
        "확인 OK 조건:\n" ..
        "  LiveOpsEvents / EventModels 포인터가 0x7xxxxxxxx대\n" ..
        "  디딤돌 기간이면 count>=1"
    )

    local info, err = wait_for_stepping_run(player_ptr)
    if not info then
        gg.alert(err)
        return
    end

    local text = format_result(info, player_ptr)
    gg.copyText(text, false)
    if info.final_x >= 0 then
        gg.alert(
            string.format(
                "시드 추출 완료\n\n" ..
                "Seed: %016X\n" ..
                "FinalX: %d → X=0..%d 열까지 안전, X=%d에서 낙사\n" ..
                "현재 타일: (%d,%d)\n\n" ..
                "클립보드에 복사했습니다.",
                info.seed,
                info.final_x,
                info.final_x,
                info.final_x + 1,
                info.last_x,
                info.last_y
            )
        )
    else
        gg.alert(
            string.format(
                "시드 추출 (FinalX=-1)\n\n" ..
                "Seed: %016X\n" ..
                "FinalX=-1 → 0열(첫 칸)부터 loose, 진행 불가\n" ..
                "현재 타일: (%d,%d)\n\n" ..
                "클립보드에 복사했습니다.",
                info.seed,
                info.last_x,
                info.last_y
            )
        )
    end
end

main()
