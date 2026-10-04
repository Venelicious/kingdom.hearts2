-- AP is authoritative for inventory and checked locations. No LocationChecks
-- calls: clicking a marker is local bookkeeping and never changes the seed.
local seen_items = {}
local checked = {}
local function location(id, name)
    local path = LOCATION_IDS[id] or LOCATION_NAMES[name]
    return path and Tracker:FindObjectForCode(path)
end
local function mark(id, name)
    local object = location(id, name)
    if object then object.AvailableChestCount = 0 end
    checked[id] = true
end
Archipelago:AddClearHandler("KH2 reset", function(slot_data)
    Tracker.BulkUpdate = true
    local ok, err = pcall(function()
        seen_items = {}
        checked = {}
        for _, code in pairs(ITEM_IDS) do
            local object = Tracker:FindObjectForCode(code)
            if object then object.AcquiredCount = 0 end
        end
        for _, path in pairs(LOCATION_IDS) do
            local object = Tracker:FindObjectForCode(path)
            if object then object.AvailableChestCount = object.ChestCount end
        end
        -- Missing and checked form the exact randomized seed location set.
        ACTIVE_LOCATIONS = nil
        if Archipelago.MissingLocations ~= nil and Archipelago.CheckedLocations ~= nil then
            ACTIVE_LOCATIONS = {}
            for _, id in pairs(Archipelago.MissingLocations) do ACTIVE_LOCATIONS[id] = true end
            for _, id in pairs(Archipelago.CheckedLocations) do
                ACTIVE_LOCATIONS[id] = true
                mark(id)
            end
        end
        if slot_data then
            print("KH2 atlas connected; fight/form reachability requires manual verification.")
        end
    end)
    Tracker.BulkUpdate = false
    if not ok then print("KH2 reset error: " .. tostring(err)) end
end)
Archipelago:AddItemHandler("KH2 items", function(index, id, name, player)
    if seen_items[index] then return end
    seen_items[index] = true
    local code = ITEM_IDS[id] or ITEM_NAMES[name]
    local object = code and Tracker:FindObjectForCode(code)
    if object then object.AcquiredCount = object.AcquiredCount + 1 end
end)
Archipelago:AddLocationHandler("KH2 locations", function(id, name)
    if not checked[id] then mark(id, name) end
end)
