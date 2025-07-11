-- === FINAL FINAL FINAL — MULTI-DOMAIN VISOR (Sector-Safe) ===

-- === Addresses ===
-- System Bus: HUD Energy Digits
local HP_HUNDREDS = 0x030008C5
local HP_TENS     = 0x030008C8
local HP_ONES     = 0x030008C7

-- Combined WRAM: True Energy and Missiles
local TRUE_HP_ADDR = 0x041310  -- << NEW ADDRESS
local MISSILES_ADDRESS = 0x041314

-- System Bus: Boss + Room ID
local BOSS_FLAG = 0x2F00
local ROOM_ID   = 0x035719

local output_path = "ram_snapshot.txt"

local last_hp = -1
local last_true_hp = -1
local last_boss = -1
local last_room = -1
local last_sector = ""

local debounce_frames = 0

-- === Sector Lookup Table ===
local SECTOR_ADDRESSES = {
    [0x00] = "MD",   -- Main Deck
    [0x01] = "SRX",  -- Sector 1
    [0x02] = "TRO",  -- Sector 2
    [0x03] = "PYR",  -- Sector 3
    [0x04] = "AQA",  -- Sector 4
    [0x05] = "ARC",  -- Sector 5
    [0x06] = "NOC"   -- Sector 6
}
local SECTOR_ADDRESS = 0x03000004

print("=== FINAL FINAL FINAL — MULTI-DOMAIN LOCKED — SECTOR SAFE ===")

while true do
    -- === Read HP Digits ===
    memory.usememorydomain("System Bus")
    local hundreds = memory.readbyte(HP_HUNDREDS)
    local tens     = memory.readbyte(HP_TENS)
    local ones     = memory.readbyte(HP_ONES)
    local hp = (hundreds * 100) + (tens * 10) + ones

    -- === Read Boss & Room ===
    local boss = memory.readbyte(BOSS_FLAG)
    local room = memory.readbyte(ROOM_ID)

    -- === Read Sector ===
    local sector_raw = memory.readbyte(SECTOR_ADDRESS)
    local sector = SECTOR_ADDRESSES[sector_raw] or string.format("UNK%02X", sector_raw)

    -- === Read TRUE HP and Missiles (Combined WRAM) ===
    memory.usememorydomain("Combined WRAM")
    local lo = memory.readbyte(TRUE_HP_ADDR)
    local hi = memory.readbyte(TRUE_HP_ADDR + 1)
    local true_hp = lo + (hi * 256)
    local missiles = memory.readbyte(MISSILES_ADDRESS)

    -- Sanity filter: missiles can't be garbage
    if missiles > 200 then
        missiles = 0
    end

    -- === Flicker armor for HP/Boss ===
    local room_valid = (room ~= 0x00 and room ~= 0xFF)
    local alive_or_real_death = (hp > 0 or (hp == 0 and room_valid))

    if last_hp > 0 and math.abs(hp - last_hp) <= 5 then
        hp = last_hp
    end

    if last_boss >= 0 and boss ~= last_boss and room == last_room then
        boss = last_boss
    end

    if debounce_frames > 0 then
        debounce_frames = debounce_frames - 1
    end

    local should_log = false

    -- === Triggers ===
    if (room ~= last_room or sector ~= last_sector) and room_valid then
        should_log = true
        print(string.format("ROOM/SECTOR CHANGE: %s: 0x%02X → 0x%02X (%s)", sector, last_room, room, sector))
    end

    if not should_log and room_valid and alive_or_real_death and debounce_frames == 0 and (
        hp ~= last_hp or true_hp ~= last_true_hp or boss ~= last_boss
    ) then
        should_log = true
        print(string.format(
            "STATE CHANGE: HUD_HP %d→%d | TRUE_HP %d→%d | Boss %d→%d",
            last_hp, hp, last_true_hp, true_hp, last_boss, boss
        ))
    end

    if should_log then
    last_hp = hp
    last_true_hp = true_hp
    last_boss = boss
    last_room = room
    last_sector = sector

    local line = string.format(
        "HP: %d Missiles: %d Boss: %s Room: H%03X_%s\n",
        true_hp, missiles, boss, room, sector
    )

    local f = io.open(output_path, "w")
    f:write(line)
    f:close()

    print("LOGGED:", line)

    debounce_frames = 10
end

    emu.frameadvance()
end
