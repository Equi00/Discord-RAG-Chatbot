const { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

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
      /*TODO: add RAG endpoint*/ 
        const response = "Generic message"

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

        const message = await interaction.editReply({content: response, components: [row]})
        
    } catch (error) {
        await interaction.editReply("Error: The bot cannot respond to the user query.")
    }
  },
}