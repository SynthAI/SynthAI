/* *****************************************************************************
 * Satari
 *
 * Copyright 2014 Google Inc.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version 2
 * as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 * *****************************************************************************
 * A.L.E (Arcade Learning Environment)
 * Copyright (c) 2009-2013 by Yavar Naddaf, Joel Veness, Marc G. Bellemare and 
 *   the Reinforcement Learning and Artificial Intelligence Laboratory
 * Released under the GNU General Public License; see License.txt for details. 
 *
 * Based on: Stella  --  "An Atari 2600 VCS Emulator"
 * Copyright (c) 1995-2007 by Bradford W. Mott and the Stella team
 *
 * *****************************************************************************
 */
#include "AirRaid.hpp"

#include "../RomUtils.hpp"

using namespace ale;

AirRaidSettings::AirRaidSettings() {

    reset();
}


/* create a new instance of the rom */
RomSettings* AirRaidSettings::clone() const { 
    
    RomSettings* rval = new AirRaidSettings();
    *rval = *this;
    return rval;
}


/* process the latest information from ALE */
void AirRaidSettings::step(const System& system) {

    // update the reward
    reward_t score = getDecimalScore(0xAA, 0xA9, 0xA8, &system);
    m_reward = score - m_score;
    m_score = score;

    // update terminal status
    int lives = readRam(&system, 0xA7);
    m_terminal = lives == 0xFF;
}


/* is end of game */
bool AirRaidSettings::isTerminal() const {

    return m_terminal;
};


/* get the most recently observed reward */
reward_t AirRaidSettings::getReward() const { 

    return m_reward; 
}


/* is an action part of the minimal set? */
bool AirRaidSettings::isMinimal(const Action &a) const {

    switch (a) {
        case PLAYER_A_NOOP:
        case PLAYER_A_FIRE:
        case PLAYER_A_RIGHT:
        case PLAYER_A_LEFT:
        case PLAYER_A_RIGHTFIRE:
        case PLAYER_A_LEFTFIRE:
            return true;
        default:
            return false;
    }   
}


/* reset the state of the game */
void AirRaidSettings::reset() {
    
    m_reward   = 0;
    m_score    = 0;
    m_terminal = false;
}
        
/* saves the state of the rom settings */
void AirRaidSettings::saveState(Serializer & ser) {
  ser.putInt(m_reward);
  ser.putInt(m_score);
  ser.putBool(m_terminal);
}

// loads the state of the rom settings
void AirRaidSettings::loadState(Deserializer & ser) {
  m_reward = ser.getInt();
  m_score = ser.getInt();
  m_terminal = ser.getBool();
}

ActionVect AirRaidSettings::getStartingActions() {
    ActionVect startingActions;
    startingActions.push_back(PLAYER_A_FIRE);
    return startingActions;
}
