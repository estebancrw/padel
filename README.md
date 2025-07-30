# 🎾 Padel Bot

A Telegram bot that automatically sends reminders to your padel group about who's responsible for court booking each week.

## 📋 How It Works

Every **Sunday, Monday, and Tuesday at 9:00 AM (Mexico City time)**, the bot sends a message to your Telegram group reminding who's responsible for booking the padel court that week.

### Current Rotation (Starting July 27, 2025)
1. **Esteban** - Week 1
2. **Chema** - Week 2  
3. **Adrian** - Week 3
4. **Chito** - Week 4
5. **Vanish** - Week 5
6. **JC** - Week 6
7. *(Back to Esteban)* - Week 7

## 🔄 How to Update the Rotation (For Non-Developers)

### Scenario 1: Someone is on Vacation

If someone can't book the court for their assigned week:

1. Click on `data/schedule_2025.json` file
2. Click the ✏️ pencil icon to edit
3. Find the week you need to change (e.g., `"2025-W40"`)
4. Change the name to whoever is covering
5. Scroll down and click "Commit changes"

**Example:** If Chito is on vacation during week 40:
```json
"2025-W40": "Adrian",  // Adrian covers for Chito
```

### Scenario 2: Swap Weeks

If two people want to swap their weeks:

1. Edit `data/schedule_2025.json`
2. Find both weeks
3. Swap the names
4. Commit changes

**Example:** Adrian and Chito swap weeks 34 and 36:
```json
"2025-W34": "Adrian",  // Was Chito's week
"2025-W36": "Chito",   // Was Adrian's week
```

### Scenario 3: Add a Special Message

For holidays or special events:

1. Edit `data/schedule_2025.json`
2. Find the `"special_messages"` section
3. Add the week and custom message

**Example:**
```json
"special_messages": {
  "2025-W52": "🎄 Holiday week: {name} is responsible (check holiday hours!)"
}
```

## 📅 Week Numbers Reference

Not sure what week number to use? Here's a quick reference:

- **July 27 - Aug 2**: Week 31 (W31)
- **Aug 3 - Aug 9**: Week 32 (W32)
- **Aug 10 - Aug 16**: Week 33 (W33)
- **Aug 17 - Aug 23**: Week 34 (W34)
- **Aug 24 - Aug 30**: Week 35 (W35)
- **Aug 31 - Sep 6**: Week 36 (W36)

💡 **Tip:** Google "week number 2025" to find any date's week number!

## 🚨 Important Notes

1. **Changes take effect immediately** - Once you commit, the next message will use the updated schedule
2. **Keep the format** - Don't change the structure, just the names
3. **Use exact spelling** - Names must match exactly (including capitals)
4. **Test first** - You can manually trigger the bot to test your changes (see below)

## 🧪 Testing Your Changes

After making changes, you can test the bot:

1. Go to the "Actions" tab in GitHub
2. Click "Send Padel Message" workflow
3. Click "Run workflow" button
4. Click the green "Run workflow" button
5. Check your Telegram group for the test message

## ❓ Need Help?

- **Format broken?** Check that all quotes and commas are in place
- **Bot not working?** Contact Esteban
- **Want to add someone new?** We'll need to update the default rotation

## 🛠️ For Developers

See [docs/BOT.md](docs/BOT.md) for:
- How to create a Telegram bot
- Getting your chat ID
- Setting up GitHub Secrets
- Local development setup
- Testing and debugging

---

*Built with ❤️ for the padel group*