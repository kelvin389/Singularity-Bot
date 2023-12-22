const lib = require('lib')({token: process.env.STDLIB_SECRET_TOKEN});

await lib.discord.channels['@0.3.2'].messages.create({
  "channel_id": `${context.params.event.channel_id}`,
  "content": "",
  "tts": false,
  "components": [
    {
      "type": 1,
      "components": [
        {
          "style": 1,
          "label": `✅`,
          "custom_id": `row_0_button_0`,
          "disabled": false,
          "type": 2
        },
        {
          "style": 1,
          "label": `❌`,
          "custom_id": `row_0_button_1`,
          "disabled": false,
          "type": 2
        },
        {
          "style": 1,
          "label": `🤔`,
          "custom_id": `row_0_button_2`,
          "disabled": false,
          "type": 2
        }
      ]
    },
    {
      "type": 1,
      "components": [
        {
          "style": 1,
          "label": `Ping Everyone`,
          "custom_id": `row_2_button_0`,
          "disabled": false,
          "type": 2
        }
      ]
    }
  ],
  "embeds": [
    {
      "type": "rich",
      "title": `Counter-Strike 2 at 11:30pm`,
      "description": "",
      "color": 0x00FFFF,
      "fields": [
        {
          "name": `Participants`,
          "value": `👑@BenAstromo\n✅@kal\n❌@BigAI\n❔@JustSomeAsianBoy\n🤔@Machu - cant play until 1:00`,
          "inline": true
        }
      ],
      "footer": {
        "text": `!note [message] to leave a note`
      }
    }
  ]
});