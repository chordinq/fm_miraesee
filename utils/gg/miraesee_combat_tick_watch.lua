-- Miraesee 2.6.0 — MainBattle / UnitEntity combat FSM watcher (GameGuardian)
--
-- IL chain (PlayerModel.GameTick → MainBattleModel.Update → CombatScene.NextFrame):
--   PlayerModel.GameTick          decompiled.c ~13881482  dt = F64.Ratio(1,10)
--   BattleMode==MainBattle(1)     player+0x2A0
--   MainBattleModel.Update        ~13810955  when State==Running(3)
--   CombatScene.NextFrame         ~13811129
--   AttacksSystem.HandleUnits     unit AttackTimer FSM
--
-- Pointer chain:
--   PlayerModel +0x58        → CurrentTick (i64, Metaplay logic tick)
--   PlayerModel +0x298  → MainBattleModel
--   PlayerModel +0x2A0  → BattleMode (int)
--   MainBattleModel +0x10 → CombatScene (CurrentCombat)
--   MainBattleModel +0x18 → BattleState (byte)
--   MainBattleModel +0x3C → CurrentWaveIdx
--   MainBattleModel +0x50 → WaveTimer (F64)
--   CombatScene +0x10     → Entities
--   Entities +0x14          → player entity id
--   Entities +0x20          → MetaDictionary<int, UnitEntity>
--   UnitEntity +0x59        → IsPlayer
--   UnitEntity +0x60/+0x70/+0x80/+0x120 → AttackDuration / WindUp / AttackTimer / Hp (FD6)
--   UnitEntity +0x90              → CombatState (Idle=0 WindingUp=1 OnCooldown=2)
--   UnitEntity +0xF0        → TargetInAttackRange
--   UnitEntity +0x2A8       → DoubleAttack pending
--
-- PlayerModel: miraesee_session.txt 우선 → 실패 시 망치 search/refine + 세션 저장.
--
-- Output (2ms poll, batched memory reads):
--   GameTick 변화 또는 CombatState/AttackTimer 변화 시 snapshot
--   catch-up 루프로 snapshot 중 밀린 tick 재샘플 (최대 CATCHUP_MAX_BURST)
--   print() — 변화마다 GG 로그 (기본 off)
--   gg.toast() — 루프당 최신 상태 1회만 갱신

local VERSION_TAG = "2.6.0"
local HAMMER_TO_ENTRIES = 0x90
local SESSION_FILE = "miraesee_session.txt"
local GAME_TICK_POLL_MS = 2
local CATCHUP_MAX_BURST = 8
local MAX_DICT_SCAN = 64

-- 화면 toast — 루프마다 최신 스냅샷 1회 (덮어쓰기)
local MONITOR_TOAST_LATEST = true
-- GG 로그 — FSM/틱 변화마다 한 줄 (스크롤 쌓임)
local MONITOR_PRINT_EVERY_CHANGE = false
-- toast 앞쪽 여백 줄 수 (기기마다 8~12 권장)
local TOAST_TOP_PAD_LINES = 10

local OFF = {
	PLAYER_CURRENT_TICK = 0x58,
	PLAYER_FORGE = 0x218,
	PLAYER_SKILL_COL = 0x240,
	PLAYER_MAIN_BATTLE = 0x298,
	PLAYER_BATTLE_MODE = 0x2A0,
	PLAYER_GAME_PAUSED = 0x20C,
	FORGE_FORGE_COUNT = 0x3C,
	MB_COMBAT_SCENE = 0x10,
	MB_BATTLE_STATE = 0x18,
	MB_CURRENT_WAVE = 0x3C,
	MB_WAVE_TIMER = 0x50,
	CS_ENTITIES = 0x10,
	ENT_PLAYER_ID = 0x14,
	ENT_UNITS_DICT = 0x20,
	UNIT_ID = 0x10,
	UNIT_IS_PLAYER = 0x59,
	UNIT_ATTACK_DURATION = 0x60,
	UNIT_WINDUP = 0x70,
	UNIT_ATTACK_TIMER = 0x80,
	UNIT_COMBAT_STATE = 0x90,
	UNIT_HP = 0x120,
	UNIT_TARGET_IN_RANGE = 0xF0,
	UNIT_DOUBLE_ATTACK = 0x2A8,
}

local BATTLE_MODE = {
	[0] = "None",
	[1] = "Main",
	[2] = "Dungeon",
	[3] = "Pvp",
	[4] = "GuildWar",
	[5] = "Mission",
}

local BATTLE_STATE = {
	[0] = "None",
	[1] = "Ready",
	[2] = "WaveFin",
	[3] = "Run",
	[4] = "Pause",
	[5] = "Won",
	[6] = "Lost",
}

local COMBAT_STATE = {
	[0] = "Idle",
	[1] = "WindingUp",
	[2] = "OnCooldown",
}

local COMBAT_STATE_KO = {
	[0] = "휴식",
	[1] = "와인드업",
	[2] = "쿨다운",
}

local F64_SCALE = 4294967296.0
local U32 = 0x100000000
local PTR_HI_MIN = 0x1000
local PTR_HI_MAX = 0x7FFF

local function normalize_u64(v)
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

local function qword_from_gg(v)
	return normalize_u64(v)
end

local function ptr_lo32(ptr)
	return normalize_u64(ptr) % U32
end

local function ptr_hi32(ptr)
	return math.floor(normalize_u64(ptr) / U32) % U32
end

local function ptr_from_hi_lo(hi, lo)
	hi = math.floor(tonumber(hi) or 0) % U32
	lo = math.floor(tonumber(lo) or 0) % U32
	return hi * U32 + lo
end

local function ptr_add(base, offset)
	base = normalize_u64(base)
	offset = normalize_u64(offset)
	local lo = ptr_lo32(base) + (offset % U32)
	local hi = ptr_hi32(base) + math.floor(offset / U32)
	if lo >= U32 then
		lo = lo - U32
		hi = hi + 1
	end
	hi = hi % U32
	return ptr_from_hi_lo(hi, lo)
end

local function is_valid_gg_address(addr)
	addr = normalize_u64(addr)
	if addr == 0 then
		return false
	end
	local hi = ptr_hi32(addr)
	local lo = ptr_lo32(addr)
	if hi < PTR_HI_MIN or hi > PTR_HI_MAX then
		return false
	end
	if lo >= U32 then
		return false
	end
	return true
end

local function gg_read(addr, flags)
	if not is_valid_gg_address(addr) then
		return nil
	end
	addr = ptr_from_hi_lo(ptr_hi32(addr), ptr_lo32(addr))
	local ok, t = pcall(function()
		return gg.getValues({ { address = addr, flags = flags } })
	end)
	if not ok or not t or not t[1] then
		return nil
	end
	return t[1].value
end

local function read_qword(addr)
	return qword_from_gg(gg_read(addr, gg.TYPE_QWORD))
end

local function read_dword(addr)
	local v = gg_read(addr, gg.TYPE_DWORD)
	return v and tonumber(v) or 0
end

local function read_byte(addr)
	local v = gg_read(addr, gg.TYPE_BYTE)
	return v and tonumber(v) or 0
end

local function gg_read_batch(specs)
	local batch = {}
	local ids = {}
	for _, spec in ipairs(specs) do
		local addr = spec.addr
		if is_valid_gg_address(addr) then
			batch[#batch + 1] = {
				address = ptr_from_hi_lo(ptr_hi32(addr), ptr_lo32(addr)),
				flags = spec.flags,
			}
			ids[#batch] = spec.id
		end
	end
	if #batch == 0 then
		return {}
	end
	local ok, results = pcall(function()
		return gg.getValues(batch)
	end)
	if not ok or not results then
		return {}
	end
	local out = {}
	for i, row in ipairs(results) do
		out[ids[i]] = row.value
	end
	return out
end

local function signed_i64(raw)
	raw = qword_from_gg(raw)
	if raw >= 0x8000000000000000 then
		raw = raw - 0x10000000000000000
	end
	return raw
end

local function int128_to_signed(lo, hi)
	lo = normalize_u64(lo)
	hi = normalize_u64(hi)
	if hi >= 0x8000000000000000 then
		hi = hi - 0x10000000000000000
	end
	if hi == 0 or hi == -1 then
		local s = lo
		if s >= 0x8000000000000000 then
			s = s - 0x10000000000000000
		end
		return s
	end
	return hi * 0x10000000000000000 + lo
end

local FD6_DIV = 1000000

local function fd6_abs_parts(lo, hi)
	lo = normalize_u64(lo)
	hi = normalize_u64(hi)
	local neg = false
	local abs = lo
	if hi == 0 or hi == 0xFFFFFFFFFFFFFFFF then
		if lo >= 0x8000000000000000 then
			local s = lo - 0x10000000000000000
			if s < 0 then
				neg = true
				abs = -s
			else
				abs = s
			end
		end
	else
		local raw = int128_to_signed(lo, hi)
		if raw < 0 then
			neg = true
			raw = -raw
		end
		abs = raw
	end
	local whole = math.floor(abs / FD6_DIV)
	local frac = abs - whole * FD6_DIV
	return neg, whole, frac
end

local function format_fd6_sec(lo, hi)
	local neg, whole, frac = fd6_abs_parts(lo, hi)
	local prefix = neg and "-" or ""
	if frac == 0 then
		return string.format("%s%d.0", prefix, whole)
	end
	local frac_s = string.format("%06d", frac):gsub("0+$", "")
	return string.format("%s%d.%s", prefix, whole, frac_s)
end

local function fd6_from_lo_hi(lo, hi)
	lo = qword_from_gg(lo)
	hi = qword_from_gg(hi)
	return {
		lo = lo,
		hi = hi,
		lo_hex = string.format("%016X", lo),
		hi_hex = string.format("%016X", hi),
		raw = int128_to_signed(lo, hi),
		sec_str = format_fd6_sec(lo, hi),
	}
end

local function read_fd6_field(addr)
	return fd6_from_lo_hi(read_qword(addr), read_qword(ptr_add(addr, 8)))
end

local function read_f64(addr)
	if addr == 0 then
		return 0.0
	end
	return signed_i64(read_qword(addr)) / F64_SCALE
end

local function heap_read_regions()
	local flags = gg.REGION_ANONYMOUS
		| gg.REGION_C_ALLOC
		| gg.REGION_C_HEAP
		| gg.REGION_C_DATA
		| gg.REGION_OTHER
	if gg.REGION_JAVA_HEAP then
		flags = flags | gg.REGION_JAVA_HEAP
	end
	if gg.REGION_JAVA then
		flags = flags | gg.REGION_JAVA
	end
	if gg.REGION_ASHMEM then
		flags = flags | gg.REGION_ASHMEM
	end
	return flags
end

local function meta_dict_get_value(dict_ptr, key)
	if dict_ptr == 0 then
		return 0
	end
	local count = read_dword(ptr_add(dict_ptr, 0x20))
	local entries = read_qword(ptr_add(dict_ptr, 0x18))
	if entries == 0 or count <= 0 then
		return 0
	end
	for i = 0, count - 1 do
		local slot = ptr_add(entries, 0x30 + (i * 0x28))
		if read_dword(slot) == key then
			return read_qword(ptr_add(slot, 0x10))
		end
	end
	return 0
end

local function validate_player_unit(unit, entity_id)
	if unit == 0 then
		return false
	end
	local probe = gg_read_batch({
		{ id = "is_player", addr = ptr_add(unit, OFF.UNIT_IS_PLAYER), flags = gg.TYPE_BYTE },
		{ id = "unit_id", addr = ptr_add(unit, OFF.UNIT_ID), flags = gg.TYPE_DWORD },
	})
	if (tonumber(probe.is_player) or 0) == 0 then
		return false
	end
	if entity_id >= 0 and (tonumber(probe.unit_id) or 0) ~= entity_id then
		return false
	end
	return true
end

local function find_player_unit(entities_ptr)
	if entities_ptr == 0 then
		return 0, 0
	end
	local head = gg_read_batch({
		{ id = "player_id", addr = ptr_add(entities_ptr, OFF.ENT_PLAYER_ID), flags = gg.TYPE_DWORD },
		{ id = "units_dict", addr = ptr_add(entities_ptr, OFF.ENT_UNITS_DICT), flags = gg.TYPE_QWORD },
	})
	local player_id = tonumber(head.player_id) or 0
	local units_dict = qword_from_gg(head.units_dict)
	if units_dict == 0 then
		return 0, player_id
	end

	local dict_head = gg_read_batch({
		{ id = "count", addr = ptr_add(units_dict, 0x20), flags = gg.TYPE_DWORD },
		{ id = "entries", addr = ptr_add(units_dict, 0x18), flags = gg.TYPE_QWORD },
	})
	local count = tonumber(dict_head.count) or 0
	local entries = qword_from_gg(dict_head.entries)
	if entries == 0 or count <= 0 then
		return 0, player_id
	end

	local limit = math.min(count, MAX_DICT_SCAN)
	local slot_specs = {}
	for i = 0, limit - 1 do
		local slot = ptr_add(entries, 0x30 + (i * 0x28))
		slot_specs[#slot_specs + 1] = { id = "k" .. i, addr = slot, flags = gg.TYPE_DWORD }
		slot_specs[#slot_specs + 1] = {
			id = "v" .. i,
			addr = ptr_add(slot, 0x10),
			flags = gg.TYPE_QWORD,
		}
	end
	local slots = gg_read_batch(slot_specs)

	local direct_unit = 0
	for i = 0, limit - 1 do
		local key = tonumber(slots["k" .. i]) or -1
		local value = qword_from_gg(slots["v" .. i])
		if key == player_id and value ~= 0 then
			direct_unit = value
			break
		end
	end
	if direct_unit ~= 0 and validate_player_unit(direct_unit, player_id) then
		return direct_unit, player_id
	end

	for i = 0, limit - 1 do
		local key = tonumber(slots["k" .. i]) or -1
		local value = qword_from_gg(slots["v" .. i])
		if value ~= 0 and validate_player_unit(value, key) then
			return value, key
		end
	end
	return 0, player_id
end

local function fmt_ptr(v)
	if v == nil or v == 0 then
		return "NULL"
	end
	return string.format("0x%X%08X", ptr_hi32(v), ptr_lo32(v))
end

local function get_pointers(t_addr)
	gg.clearResults()
	gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
	local r = gg.getResults(200)
	local p = {}
	for _, v in ipairs(r) do
		if read_qword(v.address - 0x8) == 0 or read_qword(v.address + 0x8) == 0 then
			p[#p + 1] = v.address
		end
	end
	return p
end

local function get_dict_pointers(t_addr)
	gg.clearResults()
	gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
	local r = gg.getResults(200)
	local p = {}
	for _, v in ipairs(r) do
		if read_qword(v.address - 0x8) == 0 then
			p[#p + 1] = v.address
		end
	end
	return p
end

local function get_entries_pointers(t_addr)
	gg.clearResults()
	gg.searchNumber(string.format("%X", t_addr) .. "h", gg.TYPE_QWORD)
	local r = gg.getResults(200)
	local p = {}
	for _, v in ipairs(r) do
		if read_qword(v.address - 0x10) == 0 then
			p[#p + 1] = v.address
		end
	end
	return p
end

local function trace_player_model(entries_base)
	local entries_ptrs = get_entries_pointers(entries_base)
	for _, e_ptr in ipairs(entries_ptrs) do
		for _, d_ptr in ipairs(get_dict_pointers(e_ptr - 0x18)) do
			for _, c_ptr in ipairs(get_pointers(d_ptr - 0x10)) do
				local player_base = c_ptr - 0x210
				local paused = read_dword(ptr_add(player_base, OFF.PLAYER_GAME_PAUSED))
				if paused == 0 or paused == 1 then
					local skill_col = read_qword(ptr_add(player_base, OFF.PLAYER_SKILL_COL))
					if skill_col > 0x10000000 then
						return player_base
					end
				end
			end
		end
	end
	return nil
end

local function shared_paths(file_name)
	return {
		"/sdcard/Pictures/" .. file_name,
		"/mnt/shared/Pictures/" .. file_name,
		"/storage/emulated/0/Pictures/" .. file_name,
		"/sdcard/Download/" .. file_name,
		"/storage/emulated/0/Download/" .. file_name,
	}
end

local function save_text(file_name, text)
	for _, path in ipairs(shared_paths(file_name)) do
		local file = io.open(path, "w")
		if file then
			file:write(text)
			file:close()
			return true, path
		end
	end
	return false, nil
end

local function load_session()
	for _, path in ipairs(shared_paths(SESSION_FILE)) do
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

local function save_session(hammer_addr, player_addr, forge_count)
	local text = string.format(
		"hammer=%X\nplayer=%X\nforge=%d\n",
		hammer_addr or 0,
		player_addr or 0,
		forge_count or 0
	)
	return save_text(SESSION_FILE, text)
end

local function read_forge_count(player_addr)
	local forge_ptr = read_qword(ptr_add(player_addr, OFF.PLAYER_FORGE))
	if forge_ptr == 0 then
		return 0
	end
	return read_dword(ptr_add(forge_ptr, OFF.FORGE_FORGE_COUNT))
end

local function validate_player_addr(player_addr)
	if player_addr == nil or player_addr == 0 then
		return nil
	end
	local paused = read_dword(ptr_add(player_addr, OFF.PLAYER_GAME_PAUSED))
	if paused ~= 0 and paused ~= 1 then
		return nil
	end
	local skill_col = read_qword(ptr_add(player_addr, OFF.PLAYER_SKILL_COL))
	if skill_col <= 0x10000000 then
		return nil
	end
	local forge_count = read_forge_count(player_addr)
	if forge_count <= 0 then
		return nil
	end
	return player_addr
end

local function try_session_player()
	local session = load_session()
	if not session then
		return nil, "session_missing"
	end
	local player_addr = validate_player_addr(session.player)
	if not player_addr then
		return nil, "session_stale"
	end
	return player_addr, "session"
end

local function hammer_search_with_refine()
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

local function resolve_player_via_hammer()
	gg.toast("망치 search...")
	local hammer_addr, status = hammer_search_with_refine()
	if not hammer_addr then
		return nil, status
	end

	gg.toast("PlayerModel trace...")
	local player_addr = trace_player_model(hammer_addr - HAMMER_TO_ENTRIES)
	if not player_addr then
		return nil, "trace_failed"
	end

	local forge_count = read_forge_count(player_addr)
	if forge_count <= 0 then
		return nil, "forge_count_zero"
	end

	save_session(hammer_addr, player_addr, forge_count)
	return player_addr, "hammer"
end

local function resolve_player()
	gg.toast("Session...")
	local player_addr, status = try_session_player()
	if player_addr then
		return player_addr, status
	end
	return resolve_player_via_hammer()
end

local function read_current_tick(player_ptr)
	if player_ptr == 0 then
		return 0
	end
	return tonumber(signed_i64(read_qword(ptr_add(player_ptr, OFF.PLAYER_CURRENT_TICK)))) or 0
end

local function snap_signature(snap)
	if not snap.ok then
		return "fail:" .. tostring(snap.game_tick or 0)
	end
	if snap.combat_state < 0 then
		return string.format(
			"t:%d:m:%d:bs:%d:w:%d",
			tonumber(snap.game_tick) or 0,
			snap.mode,
			snap.battle_state,
			snap.wave
		)
	end
	local at_lo = snap.at_fd6 and snap.at_fd6.lo or 0
	return string.format(
		"t:%d:cs:%d:at:%X:rng:%d:dbl:%d",
		tonumber(snap.game_tick) or 0,
		snap.combat_state,
		at_lo,
		snap.in_range and 1 or 0,
		snap.double_attack and 1 or 0
	)
end

local function fd6_sec_str(field)
	if field == nil then
		return "?"
	end
	return field.sec_str or "?"
end

local function combat_state_ko(snap)
	if snap.combat_state < 0 then
		return "(유닛 없음)"
	end
	return COMBAT_STATE_KO[snap.combat_state]
		or ("?" .. tostring(snap.combat_state))
end

local function format_status_block(snap)
	local lines = {
		string.format("게임 틱: %d", snap.game_tick or 0),
		string.format("전투 상태: %s", combat_state_ko(snap)),
	}
	if snap.combat_state < 0 then
		return table.concat(lines, "\n")
	end
	lines[#lines + 1] = string.format(
		"공격 게이지(AttackTimer): %s",
		fd6_sec_str(snap.at_fd6)
	)
	lines[#lines + 1] = string.format("체력: %s", fd6_sec_str(snap.hp_fd6))
	lines[#lines + 1] = ""
	lines[#lines + 1] = string.format("와인드업: %s", fd6_sec_str(snap.windup_fd6))
	lines[#lines + 1] = string.format(
		"공격 지속시간: %s",
		fd6_sec_str(snap.attack_duration_fd6)
	)
	return table.concat(lines, "\n")
end

local function snapshot(player_ptr)
	local out = {
		ok = false,
		paused = false,
		mode = -1,
		battle_state = -1,
		wave = -1,
		wave_timer = 0.0,
		entity_id = -1,
		combat_state = -1,
		in_range = false,
		double_attack = false,
		unit = 0,
		at_fd6 = nil,
		windup_fd6 = nil,
		attack_duration_fd6 = nil,
		hp_fd6 = nil,
		game_tick = 0,
	}
	if player_ptr == 0 then
		return out
	end

	local player_row = gg_read_batch({
		{ id = "tick", addr = ptr_add(player_ptr, OFF.PLAYER_CURRENT_TICK), flags = gg.TYPE_QWORD },
		{ id = "paused", addr = ptr_add(player_ptr, OFF.PLAYER_GAME_PAUSED), flags = gg.TYPE_BYTE },
		{ id = "mode", addr = ptr_add(player_ptr, OFF.PLAYER_BATTLE_MODE), flags = gg.TYPE_DWORD },
		{ id = "mb", addr = ptr_add(player_ptr, OFF.PLAYER_MAIN_BATTLE), flags = gg.TYPE_QWORD },
	})
	out.game_tick = tonumber(signed_i64(player_row.tick)) or 0
	out.paused = (tonumber(player_row.paused) or 0) ~= 0
	out.mode = tonumber(player_row.mode) or -1

	local mb = qword_from_gg(player_row.mb)
	if mb == 0 then
		return out
	end

	local mb_row = gg_read_batch({
		{ id = "battle_state", addr = ptr_add(mb, OFF.MB_BATTLE_STATE), flags = gg.TYPE_BYTE },
		{ id = "wave", addr = ptr_add(mb, OFF.MB_CURRENT_WAVE), flags = gg.TYPE_DWORD },
		{ id = "wave_timer", addr = ptr_add(mb, OFF.MB_WAVE_TIMER), flags = gg.TYPE_QWORD },
		{ id = "scene", addr = ptr_add(mb, OFF.MB_COMBAT_SCENE), flags = gg.TYPE_QWORD },
	})
	out.battle_state = tonumber(mb_row.battle_state) or -1
	out.wave = tonumber(mb_row.wave) or -1
	out.wave_timer = signed_i64(mb_row.wave_timer) / F64_SCALE

	local scene = qword_from_gg(mb_row.scene)
	if scene == 0 then
		out.ok = true
		return out
	end

	local entities = read_qword(ptr_add(scene, OFF.CS_ENTITIES))
	local unit, entity_id = find_player_unit(entities)
	out.entity_id = entity_id
	if unit == 0 then
		out.ok = true
		return out
	end

	out.unit = unit
	local unit_row = gg_read_batch({
		{ id = "combat_state", addr = ptr_add(unit, OFF.UNIT_COMBAT_STATE), flags = gg.TYPE_BYTE },
		{ id = "in_range", addr = ptr_add(unit, OFF.UNIT_TARGET_IN_RANGE), flags = gg.TYPE_BYTE },
		{ id = "double_attack", addr = ptr_add(unit, OFF.UNIT_DOUBLE_ATTACK), flags = gg.TYPE_BYTE },
		{ id = "at_lo", addr = ptr_add(unit, OFF.UNIT_ATTACK_TIMER), flags = gg.TYPE_QWORD },
		{ id = "at_hi", addr = ptr_add(unit, OFF.UNIT_ATTACK_TIMER + 8), flags = gg.TYPE_QWORD },
		{ id = "wu_lo", addr = ptr_add(unit, OFF.UNIT_WINDUP), flags = gg.TYPE_QWORD },
		{ id = "wu_hi", addr = ptr_add(unit, OFF.UNIT_WINDUP + 8), flags = gg.TYPE_QWORD },
		{ id = "ad_lo", addr = ptr_add(unit, OFF.UNIT_ATTACK_DURATION), flags = gg.TYPE_QWORD },
		{ id = "ad_hi", addr = ptr_add(unit, OFF.UNIT_ATTACK_DURATION + 8), flags = gg.TYPE_QWORD },
		{ id = "hp_lo", addr = ptr_add(unit, OFF.UNIT_HP), flags = gg.TYPE_QWORD },
		{ id = "hp_hi", addr = ptr_add(unit, OFF.UNIT_HP + 8), flags = gg.TYPE_QWORD },
	})
	out.combat_state = tonumber(unit_row.combat_state) or -1
	out.in_range = (tonumber(unit_row.in_range) or 0) ~= 0
	out.double_attack = (tonumber(unit_row.double_attack) or 0) ~= 0
	out.at_fd6 = fd6_from_lo_hi(unit_row.at_lo, unit_row.at_hi)
	out.windup_fd6 = fd6_from_lo_hi(unit_row.wu_lo, unit_row.wu_hi)
	out.attack_duration_fd6 = fd6_from_lo_hi(unit_row.ad_lo, unit_row.ad_hi)
	out.hp_fd6 = fd6_from_lo_hi(unit_row.hp_lo, unit_row.hp_hi)
	out.ok = true
	return out
end

local function snapshot_from_unit(player_ptr, game_tick, unit, entity_id)
	local out = {
		ok = false,
		paused = false,
		mode = -1,
		battle_state = -1,
		wave = -1,
		wave_timer = 0.0,
		entity_id = entity_id,
		combat_state = -1,
		in_range = false,
		double_attack = false,
		unit = unit,
		at_fd6 = nil,
		windup_fd6 = nil,
		attack_duration_fd6 = nil,
		hp_fd6 = nil,
		game_tick = game_tick,
	}
	if player_ptr == 0 or unit == 0 then
		return out
	end

	local player_row = gg_read_batch({
		{ id = "paused", addr = ptr_add(player_ptr, OFF.PLAYER_GAME_PAUSED), flags = gg.TYPE_BYTE },
		{ id = "mode", addr = ptr_add(player_ptr, OFF.PLAYER_BATTLE_MODE), flags = gg.TYPE_DWORD },
		{ id = "mb", addr = ptr_add(player_ptr, OFF.PLAYER_MAIN_BATTLE), flags = gg.TYPE_QWORD },
	})
	out.paused = (tonumber(player_row.paused) or 0) ~= 0
	out.mode = tonumber(player_row.mode) or -1

	local mb = qword_from_gg(player_row.mb)
	if mb == 0 then
		return out
	end

	local mb_row = gg_read_batch({
		{ id = "battle_state", addr = ptr_add(mb, OFF.MB_BATTLE_STATE), flags = gg.TYPE_BYTE },
		{ id = "wave", addr = ptr_add(mb, OFF.MB_CURRENT_WAVE), flags = gg.TYPE_DWORD },
		{ id = "wave_timer", addr = ptr_add(mb, OFF.MB_WAVE_TIMER), flags = gg.TYPE_QWORD },
	})
	out.battle_state = tonumber(mb_row.battle_state) or -1
	out.wave = tonumber(mb_row.wave) or -1
	out.wave_timer = signed_i64(mb_row.wave_timer) / F64_SCALE

	if not validate_player_unit(unit, entity_id) then
		return out
	end

	local unit_row = gg_read_batch({
		{ id = "combat_state", addr = ptr_add(unit, OFF.UNIT_COMBAT_STATE), flags = gg.TYPE_BYTE },
		{ id = "in_range", addr = ptr_add(unit, OFF.UNIT_TARGET_IN_RANGE), flags = gg.TYPE_BYTE },
		{ id = "double_attack", addr = ptr_add(unit, OFF.UNIT_DOUBLE_ATTACK), flags = gg.TYPE_BYTE },
		{ id = "at_lo", addr = ptr_add(unit, OFF.UNIT_ATTACK_TIMER), flags = gg.TYPE_QWORD },
		{ id = "at_hi", addr = ptr_add(unit, OFF.UNIT_ATTACK_TIMER + 8), flags = gg.TYPE_QWORD },
		{ id = "wu_lo", addr = ptr_add(unit, OFF.UNIT_WINDUP), flags = gg.TYPE_QWORD },
		{ id = "wu_hi", addr = ptr_add(unit, OFF.UNIT_WINDUP + 8), flags = gg.TYPE_QWORD },
		{ id = "ad_lo", addr = ptr_add(unit, OFF.UNIT_ATTACK_DURATION), flags = gg.TYPE_QWORD },
		{ id = "ad_hi", addr = ptr_add(unit, OFF.UNIT_ATTACK_DURATION + 8), flags = gg.TYPE_QWORD },
		{ id = "hp_lo", addr = ptr_add(unit, OFF.UNIT_HP), flags = gg.TYPE_QWORD },
		{ id = "hp_hi", addr = ptr_add(unit, OFF.UNIT_HP + 8), flags = gg.TYPE_QWORD },
	})
	out.combat_state = tonumber(unit_row.combat_state) or -1
	out.in_range = (tonumber(unit_row.in_range) or 0) ~= 0
	out.double_attack = (tonumber(unit_row.double_attack) or 0) ~= 0
	out.at_fd6 = fd6_from_lo_hi(unit_row.at_lo, unit_row.at_hi)
	out.windup_fd6 = fd6_from_lo_hi(unit_row.wu_lo, unit_row.wu_hi)
	out.attack_duration_fd6 = fd6_from_lo_hi(unit_row.ad_lo, unit_row.ad_hi)
	out.hp_fd6 = fd6_from_lo_hi(unit_row.hp_lo, unit_row.hp_hi)
	out.ok = true
	return out
end

local function snapshot_with_cache(player_ptr, game_tick, force_full, cache)
	if not force_full and cache.unit ~= 0 then
		local fast = snapshot_from_unit(player_ptr, game_tick, cache.unit, cache.entity_id)
		if fast.ok then
			return fast
		end
	end

	local snap = snapshot(player_ptr)
	snap.game_tick = game_tick
	if snap.unit ~= 0 then
		cache.unit = snap.unit
		cache.entity_id = snap.entity_id
	else
		cache.unit = 0
		cache.entity_id = -1
	end
	return snap
end

local function combat_state_label(snap)
	if snap.combat_state < 0 then
		return "no-unit"
	end
	return COMBAT_STATE[snap.combat_state] or ("?" .. tostring(snap.combat_state))
end

local function format_log_line(snap)
	local mode = BATTLE_MODE[snap.mode] or ("M" .. tostring(snap.mode))
	local bs = BATTLE_STATE[snap.battle_state] or ("B" .. tostring(snap.battle_state))
	local cs = combat_state_label(snap)
	local flags = {}
	if snap.paused then
		flags[#flags + 1] = "PAUSED"
	end
	if snap.battle_state ~= 3 then
		flags[#flags + 1] = "idle-battle"
	end
	if snap.in_range then
		flags[#flags + 1] = "rng"
	end
	if snap.double_attack then
		flags[#flags + 1] = "dbl"
	end
	local flag_text = #flags > 0 and (" " .. table.concat(flags, ",")) or ""
	if snap.combat_state < 0 then
		return string.format(
			"GT=%d %s|%s W%d %s%s",
			snap.game_tick or 0,
			mode,
			bs,
			snap.wave >= 0 and snap.wave or 0,
			cs,
			flag_text
		)
	end
	return string.format(
		"GT=%d %s|%s W%d CS=%s AT=%s WU=%s AD=%s HP=%s%s",
		snap.game_tick or 0,
		mode,
		bs,
		snap.wave >= 0 and snap.wave or 0,
		cs,
		snap.at_fd6 and snap.at_fd6.sec_str or "?",
		snap.windup_fd6 and snap.windup_fd6.sec_str or "?",
		snap.attack_duration_fd6 and snap.attack_duration_fd6.sec_str or "?",
		snap.hp_fd6 and snap.hp_fd6.sec_str or "?",
		flag_text
	)
end

local function show_monitor_toast(text)
	text = text:gsub("[\r\n]+$", "")
	local top_pad = string.rep("\n", TOAST_TOP_PAD_LINES)
	gg.toast(top_pad .. text)
end

local function main()
	gg.setVisible(false)
	pcall(function()
		gg.setRanges(heap_read_regions())
	end)

	local player_ptr, status = resolve_player()
	player_ptr = normalize_u64(player_ptr)
	gg.clearResults()
	if not player_ptr then
		gg.setVisible(true)
		gg.alert("PlayerModel 찾기 실패.\n" .. tostring(status))
		return
	end

	gg.setVisible(true)
	gg.alert(
		"전투 FSM 모니터\n\n"
			.. "PlayerModel: " .. fmt_ptr(player_ptr) .. "\n"
			.. "ForgeCount: " .. tostring(read_forge_count(player_ptr)) .. "\n"
			.. "CurrentTick+0x58: " .. tostring(read_current_tick(player_ptr)) .. "\n\n"
			.. "GameTick / CombatState / AttackTimer 변화 시 갱신.\n"
			.. "toast 앞쪽 개행 " .. tostring(TOAST_TOP_PAD_LINES) .. "줄.\n\n"
			.. "UnitEntity AttackTimer / WindUp / AttackDuration (FD6 sec).\n\n"
			.. "종료: GameGuardian 플로팅 아이콘 탭 → 스크립트 중지"
	)

	gg.setVisible(false)
	print("[MIRAESEE COMBAT WATCH] start " .. VERSION_TAG)
	print("poll_ms=" .. tostring(GAME_TICK_POLL_MS))
	print("toast_latest=" .. tostring(MONITOR_TOAST_LATEST))
	print("print_every_change=" .. tostring(MONITOR_PRINT_EVERY_CHANGE))
	print("toast_top_pad_lines=" .. tostring(TOAST_TOP_PAD_LINES))
	print("catchup_max_burst=" .. tostring(CATCHUP_MAX_BURST))
	local prev_game_tick = nil
	local prev_signature = nil
	local watch_reads = 0
	local catchup_total = 0
	local unit_cache = { unit = 0, entity_id = -1 }
	while true do
		if gg.isVisible() then
			break
		end

		local latest_snap = nil
		local burst = 0
		repeat
			burst = burst + 1
			local game_tick = read_current_tick(player_ptr)
			local tick_changed = prev_game_tick == nil or game_tick ~= prev_game_tick
			local snap = snapshot_with_cache(player_ptr, game_tick, tick_changed, unit_cache)
			snap.game_tick = game_tick

			local signature = snap_signature(snap)
			local sig_changed = prev_signature == nil or signature ~= prev_signature
			if tick_changed or sig_changed then
				prev_game_tick = game_tick
				prev_signature = signature
				watch_reads = watch_reads + 1
				latest_snap = snap
				if MONITOR_PRINT_EVERY_CHANGE then
					if snap.ok then
						print(format_log_line(snap))
					else
						print(string.format("GT=%d read-fail", game_tick))
					end
				end
			end

			local after_tick = read_current_tick(player_ptr)
		until after_tick == game_tick or burst >= CATCHUP_MAX_BURST

		if burst > 1 then
			catchup_total = catchup_total + (burst - 1)
		end

		if latest_snap and MONITOR_TOAST_LATEST then
			if latest_snap.ok then
				show_monitor_toast(format_status_block(latest_snap))
			else
				show_monitor_toast(
					string.format("게임 틱: %d\n읽기 실패", latest_snap.game_tick or 0)
				)
			end
		end

		gg.sleep(GAME_TICK_POLL_MS)
	end

	print(string.format(
		"[MIRAESEE COMBAT WATCH] stop updates=%d catchup_extra=%d",
		watch_reads,
		catchup_total
	))

	gg.setVisible(true)
	gg.alert(string.format("중지 (updates=%d, catchup=%d)", watch_reads, catchup_total))
end

main()
