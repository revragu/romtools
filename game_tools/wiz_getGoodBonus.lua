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

function debug_text(menu_status,town_status,bonus_points)
	if print_debug == true then
		local vpos = 50
		if menu_status == 13 then
			gui.text(50,vpos,"Create Menu Status: In Menu")
		else
			gui.text(50,vpos,"Create Menu Status: " .. tostring(menu_status))
		end
		vpos = vpos + 20
		if town_status == 1 then
			gui.text(50,vpos,"Town Status: Out of Town")
		elseif town_status == 2 then
			gui.text(50,vpos,"Town Status: In Town")
		else
			gui.text(50,vpos,"Town Status:" .. tostring(town_status))
		end
		vpos = vpos + 20
		gui.text(50,vpos,'bonus points: ' .. tostring(bonus_points))
	end
end

while true do
	-- read whether you're in town, in the right menu, and how many bonus
	-- points you have. i think that should be enough to make sure that this 
	-- isn't running anywhere else?
	local town_status = memory.read_u8(0x0001FF)
	local menu_status = memory.read_u8(0x000246)
	local bonus_points = memory.read_u8(0x7E101C)
	
	debug_text(menu_status,town_status,bonus_points)
	
	-- if you're in the bonus point allocation menu and outside of town, run
	-- the logic
	if menu_status == 13 and town_status == 1 then
		debug_text(menu_status,town_status,bonus_points)

		-- if bonus points are less than the target points
		while bonus_points < target_points do
			input = {}
			input.Y=true

			-- read current bonus points
			bonus_points = memory.read_u8(0x7E101C)
			
			-- hold the y button for 6 frames (reroll)
			for i=1, 6, 1 do
				debug_text(menu_status,bonus_points)
				joypad.set(input,1)
				emu.frameadvance()
			end
			debug_text(menu_status,bonus_points)
			-- release y button
			input.Y=false
			joypad.set(input,1)
			emu.frameadvance()
		end
	end
	emu.frameadvance()
end
