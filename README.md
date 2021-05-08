# BotTelegramMCPS
Telegram bot for the MCPS project, https://t.me/MCPSbot.
## List of commands:
### Utils:
- **/help** - Shows a list of all possible commands
- **/user** - Shows informations about you
- **/topics topic** - Shows every topic you're subscribed to (if no argument is passed)

### Modify Parameters
- **/changeoffset topic offset** - Changes the sampling interval of the desired topic (you're subscribed to)
- **/changetrigger topic trigger** - Changes the trigger condition of the desired topic (you're subscribed to)
- **/setalert topic offset** - Changes the alert offset of the desired topic (you're subscribed to)

### Return Records
- **/avgtemp topic year-month-day** - Gives the average temperature of the current day if no argument is passed
- **/avghum topic year-month-day** - Gives the average humidity of the current day if no argument is passed
- **/lasttemp topic year-month-day** - Returns the last recorded temperature of the current day if no argument is passed
- **/lasthum topic year-month-day** - Returns the last recorded humidity of the current day if no argument is passed
