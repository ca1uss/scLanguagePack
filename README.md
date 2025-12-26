
This is a modified fork of a fork of the original [Component Language Pack by ExoAE](https://github.com/ExoAE/ScCompLangPack). 

**All credit for the original language pack goes to [ExoAE](https://github.com/ExoAE).**

## Changes
- Added **average** prices to most commodities
- Replaced some ship names with their well known nicknames eg Ursa Medivac -> Nursa
- Some basic troubleshooting for error codes and clearer UI stuff
- Markers to signify illegal cargo

## Applying to the game
1. Copy the `Localization` folder of the current game version
2. Navigate to `StarCitizen/LIVE/data` and paste `Localization`
3. In `/LIVE`, create a file `user.cfg` and add `g_language = english`, or use the one provided  

## Modifying and creating your own version
- **If you have a non default install path, you will need to update almost all files to acknowledge this**
- Copy any lines from `global.ini` to `target_strings.ini` and modify to your hearts content
- `customStrings.py` will merge your changes to `global.ini` and move it to the game directory 
- `process-new-patch.py` will get all new strings when you install a new patch
- `getPrices.py` will update commodity prices according to UEX data (may take a few days to update after a patch)


## Notes

- This project is not affiliated with Cloud Imperium Games.
- Using language packs is currently intended by Cloud Imperium Games. 
https://robertsspaceindustries.com/spectrum/community/SC/forum/1/thread/star-citizen-community-localization-update

## ☕ Support the Original Creator

If you'd like to support the original creator ExoAE, you can use their Star Citizen referral code when buying the game:

**STAR-4JD7-RZT4**

Thank you to ExoAE for creating the original pack!
