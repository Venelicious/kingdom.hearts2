-- This atlas deliberately does not claim to implement AP combat/form logic.
-- Inspect is used for unknown reachability, avoiding misleading green markers.
ACTIVE_LOCATIONS = nil
function enabled(id)
    return ACTIVE_LOCATIONS == nil or ACTIVE_LOCATIONS[tonumber(id)] == true
end
function access(region)
    local data = REGIONS[tonumber(region)]
    if data and data.name == "Garden Of Assemblage" then
        return AccessibilityLevel.Normal
    end
    return AccessibilityLevel.Inspect
end
