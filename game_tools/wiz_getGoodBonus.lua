-- Author: Ragu
-- Game: Wizardry I-II-III - Story of Llylgamyn (Japan) (En,Ja) (NP)
-- Emulator: Bizhawk
-- Core Used: BSNESv115+
-- System: Super Famicom/Super NES
-- Description: Retry rolls until you get a good bonus during character
-- creation. 
-- I wrote this for the original japanese version but i doubt the addresses 
-- have changed too much in the fan-translated version so it should work?
-- Usage: Load ROM in Bizhawk, go to Tools > Lua Console, then Script > Open 
-- Script, select the script.

-- change the target_points variable to the minimum you'd like. i'm not totally
-- sure what the maximum is, but 29 is as high as i've gotten and you'll be
-- doing a LOT of rerolls for that
local target_points = 20
local print_debug = false

function debug_text()
	if print_debug == true then
		local vpos = 50
		gui.text(50,vpos,"Create Menu Status: " .. tostring(getMenuStatus()))
		vpos = vpos + 20
		gui.text(50,vpos,"Town Status: " .. tostring(getTownStatus()))
		vpos = vpos + 20
		gui.text(50,vpos,'Bonus Points: ' .. tostring(getBonusPoints()))
		vpos = vpos + 20
		gui.text(50,vpos,"Hit target values: " .. tostring(hit_target))
	end
end

-- return current number of bonus points
function getBonusPoints()
	return(memory.read_u8(0x7E101C))
end

-- return location value
function getTownStatus()
	local town_status = memory.read_u8(0x0001FF)
	if town_status == 1 then
		return("Out of Town")
	elseif town_status == 2 then
		return("In Town")
	else
		return(tostring(town_status))
	end
end

-- return whether you're in character creation menu
function getMenuStatus()
	local menu_status = memory.read_u8(0x000246)
	if menu_status == 13 then
		return(true)
	else
		return(false)
	end
end


while true do
	hit_target = false	
	debug_text()
	
	-- if you're in the bonus point allocation menu and outside of town, run
	-- the logic. this should be enough to keep it from running elsewhere?
	while getMenuStatus() and getTownStatus() == "Out of Town" do
		debug_text()

		-- if bonus points are less than the target points and you haven't hit
		-- the target value yet, keep rerolling until you hit it
		while getBonusPoints() < target_points and hit_target == false do
			input = {}
			input.Y=true
			-- hold the y button for 6 frames (reroll)
			for i=1, 6, 1 do
				debug_text()
				joypad.set(input,1)
				emu.frameadvance()
			end
			debug_text()
			-- release y button
			input.Y=false
			joypad.set(input,1)
			emu.frameadvance()
		end
		-- once you've broken out of the reroll loop (because you've hit a
		-- threshold value, set hit_target to true
		hit_target = true
		emu.frameadvance()
	end
	emu.frameadvance()
end
