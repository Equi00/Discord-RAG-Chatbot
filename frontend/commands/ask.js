const { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

const cache = require("../cache/cache")

module.exports = {
  data: new SlashCommandBuilder()
  .setName("ask")
  .setDescription("Ask a question to the RAG bot")
  .addStringOption(option =>
    option
    .setName("question")
    .setDescription("your question")
    .setRequired(true)
  ),

  async execute(interaction) {
    const question = interaction.options.getString("question")

    await interaction.deferReply()

    try{
      const response = await fetch(
        `http://localhost:8000/api/llm_response?query=${encodeURIComponent(question)}`
      )

      const row = new ActionRowBuilder()
          .addComponents(
            new ButtonBuilder()
              .setCustomId("feedback_up")
              .setLabel("👍")
              .setStyle(ButtonStyle.Success),
            new ButtonBuilder()
              .setCustomId("feedback_down")
              .setLabel("👎")
              .setStyle(ButtonStyle.Danger)
          )

      const data = await response.json()
      const message = await interaction.editReply({content: data.response, components: [row]})

      cache.set(message.id, {
        question,
        answer: data.response,
        context: data.context,
        date: new Date().toLocaleDateString("en-US"),
        type: data.type
      })
        
    } catch (error) {
        await interaction.editReply("Error: The bot cannot respond to the user query.")
    }
  },
}